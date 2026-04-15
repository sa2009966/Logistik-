"""Acceso a datos: esquema, usuarios y transacciones logísticas (POO + DI)."""

import logging
from datetime import date
from typing import TYPE_CHECKING, Optional, Tuple

import mysql.connector
import pandas as pd
from mysql.connector import Error

from core.constants import ConstantesNegocio
from services.contracts import IAuthRepository, IBootstrapRepository, ITransaccionesDataSource

if TYPE_CHECKING:
    from core.config import ConfiguracionAplicacion
    from core.security import SecurityHandler
    from database.connection import GestorConexionMySQL

logger = logging.getLogger(__name__)


class LogistikRepository(IAuthRepository, IBootstrapRepository, ITransaccionesDataSource):
    """
    Repositorio SQL: recibe el gestor de conexión y el manejador de seguridad por constructor.
    No instancia dependencias internamente.
    """

    def __init__(
        self,
        gestor_mysql: "GestorConexionMySQL",
        security_handler: "SecurityHandler",
        configuracion: "ConfiguracionAplicacion",
    ) -> None:
        self._gestor = gestor_mysql
        self._security = security_handler
        self._config = configuracion

    def _conexion_al_servidor(self):
        return mysql.connector.connect(
            host=self._config.db_host,
            port=self._config.db_port,
            user=self._config.db_user,
            password=self._config.db_password,
            autocommit=True,
            connection_timeout=30,
        )

    def inicializar_esquema_base_datos(self) -> None:
        conn = None
        cursor = None
        tbl_tx = ConstantesNegocio.DB_TABLE_TRANSACTIONS
        tbl_users = ConstantesNegocio.DB_TABLE_USERS
        try:
            conn = self._conexion_al_servidor()
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self._config.db_name}`")
            cursor.execute(f"USE `{self._config.db_name}`")

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {tbl_tx} (
                    id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
                    fecha DATE NOT NULL,
                    cliente VARCHAR(100) NOT NULL,
                    tipo_servicio VARCHAR(100) NOT NULL,
                    descripcion VARCHAR(255) NOT NULL,
                    origen VARCHAR(100) NOT NULL,
                    destino VARCHAR(100) NOT NULL,
                    monto_total DECIMAL(10, 2) NOT NULL,
                    estado VARCHAR(50) NOT NULL,
                    metodo_pago VARCHAR(50) NOT NULL,
                    usuario_registro VARCHAR(50) NOT NULL,
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {tbl_users} (
                    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
                    nombre_usuario VARCHAR(64) NOT NULL UNIQUE,
                    password_hash VARCHAR(255) NOT NULL,
                    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None and conn.is_connected():
                conn.close()
        self._gestor.reiniciar()

    def asegurar_usuario_admin_por_defecto(self) -> None:
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        tbl_users = ConstantesNegocio.DB_TABLE_USERS
        try:
            cursor.execute(
                f"SELECT COUNT(*) FROM {tbl_users} WHERE nombre_usuario = %s",
                (self._config.default_admin_username,),
            )
            (count,) = cursor.fetchone()
            if count == 0:
                ph = self._security.hashear_contrasena(self._config.default_admin_password)
                cursor.execute(
                    f"""
                    INSERT INTO {tbl_users} (nombre_usuario, password_hash)
                    VALUES (%s, %s)
                    """,
                    (self._config.default_admin_username, ph),
                )
                conn.commit()
                logger.warning(
                    "Usuario admin creado. Cambie default_admin_password en .env en producción."
                )
        finally:
            cursor.close()

    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Tuple[int, str, str]]:
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        tbl_users = ConstantesNegocio.DB_TABLE_USERS
        try:
            cursor.execute(
                f"""
                SELECT id_usuario, nombre_usuario, password_hash
                FROM {tbl_users}
                WHERE nombre_usuario = %s
                """,
                (nombre_usuario.strip(),),
            )
            fila = cursor.fetchone()
            return fila if fila else None
        finally:
            cursor.close()

    def crear_usuario(self, nombre_usuario: str, contrasena_texto: str) -> bool:
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        tbl_users = ConstantesNegocio.DB_TABLE_USERS
        try:
            cursor.execute(
                f"SELECT 1 FROM {tbl_users} WHERE nombre_usuario = %s",
                (nombre_usuario.strip(),),
            )
            if cursor.fetchone():
                return False
            cursor.execute(
                f"""
                INSERT INTO {tbl_users} (nombre_usuario, password_hash)
                VALUES (%s, %s)
                """,
                (
                    nombre_usuario.strip(),
                    self._security.hashear_contrasena(contrasena_texto),
                ),
            )
            conn.commit()
            return True
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def insertar_transaccion(
        self,
        fecha: date,
        cliente: str,
        tipo_servicio: str,
        descripcion: str,
        origen: str,
        destino: str,
        monto_total: float,
        estado: str,
        metodo_pago: str,
        usuario_registro: str,
    ) -> None:
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        tbl_tx = ConstantesNegocio.DB_TABLE_TRANSACTIONS
        try:
            cursor.execute(
                f"""
                INSERT INTO {tbl_tx}
                (fecha, cliente, tipo_servicio, descripcion, origen, destino,
                 monto_total, estado, metodo_pago, usuario_registro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    fecha,
                    cliente,
                    tipo_servicio,
                    descripcion,
                    origen,
                    destino,
                    monto_total,
                    estado,
                    metodo_pago,
                    usuario_registro,
                ),
            )
            conn.commit()
        except Error:
            conn.rollback()
            raise
        finally:
            cursor.close()

    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        conn = self._gestor.obtener()
        tbl_tx = ConstantesNegocio.DB_TABLE_TRANSACTIONS
        consulta = f"""
            SELECT id_transaccion, fecha, cliente, tipo_servicio, descripcion, origen, destino,
                   monto_total, estado, metodo_pago, usuario_registro, fecha_registro
            FROM {tbl_tx}
            ORDER BY fecha ASC, id_transaccion ASC
        """
        return pd.read_sql(consulta, conn)
