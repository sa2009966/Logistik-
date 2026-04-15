"""Página de bienvenida antes del login (mensaje de valor y CTA)."""

import streamlit as st

from services.container import obtener_contenedor
from ui.styles import CYBER_CYAN, CYBER_GREEN, TemaInterfaz


def mostrar_pagina_inicio() -> None:
    """Renderiza la landing con animaciones CSS y botón hacia el formulario de acceso."""
    contenedor = obtener_contenedor()
    tema = TemaInterfaz()
    contenido_html = f"""
    <div class="fade-in-up" style="text-align:center; max-width:920px; margin:0 auto;">
      <p style="font-family:'JetBrains Mono',monospace; font-size:0.85rem; letter-spacing:0.35em;
                color:{CYBER_CYAN}; margin-bottom:1rem; opacity:0.95;">
        LOGISTIK · BUSINESS INTELLIGENCE
      </p>
      <h1 class="elite-glow" style="font-size:clamp(2.2rem, 5vw, 3.4rem); font-weight:700; margin:0 0 1rem;
                                      background:linear-gradient(90deg,{CYBER_CYAN},{CYBER_GREEN});
                                      -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                                      background-clip:text;">
        Inteligencia operativa para cadenas logísticas de alto rendimiento
      </h1>
      <p class="fade-in-delay" style="font-size:1.15rem; color:#b8c5d9; line-height:1.7; max-width:720px; margin:0 auto 2rem;">
        Visualiza ingresos, estados y servicios en un panel oscuro tipo comando.
        Unifica transacciones, KPIs y reportes en un solo entorno seguro.
      </p>
      <div class="fade-in-delay-2 glass-panel" style="display:inline-block; padding:1.25rem 1.75rem; text-align:left; max-width:640px;">
        <p style="margin:0 0 0.5rem; color:{CYBER_GREEN}; font-weight:600;">¿Qué resuelve?</p>
        <ul style="margin:0; padding-left:1.2rem; color:#c9d6ea; line-height:1.8;">
          <li>Registro operativo de envíos y servicios</li>
          <li>Dashboard con filtros por fecha, estado y tipo de servicio</li>
          <li>Exportación CSV para reporting ejecutivo</li>
        </ul>
      </div>
    </div>
    """
    st.markdown(tema.envolver_contenedor_landing(contenido_html), unsafe_allow_html=True)

    _, columna, _ = st.columns([1, 1, 1])
    with columna:
        if st.button("Acceder al sistema", type="primary", use_container_width=True):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LOGIN)
            st.rerun()
