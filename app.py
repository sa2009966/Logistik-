"""
Punto de entrada: estilos globales, capa de datos (MySQL o demo) y navegación por autenticación.
"""

import streamlit as st
from mysql.connector import Error

from core import auth
from database import repository
from services import demo_data
from ui.styles import inyectar_estilos_globales


def _inicializar_capa_datos() -> None:
    """Intenta crear esquema y admin; si MySQL falla, activa datos demo en sesión."""
    if "use_demo_mode" not in st.session_state:
        st.session_state.use_demo_mode = False
    try:
        repository.inicializar_esquema_base_datos()
        repository.asegurar_usuario_admin_por_defecto()
        st.session_state.use_demo_mode = False
    except Error:
        st.session_state.use_demo_mode = True
        demo_data.inicializar_datos_demostracion()


def principal() -> None:
    """Configura la página, aplica estilos y muestra la vista según sesión y ruta."""
    st.set_page_config(
        page_title="Logistik BI Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inyectar_estilos_globales()
    auth.inicializar_claves_sesion()
    _inicializar_capa_datos()

    if not auth.esta_autenticado():
        st.markdown(
            '<style>[data-testid="stSidebar"] { display: none !important; }</style>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<style>[data-testid="stSidebar"] { display: block !important; }</style>',
            unsafe_allow_html=True,
        )

    if auth.esta_autenticado():
        from ui.views.dashboard import mostrar_panel_principal

        mostrar_panel_principal()
        return

    if st.session_state.get(auth.SESSION_NAV) == auth.NAV_LOGIN:
        from ui.views.login import mostrar_inicio_sesion

        mostrar_inicio_sesion()
        return

    from ui.views.landing import mostrar_pagina_inicio

    mostrar_pagina_inicio()


if __name__ == "__main__":
    principal()
