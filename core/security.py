"""Funciones de cifrado de contraseñas con bcrypt (hash y verificación)."""

import bcrypt


def hashear_contrasena(contrasena: str) -> str:
    """Genera un hash seguro de la contraseña para almacenar en base de datos."""
    return bcrypt.hashpw(contrasena.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verificar_contrasena(contrasena: str, hash_almacenado: str) -> bool:
    """Comprueba si la contraseña en texto plano coincide con el hash guardado."""
    try:
        return bcrypt.checkpw(contrasena.encode("utf-8"), hash_almacenado.encode("utf-8"))
    except (ValueError, TypeError):
        return False
