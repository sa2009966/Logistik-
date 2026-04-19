"""Página de bienvenida renovada — hero, feature grid, stats y CTA."""

import streamlit as st

from services.container import obtener_contenedor
from ui.styles import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_BORDER,
    COLOR_CARD,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    envolver_contenedor_landing,
)

# ── Paleta auxiliar para los iconos de feature cards ──────────────────────────
_ICON_BG = "rgba(96, 165, 250, 0.10)"
_ICON_BORDER = "rgba(96, 165, 250, 0.22)"

# ── Datos de la cuadrícula de características ─────────────────────────────────
_FEATURES = [
    {
        "icon": "📊",
        "titulo": "BI Dinámico",
        "desc": (
            "Filtros por fecha, estado y tipo de servicio enviados directo a la capa de datos. "
            "En MySQL se traduce a SQL con <code>WHERE</code>; en modo demo filtra en memoria."
        ),
    },
    {
        "icon": "👥",
        "titulo": "Admin de usuarios",
        "desc": (
            "CRUD completo de cuentas con asignación de roles "
            "<em>admin · analista · operador</em>. "
            "Panel exclusivo para administradores, invisible para otros roles."
        ),
    },
    {
        "icon": "🗂️",
        "titulo": "CSV Mapper dinámico",
        "desc": (
            "Carga cualquier CSV aunque sus columnas no coincidan con el esquema. "
            "El sistema detecta las diferencias y te guía para mapear los campos visualmente."
        ),
    },
    {
        "icon": "🛡️",
        "titulo": "Seguridad bcrypt",
        "desc": (
            "Contraseñas hasheadas con <code>bcrypt</code> + salt automático. "
            "Auditoría de login, registros y exportaciones con timestamp UTC."
        ),
    },
    {
        "icon": "📤",
        "titulo": "Exportación inteligente",
        "desc": (
            "Reportes descargables en <strong>CSV</strong> y <strong>Excel .xlsx</strong> "
            "sobre los datos filtrados activos, con registro de descarga en auditoría."
        ),
    },
    {
        "icon": "🔌",
        "titulo": "Modo demo offline",
        "desc": (
            "Sin MySQL disponible el sistema activa datos de ejemplo en memoria. "
            "Mismas herramientas, misma UX: cero configuración para evaluar el producto."
        ),
    },
]

# ── Stats rápidos ──────────────────────────────────────────────────────────────
_STATS = [
    {"valor": "6", "etiqueta": "Módulos funcionales"},
    {"valor": "3", "etiqueta": "Roles de usuario"},
    {"valor": "2", "etiqueta": "Fuentes de datos"},
    {"valor": "100 %", "etiqueta": "Principios SOLID"},
]


# ── Helpers HTML ───────────────────────────────────────────────────────────────

def _html_badge(texto: str) -> str:
    return (
        f'<span style="display:inline-block; padding:0.25rem 0.85rem; '
        f'background:{_ICON_BG}; border:1px solid {_ICON_BORDER}; '
        f'border-radius:999px; font-size:0.75rem; font-weight:600; '
        f'letter-spacing:0.08em; text-transform:uppercase; color:{COLOR_ACCENT}; '
        f'margin-bottom:1.25rem;">{texto}</span>'
    )


def _html_feature_card(icon: str, titulo: str, desc: str) -> str:
    return f"""
    <div class="ss-glass-panel fade-in-delay" style="
        padding:1.4rem 1.5rem;
        height:100%;
        display:flex;
        flex-direction:column;
        gap:0.75rem;
    ">
      <div style="
          width:2.6rem; height:2.6rem;
          background:{_ICON_BG};
          border:1px solid {_ICON_BORDER};
          border-radius:10px;
          display:flex; align-items:center; justify-content:center;
          font-size:1.25rem; flex-shrink:0;
      ">{icon}</div>
      <p style="margin:0; font-weight:600; font-size:0.97rem; color:{COLOR_TEXT};">{titulo}</p>
      <p style="margin:0; font-size:0.86rem; color:{COLOR_TEXT_MUTED}; line-height:1.6;">{desc}</p>
    </div>
    """


def _html_stat(valor: str, etiqueta: str) -> str:
    return f"""
    <div style="text-align:center; padding:1rem 0.5rem;">
      <p style="margin:0; font-size:1.8rem; font-weight:700; color:{COLOR_ACCENT};
                letter-spacing:-0.02em; line-height:1;">{valor}</p>
      <p style="margin:0.35rem 0 0; font-size:0.78rem; color:{COLOR_TEXT_MUTED};
                text-transform:uppercase; letter-spacing:0.08em;">{etiqueta}</p>
    </div>
    """


def _html_divider() -> str:
    return f'<hr style="border:none; border-top:1px solid {COLOR_BORDER}; margin:0.25rem 0;" />'


# ── Vista principal ────────────────────────────────────────────────────────────

def mostrar_pagina_inicio() -> None:
    """Renderiza la landing renovada con hero, feature grid, stats y CTA."""
    contenedor = obtener_contenedor()

    # ── Hero ──────────────────────────────────────────────────────────────────
    hero_html = f"""
    <div class="fade-in-up" style="text-align:center; max-width:860px; margin:0 auto 2.5rem;">
      {_html_badge("Logistik BI · v2 · Slate &amp; Steel")}
      <h1 style="
          font-size:clamp(1.9rem, 5.5vw, 3rem);
          font-weight:700;
          line-height:1.15;
          letter-spacing:-0.03em;
          color:{COLOR_TEXT};
          margin:0 0 1.1rem;
      ">
        Inteligencia operativa para<br>
        <span style="color:{COLOR_ACCENT};">logística moderna</span>
      </h1>
      <p style="
          font-size:1.05rem;
          color:{COLOR_TEXT_MUTED};
          line-height:1.7;
          max-width:640px;
          margin:0 auto 2rem;
      ">
        Dashboard BI con filtros en tiempo real, gestión de usuarios por roles,
        mapper dinámico de CSV y modo demo sin servidor.
        Arquitectura <strong style="color:{COLOR_TEXT};">100&nbsp;% SOLID</strong>,
        lista para producción.
      </p>
    </div>
    """
    st.markdown(envolver_contenedor_landing(hero_html), unsafe_allow_html=True)

    # ── CTA principal ────────────────────────────────────────────────────────
    _, col_cta, _ = st.columns([1.2, 1, 1.2])
    with col_cta:
        if st.button(
            "Acceder al sistema →",
            type="primary",
            use_container_width=True,
            key="landing_cta_top",
        ):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LOGIN)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Separador con label ───────────────────────────────────────────────────
    st.markdown(
        f'<p style="text-align:center; font-size:0.75rem; letter-spacing:0.12em; '
        f'text-transform:uppercase; color:{COLOR_TEXT_MUTED}; margin:1.5rem 0 1.25rem;">'
        f'Funcionalidades incluidas</p>',
        unsafe_allow_html=True,
    )

    # ── Feature grid — 3 columnas × 2 filas ──────────────────────────────────
    fila1 = st.columns(3, gap="medium")
    fila2 = st.columns(3, gap="medium")
    filas = fila1 + fila2

    for col, feat in zip(filas, _FEATURES):
        with col:
            st.markdown(
                _html_feature_card(feat["icon"], feat["titulo"], feat["desc"]),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Stats bar ─────────────────────────────────────────────────────────────
    stats_inner = "".join(_html_stat(s["valor"], s["etiqueta"]) for s in _STATS)
    stats_cols_html = "".join(
        f'<div style="flex:1; min-width:120px;">{_html_stat(s["valor"], s["etiqueta"])}</div>'
        for s in _STATS
    )
    stats_html = f"""
    <div class="ss-glass-panel fade-in-delay-2" style="
        padding:1.25rem 2rem;
        display:flex;
        flex-wrap:wrap;
        justify-content:space-around;
        align-items:center;
        gap:0.5rem 1rem;
        max-width:820px;
        margin:0 auto;
    ">
      {stats_cols_html}
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Nota de modo demo ─────────────────────────────────────────────────────
    nota_html = f"""
    <div class="fade-in-delay-2" style="text-align:center; max-width:580px; margin:0 auto 1rem;">
      <p style="font-size:0.84rem; color:{COLOR_TEXT_MUTED}; line-height:1.6; margin:0;">
        Sin base de datos MySQL el sistema activa automáticamente el
        <strong style="color:{COLOR_TEXT};">Modo Demo</strong>
        con datos de ejemplo precargados.
        Credenciales demo: <code style="
            background:{COLOR_CARD};
            border:1px solid {COLOR_BORDER};
            border-radius:4px;
            padding:0.1rem 0.4rem;
            font-size:0.82rem;
            color:{COLOR_ACCENT};
        ">admin / demo123</code>
      </p>
    </div>
    """
    st.markdown(nota_html, unsafe_allow_html=True)

    # ── CTA secundario ────────────────────────────────────────────────────────
    _, col_cta2, _ = st.columns([1.5, 1, 1.5])
    with col_cta2:
        if st.button(
            "Acceder al sistema →",
            type="primary",
            use_container_width=True,
            key="landing_cta_bottom",
        ):
            contenedor.sesion.establecer_navegacion(contenedor.sesion.NAV_LOGIN)
            st.rerun()

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        f'<p style="text-align:center; font-size:0.72rem; color:{COLOR_TEXT_MUTED}; '
        f'margin-top:2rem; letter-spacing:0.04em;">'
        f'Logistik BI · Arquitectura POO + SOLID · Python · Streamlit</p>',
        unsafe_allow_html=True,
    )
