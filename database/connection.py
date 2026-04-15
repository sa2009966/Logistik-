"""Conexión a MySQL con reintentos y comprobación de vida (ping); instancia inyectada desde la raíz."""

import logging
import threading
import time
from typing import TYPE_CHECKING, Optional

import mysql.connector
from mysql.connector import Error

if TYPE_CHECKING:
    from core.config import ConfiguracionAplicacion

logger = logging.getLogger(__name__)

_MAX_RETRIES = 4
_RETRY_DELAY_SEC = 1.5


class GestorConexionMySQL:
    """
    Mantiene una conexión con reconexión ante cortes.
    La configuración se inyecta (sin lectura global de entorno aquí).
    """

    def __init__(self, configuracion: "ConfiguracionAplicacion") -> None:
        self._config = configuracion
        self._conn = None
        self._lock = threading.Lock()

    def _construir_configuracion(self, base_datos: Optional[str] = None) -> dict:
        cfg = {
            "host": self._config.db_host,
            "port": self._config.db_port,
            "user": self._config.db_user,
            "password": self._config.db_password,
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
        with self._lock:
            if self._conn is None or not self._conn.is_connected():
                self.conectar_con_reintentos(self._config.db_name)
            else:
                try:
                    self._conn.ping(reconnect=True, attempts=3, delay=1)
                except Error:
                    logger.warning("Ping falló; reconectando.")
                    self.conectar_con_reintentos(self._config.db_name)
            return self._conn

    def reiniciar(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    if self._conn.is_connected():
                        self._conn.close()
                except Error:
                    pass
                self._conn = None
