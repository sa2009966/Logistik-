"""Página de bienvenida antes del login (Slate & Steel)."""

import streamlit as st

from services.container import obtener_contenedor
from ui.styles import COLOR_ACCENT, COLOR_TEXT_MUTED, envolver_contenedor_landing


def mostrar_pagina_inicio() -> None:
    """Renderiza la landing con valor de producto y CTA hacia el acceso."""
    contenedor = obtener_contenedor()
    contenido_html = f"""
    <div class="fade-in-up" style="text-align:center; max-width:920px; margin:0 auto;">
      <p style="font-size:0.8rem; letter-spacing:0.2em; text-transform:uppercase;
                color:{COLOR_TEXT_MUTED}; margin-bottom:1rem;">
        Logistik BI · Slate &amp; Steel
      </p>
      <h1 style="font-size:clamp(1.75rem, 5vw, 2.75rem); font-weight:700; margin:0 0 1rem;
                 color:{COLOR_ACCENT}; line-height:1.2;">
        Panel de inteligencia para operaciones logísticas
      </h1>
      <p class="fade-in-delay" style="font-size:1.05rem; color:{COLOR_TEXT_MUTED}; line-height:1.65; max-width:760px; margin:0 auto 2rem;">
        Centraliza transacciones, indicadores y reportes en un solo entorno profesional.
        Conéctate a <strong style="color:#C9D1D9;">MySQL</strong> o trabaja en
        <strong style="color:#C9D1D9;">modo demo</strong> sin servidor: mismas herramientas, datos de ejemplo.
      </p>
      <div class="fade-in-delay-2 ss-glass-panel" style="display:inline-block; padding:1.25rem 1.75rem; text-align:left; max-width:680px;">
        <p style="margin:0 0 0.65rem; color:{COLOR_ACCENT}; font-weight:600;">Incluye</p>
        <ul style="margin:0; padding-left:1.2rem; color:#C9D1D9; line-height:1.8;">
          <li><strong>Dashboard BI</strong> con filtros por fecha, estado y tipo de servicio</li>
          <li><strong>Alertas de KPIs</strong> según umbrales de ingresos, volumen y ticket medio</li>
          <li><strong>Exportación</strong> de reportes en CSV y Excel (.xlsx)</li>
          <li><strong>Auditoría</strong> de acciones relevantes (acceso, transacciones, exportaciones)</li>
          <li><strong>Acceso seguro</strong> con contraseñas protegidas por bcrypt</li>
        </ul>
      </div>
      <p class="fade-in-delay-2" style="margin-top:1.5rem; font-size:0.88rem; color:{COLOR_TEXT_MUTED}; max-width:640px; margin-left:auto; margin-right:auto;">
        Interfaz responsive, paleta Slate &amp; Steel e indicadores listos para decisiones ejecutivas.
      </p>
    </div>
    """
    st.markdown(envolver_contenedor_landing(contenido_html), unsafe_allow_html=True)

    _, columna, _ = st.columns([1, 1, 1])
    with columna:
        if st.button("Acceder al sistema", type="primary", use_container_width=True):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LOGIN)
            st.rerun()
