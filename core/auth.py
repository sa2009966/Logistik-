"""Control de claves y banderas de sesión en Streamlit (sin acceso a base de datos)."""

import streamlit as st


class AuthSessionController:
    """
    Gestiona únicamente el estado de sesión y navegación en `st.session_state`.
    La validación de credenciales vive en la capa services (AuthService).
    """

    SESSION_USER = "auth_username"
    SESSION_USER_ID = "auth_user_id"
    SESSION_AUTH = "authenticated"
    SESSION_NAV = "nav_view"
    NAV_LANDING = "landing"
    NAV_LOGIN = "login"

    def inicializar_claves_sesion(self) -> None:
        """Asegura banderas de autenticación y navegación antes de renderizar."""
        if self.SESSION_AUTH not in st.session_state:
            st.session_state[self.SESSION_AUTH] = False
        if self.SESSION_NAV not in st.session_state:
            st.session_state[self.SESSION_NAV] = self.NAV_LANDING

    def esta_autenticado(self) -> bool:
        return bool(st.session_state.get(self.SESSION_AUTH))

    def obtener_usuario_actual(self) -> str:
        return str(st.session_state.get(self.SESSION_USER, ""))

    def establecer_sesion_autenticada(self, nombre_usuario: str, id_usuario: int) -> None:
        st.session_state[self.SESSION_AUTH] = True
        st.session_state[self.SESSION_USER] = nombre_usuario
        st.session_state[self.SESSION_USER_ID] = id_usuario

    def cerrar_sesion(self) -> None:
        st.session_state[self.SESSION_AUTH] = False
        for k in (self.SESSION_USER, self.SESSION_USER_ID):
            if k in st.session_state:
                del st.session_state[k]
        st.session_state[self.SESSION_NAV] = self.NAV_LANDING

    def establecer_navegacion(self, vista: str) -> None:
        st.session_state[self.SESSION_NAV] = vista

    def obtener_navegacion_actual(self) -> str:
        return str(st.session_state.get(self.SESSION_NAV, self.NAV_LANDING))
