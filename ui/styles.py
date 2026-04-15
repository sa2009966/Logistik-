"""
Tema visual Slate & Steel: CSS centralizado y utilidades de presentación (SRP).
La lógica de negocio vive fuera de este módulo.
"""

import streamlit as st

# --- Paleta Slate & Steel (profesional, sin neón) ---
COLOR_BG = "#0B0E14"
COLOR_CARD = "#161B22"
COLOR_BORDER = "#30363D"
COLOR_ACCENT = "#60A5FA"
COLOR_TEXT = "#E6EDF3"
COLOR_TEXT_MUTED = "#8B949E"
COLOR_TEXT_SUBTLE = "#6E7681"

# Alias retrocompatibles (evitan roturas en imports antiguos)
CYBER_CYAN = COLOR_ACCENT
CYBER_GREEN = "#93C5FD"
CYBER_VIOLET = "#64748B"
BG_PURE = COLOR_BG


def apply_custom_theme() -> None:
    """
    Inyecta el tema global: Inter, paleta Slate & Steel, responsividad mobile-first,
    micro-interacciones y utilidades de skeleton (animación CSS).
    Llamar una vez al inicio de la app (p. ej. desde app.principal).
    """
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        /* Iconos de expander/chevron de Streamlit (Material Symbols); evita texto literal tipo "arrow_downward" */
        @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0&display=swap');

        :root {{
            --ss-bg: {COLOR_BG};
            --ss-card: {COLOR_CARD};
            --ss-border: {COLOR_BORDER};
            --ss-accent: {COLOR_ACCENT};
            --ss-text: {COLOR_TEXT};
            --ss-muted: {COLOR_TEXT_MUTED};
            --ss-radius: 8px;
            --ss-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
            --ss-shadow-hover: 0 8px 32px rgba(0, 0, 0, 0.45);
            --ss-transition: 0.3s ease;
        }}

        html, body,
        [data-testid="stAppViewContainer"],
        .stApp {{
            background: var(--ss-bg) !important;
            color: var(--ss-text) !important;
            font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
        }}

        /* No usar .stApp * con Inter !important: rompe la fuente Material del chevron del st.expander
           y muestra texto literal ("arrow_downward"). Los widgets heredan del contenedor. */
        .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
        .stApp li, .stApp td, .stApp th, .stApp caption, .stApp [data-testid="stMarkdown"] p {{
            font-family: 'Inter', system-ui, -apple-system, sans-serif;
        }}

        [data-testid="stHeader"] {{
            background: rgba(11, 14, 20, 0.92) !important;
            border-bottom: 1px solid var(--ss-border) !important;
            backdrop-filter: blur(8px);
        }}

        [data-testid="stToolbar"] {{
            background: transparent !important;
        }}

        .block-container {{
            padding-top: clamp(1rem, 4vw, 2rem) !important;
            max-width: min(1200px, 100%) !important;
            padding-left: clamp(0.75rem, 3vw, 1.5rem) !important;
            padding-right: clamp(0.75rem, 3vw, 1.5rem) !important;
        }}

        /* Fade-in al cargar el contenido principal */
        .main .block-container {{
            animation: ssFadeIn 0.45s ease-out both;
        }}
        @keyframes ssFadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        h1, h2, h3, h4 {{
            font-weight: 600 !important;
            letter-spacing: -0.02em;
            color: var(--ss-text) !important;
        }}

        /* Tarjetas y bloques tipo card */
        .ss-card {{
            background: var(--ss-card);
            border: 1px solid var(--ss-border);
            border-radius: var(--ss-radius);
            box-shadow: var(--ss-shadow);
            transition: box-shadow var(--ss-transition), border-color var(--ss-transition),
                        transform var(--ss-transition);
        }}
        .ss-card:hover {{
            box-shadow: var(--ss-shadow-hover);
            border-color: rgba(96, 165, 250, 0.35);
        }}

        /* Formularios y expanders */
        div[data-testid="stForm"] {{
            background: var(--ss-card) !important;
            border: 1px solid var(--ss-border) !important;
            border-radius: var(--ss-radius) !important;
            padding: 1.25rem 1.5rem !important;
            box-shadow: var(--ss-shadow);
        }}
        /* Ayuda residual del formulario en runtimes antiguos (sin enter_to_submit=False) */
        [data-testid="stForm"] [data-baseweb="form-input-help"],
        [data-testid="stForm"] [data-testid="stFormSubmitInstructions"] {{
            display: none !important;
        }}

        details[data-testid="stExpander"] {{
            background: var(--ss-card) !important;
            border: 1px solid var(--ss-border) !important;
            border-radius: var(--ss-radius) !important;
            box-shadow: var(--ss-shadow);
            transition: box-shadow var(--ss-transition);
        }}
        details[data-testid="stExpander"]:hover {{
            box-shadow: var(--ss-shadow-hover);
        }}
        details[data-testid="stExpander"] summary {{
            font-weight: 600;
            color: var(--ss-text);
            display: flex !important;
            align-items: center !important;
            gap: 0.5rem !important;
            min-height: 2.75rem !important;
            padding: 0.65rem 1rem !important;
            margin: 0 !important;
            list-style: none !important;
            cursor: pointer;
        }}
        details[data-testid="stExpander"] summary::-webkit-details-marker {{
            display: none !important;
        }}
        /* Campos de texto alineados a tarjeta Slate (#161B22) */
        .stTextInput input,
        .stTextArea textarea,
        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea {{
            background-color: var(--ss-card) !important;
            color: var(--ss-text) !important;
            border: 1px solid var(--ss-border) !important;
            caret-color: var(--ss-accent) !important;
        }}
        .stTextInput input:focus,
        [data-baseweb="input"] input:focus {{
            border-color: rgba(96, 165, 250, 0.55) !important;
            box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.25) !important;
        }}

        /* Contraseña: espacio para icono "ojo" / adornos Base Web y mensajes de validación */
        [data-testid="stTextInput"] [data-baseweb="input"] input[type="password"],
        [data-testid="stTextInput"] input[type="password"] {{
            padding-right: 3rem !important;
            padding-left: 0.85rem !important;
        }}
        [data-testid="stTextInput"] [data-baseweb="baseui-input-adornment--end"],
        [data-testid="stTextInput"] [data-baseweb="input"] [aria-label*="password" i],
        [data-testid="stTextInput"] [data-baseweb="input"] button[aria-label] {{
            margin-right: 0.15rem !important;
        }}
        /* Mensajes bajo el campo (ayuda / error) — no pegados al borde del input */
        [data-testid="stTextInput"] + div,
        [data-testid="stTextInput"] ~ [data-testid="stCaption"] {{
            margin-top: 0.35rem !important;
        }}

        /* Navegación secundaria bajo el formulario de login */
        .ss-login-nav-spacer {{
            height: 1.35rem;
            min-height: 1.35rem;
        }}

        /* Botón secundario (p. ej. Volver): outline sobrio, no compite con primario */
        .stButton > button[kind="secondary"] {{
            background: transparent !important;
            color: var(--ss-muted) !important;
            border: 1px solid var(--ss-border) !important;
            border-radius: var(--ss-radius) !important;
            font-weight: 500 !important;
            transition: background var(--ss-transition), color var(--ss-transition),
                        border-color var(--ss-transition);
        }}
        .stButton > button[kind="secondary"]:hover {{
            background: rgba(96, 165, 250, 0.08) !important;
            color: var(--ss-text) !important;
            border-color: rgba(96, 165, 250, 0.35) !important;
        }}
        [data-baseweb="select"] > div {{
            background-color: var(--ss-card) !important;
            border-color: var(--ss-border) !important;
            color: var(--ss-text) !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 6px;
            background: rgba(22, 27, 34, 0.85);
            border-radius: var(--ss-radius);
            padding: 6px;
            border: 1px solid var(--ss-border);
        }}
        .stTabs [aria-selected="true"] {{
            background: rgba(96, 165, 250, 0.12) !important;
            border-radius: 6px !important;
            color: var(--ss-accent) !important;
        }}

        /* Métricas KPI */
        div[data-testid="metric-container"] {{
            background: var(--ss-card) !important;
            border: 1px solid var(--ss-border) !important;
            border-radius: var(--ss-radius) !important;
            padding: 1rem 1.1rem !important;
            box-shadow: var(--ss-shadow);
            transition: box-shadow var(--ss-transition), border-color var(--ss-transition);
        }}
        div[data-testid="metric-container"]:hover {{
            box-shadow: var(--ss-shadow-hover);
            border-color: rgba(96, 165, 250, 0.25);
        }}
        [data-testid="stMetricValue"] {{
            color: var(--ss-accent) !important;
        }}

        /* Botones primarios */
        .stButton > button[kind="primary"],
        .stDownloadButton > button {{
            background: var(--ss-accent) !important;
            color: #0B0E14 !important;
            font-weight: 600 !important;
            border: none !important;
            border-radius: var(--ss-radius) !important;
            transition: filter var(--ss-transition), transform var(--ss-transition);
        }}
        .stButton > button[kind="primary"]:hover {{
            filter: brightness(1.08);
        }}

        /* Inputs */
        .stTextInput input, .stSelectbox div[data-baseweb="select"] > div,
        [data-baseweb="input"] {{
            border-radius: var(--ss-radius) !important;
        }}

        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: #0D1117 !important;
            border-right: 1px solid var(--ss-border) !important;
        }}

        /* Skeleton (shimmer) — útil con placeholders HTML o futuras extensiones */
        @keyframes ssShimmer {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        .ss-skeleton {{
            border-radius: var(--ss-radius);
            background: linear-gradient(
                90deg,
                {COLOR_CARD} 0%,
                rgba(96, 165, 250, 0.08) 50%,
                {COLOR_CARD} 100%
            );
            background-size: 200% 100%;
            animation: ssShimmer 1.2s ease-in-out infinite;
        }}
        .ss-skeleton-line {{
            height: 14px;
            margin-bottom: 10px;
            width: 100%;
            max-width: 280px;
        }}
        .ss-skeleton-block {{
            height: 120px;
            width: 100%;
            margin-bottom: 1rem;
        }}

        /* Landing: fondo sutil sin rejilla neón */
        .ss-landing-bg {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(ellipse 80% 50% at 50% -15%, rgba(96, 165, 250, 0.06), transparent 55%),
                linear-gradient(180deg, var(--ss-bg) 0%, #0D1117 100%);
        }}
        .ss-landing-inner {{
            position: relative;
            z-index: 1;
            min-height: 88vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: clamp(1rem, 4vw, 2rem);
        }}
        .ss-glass-panel {{
            background: var(--ss-card);
            border: 1px solid var(--ss-border);
            border-radius: var(--ss-radius);
            box-shadow: var(--ss-shadow);
            transition: box-shadow var(--ss-transition), border-color var(--ss-transition);
        }}
        .ss-glass-panel:hover {{
            box-shadow: var(--ss-shadow-hover);
        }}
        .fade-in-up {{
            animation: ssFadeIn 0.55s ease-out both;
        }}
        .fade-in-delay {{
            animation: ssFadeIn 0.6s ease-out 0.12s both;
        }}
        .fade-in-delay-2 {{
            animation: ssFadeIn 0.65s ease-out 0.24s both;
        }}

        /* Layout responsive en zona principal: columnas → apiladas en móvil */
        @media (max-width: 768px) {{
            section.main .block-container [data-testid="stHorizontalBlock"] {{
                flex-wrap: wrap !important;
            }}
            section.main .block-container [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
                flex: 1 1 100% !important;
                width: 100% !important;
                min-width: 100% !important;
                max-width: 100% !important;
            }}
        }}

        /* Gráficos Plotly: contenedor visual tipo tarjeta */
        section.main [data-testid="stPlotlyChart"] {{
            border: 1px solid var(--ss-border);
            border-radius: var(--ss-radius);
            background: var(--ss-card);
            padding: 0.5rem;
            box-shadow: var(--ss-shadow);
            transition: box-shadow var(--ss-transition);
            min-height: 240px;
        }}
        section.main [data-testid="stPlotlyChart"]:hover {{
            box-shadow: var(--ss-shadow-hover);
        }}
        @media (max-width: 768px) {{
            section.main [data-testid="stPlotlyChart"] {{
                min-height: 200px;
                aspect-ratio: 16 / 10;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def envolver_contenedor_landing(html_interior: str) -> str:
    """Envuelve el HTML de la landing con fondo Slate & Steel."""
    return f"""
    <div class="ss-landing-bg"></div>
    <div class="ss-landing-inner">
      {html_interior}
    </div>
    """


def html_skeleton_block() -> str:
    """HTML reutilizable para estado de carga tipo skeleton (solo presentación)."""
    return """
    <div class="ss-skeleton ss-skeleton-line" style="max-width:40%;"></div>
    <div class="ss-skeleton ss-skeleton-line" style="max-width:70%;"></div>
    <div class="ss-skeleton ss-skeleton-block"></div>
    """


class TemaInterfaz:
    """Compatibilidad: delega en apply_custom_theme."""

    def inyectar_estilos_globales(self) -> None:
        apply_custom_theme()
