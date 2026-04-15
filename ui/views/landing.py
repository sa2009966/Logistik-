"""Página de bienvenida antes del login (Slate & Steel)."""

import streamlit as st

from services.container import obtener_contenedor
from ui.styles import COLOR_ACCENT, COLOR_TEXT_MUTED, envolver_contenedor_landing


def mostrar_pagina_inicio() -> None:
    """Renderiza la landing con CTA hacia el formulario de acceso."""
    contenedor = obtener_contenedor()
    contenido_html = f"""
    <div class="fade-in-up" style="text-align:center; max-width:920px; margin:0 auto;">
      <p style="font-size:0.8rem; letter-spacing:0.2em; text-transform:uppercase;
                color:{COLOR_TEXT_MUTED}; margin-bottom:1rem;">
        Logistik · Business Intelligence
      </p>
      <h1 style="font-size:clamp(1.75rem, 5vw, 2.75rem); font-weight:700; margin:0 0 1rem;
                 color:{COLOR_ACCENT}; line-height:1.2;">
        Inteligencia operativa para cadenas logísticas
      </h1>
      <p class="fade-in-delay" style="font-size:1.05rem; color:{COLOR_TEXT_MUTED}; line-height:1.65; max-width:720px; margin:0 auto 2rem;">
        Unifica transacciones, KPIs y reportes en un entorno seguro y orientado a datos.
      </p>
      <div class="fade-in-delay-2 ss-glass-panel" style="display:inline-block; padding:1.25rem 1.75rem; text-align:left; max-width:640px;">
        <p style="margin:0 0 0.5rem; color:{COLOR_ACCENT}; font-weight:600;">Qué resuelve</p>
        <ul style="margin:0; padding-left:1.2rem; color:#C9D1D9; line-height:1.75;">
          <li>Registro operativo de envíos y servicios</li>
          <li>Dashboard con filtros por fecha, estado y tipo de servicio</li>
          <li>Exportación CSV para reporting ejecutivo</li>
        </ul>
      </div>
    </div>
    """
    st.markdown(envolver_contenedor_landing(contenido_html), unsafe_allow_html=True)

    _, columna, _ = st.columns([1, 1, 1])
    with columna:
        if st.button("Acceder al sistema", type="primary", use_container_width=True):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LOGIN)
            st.rerun()
