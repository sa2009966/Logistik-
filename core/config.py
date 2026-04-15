"""Carga de variables de entorno (.env) y valores por defecto de la aplicación."""

import os
from pathlib import Path

_env_path = Path(__file__).resolve().parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(_env_path)
except ImportError:
    pass


class ConfiguracionAplicacion:
    """Parámetros globales de entorno; instanciada en la composición raíz (app / contenedor)."""

    def __init__(self) -> None:
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = int(os.getenv("DB_PORT", "3306"))
        self.db_user = os.getenv("DB_USER", "root")
        self.db_password = os.getenv("DB_PASSWORD", "1234")
        self.db_name = os.getenv("DB_NAME", "db_bi_alex")
        self.default_admin_username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        self.default_admin_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMeSecure!2026")
        self.allow_self_registration = os.getenv("ALLOW_SELF_REGISTRATION", "true").lower() in (
            "1",
            "true",
            "yes",
        )
