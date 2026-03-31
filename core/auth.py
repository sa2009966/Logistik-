"""Gestión de sesión en Streamlit: login, logout y registro contra el repositorio."""

from typing import Tuple

import streamlit as st

from core import config
from core.security import verificar_contrasena
from database import repository

# Claves de session_state (evitar literales repetidos en vistas)
SESSION_USER = "auth_username"
SESSION_USER_ID = "auth_user_id"
SESSION_AUTH = "authenticated"
SESSION_NAV = "nav_view"
NAV_LANDING = "landing"
NAV_LOGIN = "login"


def inicializar_claves_sesion() -> None:
    """Asegura que existan banderas de autenticación y navegación antes de renderizar."""
    if SESSION_AUTH not in st.session_state:
        st.session_state[SESSION_AUTH] = False
    if SESSION_NAV not in st.session_state:
        st.session_state[SESSION_NAV] = NAV_LANDING


def esta_autenticado() -> bool:
    """Indica si el usuario ya pasó el login en esta sesión."""
    return bool(st.session_state.get(SESSION_AUTH))


def obtener_usuario_actual() -> str:
    """Nombre de usuario de la sesión activa (cadena vacía si no hay sesión)."""
    return str(st.session_state.get(SESSION_USER, ""))


def iniciar_sesion(
    nombre_usuario: str, contrasena: str, modo_demostracion: bool = False
) -> Tuple[bool, str]:
    """
    Valida credenciales contra MySQL o, en modo demo, contra usuario fijo.
    Devuelve (éxito, mensaje de error vacío si todo va bien).
    """
    u = nombre_usuario.strip()
    if not u or not contrasena:
        return False, "Usuario y contraseña son obligatorios."
    if modo_demostracion:
        if u == "admin" and contrasena == "demo123":
            st.session_state[SESSION_AUTH] = True
            st.session_state[SESSION_USER] = u
            st.session_state[SESSION_USER_ID] = 0
            return True, ""
        return False, "Credenciales inválidas (modo demo: admin / demo123)."
    fila = repository.obtener_usuario_por_nombre(u)
    if not fila:
        return False, "Usuario o contraseña incorrectos."
    _uid, _name, pwd_hash = fila
    if not verificar_contrasena(contrasena, pwd_hash):
        return False, "Usuario o contraseña incorrectos."
    st.session_state[SESSION_AUTH] = True
    st.session_state[SESSION_USER] = u
    st.session_state[SESSION_USER_ID] = int(_uid)
    return True, ""


def cerrar_sesion() -> None:
    """Limpia la sesión y vuelve la navegación a la pantalla de inicio."""
    st.session_state[SESSION_AUTH] = False
    for k in (SESSION_USER, SESSION_USER_ID):
        if k in st.session_state:
            del st.session_state[k]
    st.session_state[SESSION_NAV] = NAV_LANDING


def registrar_usuario(
    nombre_usuario: str,
    contrasena: str,
    confirmacion: str,
    modo_demostracion: bool = False,
) -> Tuple[bool, str]:
    """Crea un usuario nuevo si la política de registro lo permite."""
    if modo_demostracion:
        return False, "El registro no está disponible en modo demo (sin MySQL)."
    if not config.ALLOW_SELF_REGISTRATION:
        return False, "El registro público está deshabilitado."
    u = nombre_usuario.strip()
    if len(u) < 3:
        return False, "El usuario debe tener al menos 3 caracteres."
    if len(contrasena) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres."
    if contrasena != confirmacion:
        return False, "Las contraseñas no coinciden."
    try:
        ok = repository.crear_usuario(u, contrasena)
        if not ok:
            return False, "Ese nombre de usuario ya está registrado."
        return True, "Cuenta creada. Ya puede iniciar sesión."
    except Exception as e:
        return False, f"No se pudo registrar: {e}"
