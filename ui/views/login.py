"""Formulario de inicio de sesión y registro opcional (glassmorphism vía ui/styles)."""

import streamlit as st

from core import auth, config
from ui.styles import CYBER_CYAN


def mostrar_inicio_sesion() -> None:
    """Pantalla de credenciales; en modo demo muestra usuario/contraseña de prueba."""
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:1.5rem;" class="fade-in-up">
          <h2 style="color:{CYBER_CYAN}; font-weight:700; margin-bottom:0.35rem;">Acceso corporativo</h2>
          <p style="color:#9ab0c8; font-size:0.95rem;">Autenticación obligatoria · contraseñas con bcrypt</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    modo_demo = st.session_state.get("use_demo_mode", False)
    if modo_demo:
        st.info("Modo demo activo (sin MySQL). Use **admin** / **demo123**.")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        enviado = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

    if enviado:
        exito, mensaje = auth.iniciar_sesion(usuario, contrasena, modo_demostracion=modo_demo)
        if exito:
            st.success("Sesión iniciada.")
            st.rerun()
        else:
            st.error(mensaje)

    col_volver, _ = st.columns(2)
    with col_volver:
        if st.button("← Volver al inicio", use_container_width=True):
            st.session_state[auth.SESSION_NAV] = auth.NAV_LANDING
            st.rerun()

    if config.ALLOW_SELF_REGISTRATION:
        with st.expander("Crear cuenta (registro)", expanded=False):
            st.caption("Formulario con estilo cristal definido en `ui/styles.py`.")
            with st.form("register_form"):
                nuevo_usuario = st.text_input("Nuevo usuario")
                clave = st.text_input("Contraseña", type="password", key="np")
                clave_confirm = st.text_input("Confirmar contraseña", type="password", key="nc")
                registrar = st.form_submit_button("Registrar", use_container_width=True)
            if registrar:
                ok, msg = auth.registrar_usuario(
                    nuevo_usuario, clave, clave_confirm, modo_demostracion=modo_demo
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
