"""
Punto de entrada: composición DI, capa de datos (MySQL o demo) y navegación por autenticación.
"""

import streamlit as st
from mysql.connector import Error

from services.container import ContenedorAplicacion, fabricar_contenedor
from ui.styles import apply_custom_theme


def _inicializar_capa_datos(contenedor: ContenedorAplicacion) -> None:
    """Intenta crear esquema y admin; si MySQL falla, activa datos demo en sesión."""
    if "use_demo_mode" not in st.session_state:
        st.session_state.use_demo_mode = False
    try:
        contenedor.bootstrap_repo.inicializar_esquema_base_datos()
        contenedor.bootstrap_repo.asegurar_usuario_admin_por_defecto()
        contenedor.audit.inicializar_almacen(usar_demo=False)
        st.session_state.use_demo_mode = False
    except Error:
        st.session_state.use_demo_mode = True
        contenedor.demo.inicializar_demostracion_si_ausente()
        contenedor.audit.inicializar_almacen(usar_demo=True)


def principal() -> None:
    """Configura la página, aplica estilos y muestra la vista según sesión y ruta."""
    st.set_page_config(
        page_title="Logistik BI Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    apply_custom_theme()

    if "_contenedor" not in st.session_state:
        st.session_state["_contenedor"] = fabricar_contenedor()
    contenedor = st.session_state["_contenedor"]

    contenedor.sesion.inicializar_claves_sesion()
    _inicializar_capa_datos(contenedor)

    if not contenedor.sesion.esta_autenticado():
        st.markdown(
            '<style>[data-testid="stSidebar"] { display: none !important; }</style>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<style>[data-testid="stSidebar"] { display: block !important; }</style>',
            unsafe_allow_html=True,
        )

    if contenedor.sesion.esta_autenticado():
        from ui.views.dashboard import mostrar_panel_principal

        mostrar_panel_principal()
        return

    if contenedor.sesion.obtener_navegacion_actual() == contenedor.sesion.NAV_LOGIN:
        from ui.views.login import mostrar_inicio_sesion

        mostrar_inicio_sesion()
        return

    from ui.views.landing import mostrar_pagina_inicio

    mostrar_pagina_inicio()


if __name__ == "__main__":
    principal()
