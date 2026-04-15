"""Formulario de inicio de sesión y registro opcional (Slate & Steel)."""

import inspect
from typing import Any

import streamlit as st

from services.container import obtener_contenedor
from ui.styles import COLOR_ACCENT, COLOR_TEXT_MUTED


def _st_form(name: str, **kwargs: Any) -> Any:
    """
    Abre st.form ocultando la ayuda "Press Enter to submit" si el runtime lo permite
    (parámetro enter_to_submit desde Streamlit reciente).
    """
    sig = inspect.signature(st.form)
    if "enter_to_submit" in sig.parameters:
        return st.form(name, enter_to_submit=False, **kwargs)
    return st.form(name, **kwargs)


def mostrar_inicio_sesion() -> None:
    """Pantalla de credenciales; en modo demo muestra usuario/contraseña de prueba."""
    contenedor = obtener_contenedor()
    st.markdown(
        f"""
        <div style="text-align:center; margin-bottom:1.75rem;" class="fade-in-up">
          <h2 style="color:{COLOR_ACCENT}; font-weight:700; margin:0 0 0.5rem 0;">Acceso corporativo</h2>
          <p style="color:{COLOR_TEXT_MUTED}; font-size:0.95rem; margin:0;">Autenticación obligatoria · contraseñas con bcrypt</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    modo_demo = st.session_state.get("use_demo_mode", False)
    if modo_demo:
        st.info("Modo demo activo (sin MySQL). Use **admin** / **demo123**.")

    _, col_login, _ = st.columns([1, 5, 1])
    with col_login:
        with _st_form("login_form"):
            usuario = st.text_input("Usuario")
            contrasena = st.text_input("Contraseña", type="password")
            enviado = st.form_submit_button("Ingresar", type="primary", use_container_width=True)

        if enviado:
            exito, mensaje = contenedor.auth.iniciar_sesion(
                usuario, contrasena, modo_demostracion=modo_demo
            )
            if exito:
                st.success("Sesión iniciada.")
                st.rerun()
            else:
                st.error(mensaje)

        st.markdown(
            '<div class="ss-login-nav-spacer" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )
        if st.button("← Volver al inicio", type="secondary", use_container_width=True):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LANDING)
            st.rerun()

    if contenedor.configuracion.allow_self_registration:
        st.divider()
        st.markdown(
            f"""
            <div style="text-align:center; margin: 1.5rem 0 1rem 0;">
              <h3 style="color:{COLOR_ACCENT}; font-weight:600; margin:0 0 0.35rem 0;">Registrarse</h3>
              <p style="color:{COLOR_TEXT_MUTED}; font-size:0.9rem; margin:0;">Crea una cuenta nueva. Luego podrás iniciar sesión con esas credenciales.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        _, col_reg, _ = st.columns([1, 5, 1])
        with col_reg:
            with _st_form("register_form"):
                nuevo_usuario = st.text_input("Nuevo usuario", key="reg_user")
                clave = st.text_input("Contraseña", type="password", key="reg_np")
                clave_confirm = st.text_input("Confirmar contraseña", type="password", key="reg_nc")
                registrar = st.form_submit_button("Crear cuenta", type="primary", use_container_width=True)
            if registrar:
                ok, msg = contenedor.auth.registrar_usuario(
                    nuevo_usuario, clave, clave_confirm, modo_demostracion=modo_demo
                )
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
