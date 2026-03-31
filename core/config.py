"""Carga de variables de entorno (.env) y valores por defecto de la aplicación."""

import os
from pathlib import Path

# Ruta al .env en la raíz del proyecto (junto a app.py)
_env_path = Path(__file__).resolve().parent.parent / ".env"
try:
    from dotenv import load_dotenv

    load_dotenv(_env_path)
except ImportError:
    # python-dotenv opcional: se usan solo variables de entorno del sistema
    pass

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "1234")
DB_NAME = os.getenv("DB_NAME", "db_bi_alex")

DEFAULT_ADMIN_USERNAME = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "ChangeMeSecure!2026")

# Permite registro desde la pantalla de login (desactivar en entornos cerrados)
ALLOW_SELF_REGISTRATION = os.getenv("ALLOW_SELF_REGISTRATION", "true").lower() in (
    "1",
    "true",
    "yes",
)
