"""Acceso a datos: creación de esquema, usuarios y transacciones logísticas."""

import logging
from datetime import date
from typing import Optional, Tuple

import mysql.connector
import pandas as pd
from mysql.connector import Error

from core import config
from core.constants import DB_TABLE_TRANSACTIONS, DB_TABLE_USERS
from core.security import hashear_contrasena
from database.connection import obtener_conexion, reiniciar_conexion

logger = logging.getLogger(__name__)


def _conexion_al_servidor():
    """Conexión sin base seleccionada (solo para CREATE DATABASE / DDL inicial)."""
    return mysql.connector.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        autocommit=True,
        connection_timeout=30,
    )


def inicializar_esquema_base_datos() -> None:
    """Crea la base de datos, la tabla de transacciones y la de usuarios si no existen."""
    conn = None
    cursor = None
    try:
        conn = _conexion_al_servidor()
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}`")
        cursor.execute(f"USE `{config.DB_NAME}`")

        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {DB_TABLE_TRANSACTIONS} (
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
            CREATE TABLE IF NOT EXISTS {DB_TABLE_USERS} (
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
    # Tras DDL fuera del singleton, se fuerza nueva conexión a la base ya creada
    reiniciar_conexion()


def asegurar_usuario_admin_por_defecto() -> None:
    """Si no hay fila para el admin por defecto, la inserta con contraseña hasheada."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT COUNT(*) FROM {DB_TABLE_USERS} WHERE nombre_usuario = %s",
            (config.DEFAULT_ADMIN_USERNAME,),
        )
        (count,) = cursor.fetchone()
        if count == 0:
            ph = hashear_contrasena(config.DEFAULT_ADMIN_PASSWORD)
            cursor.execute(
                f"""
                INSERT INTO {DB_TABLE_USERS} (nombre_usuario, password_hash)
                VALUES (%s, %s)
                """,
                (config.DEFAULT_ADMIN_USERNAME, ph),
            )
            conn.commit()
            logger.warning(
                "Usuario admin creado. Cambie DEFAULT_ADMIN_PASSWORD en .env en producción."
            )
    finally:
        cursor.close()


def obtener_usuario_por_nombre(nombre_usuario: str) -> Optional[Tuple[int, str, str]]:
    """Devuelve (id, nombre, hash) o None si no existe."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            SELECT id_usuario, nombre_usuario, password_hash
            FROM {DB_TABLE_USERS}
            WHERE nombre_usuario = %s
            """,
            (nombre_usuario.strip(),),
        )
        fila = cursor.fetchone()
        return fila if fila else None
    finally:
        cursor.close()


def crear_usuario(nombre_usuario: str, contrasena_texto: str) -> bool:
    """
    Inserta un usuario nuevo.
    Retorna False si el nombre ya está en uso.
    """
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"SELECT 1 FROM {DB_TABLE_USERS} WHERE nombre_usuario = %s",
            (nombre_usuario.strip(),),
        )
        if cursor.fetchone():
            return False
        cursor.execute(
            f"""
            INSERT INTO {DB_TABLE_USERS} (nombre_usuario, password_hash)
            VALUES (%s, %s)
            """,
            (nombre_usuario.strip(), hashear_contrasena(contrasena_texto)),
        )
        conn.commit()
        return True
    except Error:
        conn.rollback()
        raise
    finally:
        cursor.close()


def insertar_transaccion(
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
    """Alta de una fila en transacciones_logistik."""
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"""
            INSERT INTO {DB_TABLE_TRANSACTIONS}
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


def cargar_transacciones_dataframe() -> pd.DataFrame:
    """Lee todas las transacciones ordenadas para el dashboard."""
    conn = obtener_conexion()
    consulta = f"""
        SELECT id_transaccion, fecha, cliente, tipo_servicio, descripcion, origen, destino,
               monto_total, estado, metodo_pago, usuario_registro, fecha_registro
        FROM {DB_TABLE_TRANSACTIONS}
        ORDER BY fecha ASC, id_transaccion ASC
    """
    return pd.read_sql(consulta, conn)
