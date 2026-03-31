"""Conexión singleton a MySQL con reintentos y comprobación de vida (ping)."""

import logging
import threading
import time
from typing import Optional

import mysql.connector
from mysql.connector import Error

from core import config

logger = logging.getLogger(__name__)

_MAX_RETRIES = 4
_RETRY_DELAY_SEC = 1.5


class GestorConexionMySQL:
    """
    Patrón singleton: una sola conexión compartida y reconexión ante cortes.
    """

    _instance: Optional["GestorConexionMySQL"] = None
    _lock = threading.Lock()
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def _construir_configuracion(self, base_datos: Optional[str] = None) -> dict:
        """Parámetros para mysql.connector según core.config."""
        cfg = {
            "host": config.DB_HOST,
            "port": config.DB_PORT,
            "user": config.DB_USER,
            "password": config.DB_PASSWORD,
            "autocommit": False,
            "connection_timeout": 30,
            "pool_reset_session": True,
        }
        if base_datos:
            cfg["database"] = base_datos
        return cfg

    def _conectar_una_vez(self, base_datos: Optional[str] = None) -> None:
        self._conn = mysql.connector.connect(**self._construir_configuracion(base_datos))

    def conectar_con_reintentos(self, base_datos: Optional[str] = None) -> None:
        """Intenta abrir conexión varias veces antes de propagar el error."""
        last_err: Optional[Exception] = None
        for intento in range(1, _MAX_RETRIES + 1):
            try:
                self._conectar_una_vez(base_datos)
                logger.info("Conexión MySQL establecida (intento %s).", intento)
                return
            except Error as e:
                last_err = e
                logger.warning("Fallo conexión MySQL intento %s: %s", intento, e)
                time.sleep(_RETRY_DELAY_SEC * intento)
        raise last_err  # type: ignore[misc]

    def obtener(self):
        """Devuelve conexión viva; reconecta si hace falta."""
        if self._conn is None or not self._conn.is_connected():
            self.conectar_con_reintentos(config.DB_NAME)
        else:
            try:
                self._conn.ping(reconnect=True, attempts=3, delay=1)
            except Error:
                logger.warning("Ping falló; reconectando.")
                self.conectar_con_reintentos(config.DB_NAME)
        return self._conn

    def reiniciar(self) -> None:
        """Cierra la conexión interna (útil tras DDL o pruebas)."""
        if self._conn is not None:
            try:
                if self._conn.is_connected():
                    self._conn.close()
            except Error:
                pass
            self._conn = None


_gestor = GestorConexionMySQL()


def obtener_conexion():
    """Punto de uso habitual: conexión a la base configurada en DB_NAME."""
    return _gestor.obtener()


def reiniciar_conexion():
    """Invalida el singleton para forzar un nuevo handshake con MySQL."""
    _gestor.reiniciar()
