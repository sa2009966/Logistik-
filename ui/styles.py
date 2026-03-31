"""Inyección de CSS global para tema oscuro Elite / Cyber y contenedor de landing."""

import streamlit as st

# Paleta compartida con ui/charts.py para coherencia visual
CYBER_CYAN = "#00f5ff"
CYBER_GREEN = "#39ff14"
CYBER_VIOLET = "#bf5fff"
BG_PURE = "#000000"


def inyectar_estilos_globales() -> None:
    """Aplica tipografía, fondo, glassmorphism y animaciones a toda la app Streamlit."""
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

        html, body, [data-testid="stAppViewContainer"] {{
            background: {BG_PURE} !important;
            color: #e8f1ff !important;
            font-family: 'Outfit', system-ui, sans-serif !important;
        }}

        [data-testid="stHeader"] {{
            background: rgba(0,0,0,0.85) !important;
            border-bottom: 1px solid rgba(0, 245, 255, 0.2);
        }}

        [data-testid="stToolbar"] {{
            background: transparent !important;
        }}

        .block-container {{
            padding-top: 2rem !important;
            max-width: 1200px !important;
        }}

        h1, h2, h3 {{
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
        }}

        .elite-glow {{
            text-shadow: 0 0 24px rgba(0, 245, 255, 0.35);
        }}

        .fade-in-up {{
            animation: fadeInUp 0.9s ease-out both;
        }}
        .fade-in-delay {{
            animation: fadeInUp 1s ease-out 0.2s both;
        }}
        .fade-in-delay-2 {{
            animation: fadeInUp 1.1s ease-out 0.45s both;
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(22px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes pulseLine {{
            0%, 100% {{ opacity: 0.35; }}
            50% {{ opacity: 1; }}
        }}

        .cyber-grid-bg {{
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            background:
                radial-gradient(ellipse 80% 50% at 50% -20%, rgba(0, 245, 255, 0.12), transparent 55%),
                radial-gradient(ellipse 60% 40% at 100% 50%, rgba(57, 255, 20, 0.06), transparent 50%),
                linear-gradient(180deg, #000000 0%, #050508 40%, #000000 100%);
        }}
        .cyber-grid-bg::before {{
            content: "";
            position: absolute;
            inset: 0;
            background-image:
                linear-gradient(rgba(0, 245, 255, 0.04) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 245, 255, 0.04) 1px, transparent 1px);
            background-size: 48px 48px;
            animation: pulseLine 6s ease-in-out infinite;
        }}

        .glass-panel {{
            background: rgba(12, 18, 28, 0.55) !important;
            border: 1px solid rgba(0, 245, 255, 0.18) !important;
            border-radius: 18px !important;
            backdrop-filter: blur(14px) saturate(140%);
            -webkit-backdrop-filter: blur(14px) saturate(140%);
            box-shadow:
                0 0 0 1px rgba(255,255,255,0.03) inset,
                0 20px 50px rgba(0, 0, 0, 0.55);
        }}

        div[data-testid="stForm"] {{
            background: rgba(10, 14, 22, 0.65) !important;
            border: 1px solid rgba(0, 245, 255, 0.2) !important;
            border-radius: 18px !important;
            padding: 1.25rem 1.5rem !important;
            backdrop-filter: blur(16px);
        }}

        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: rgba(0,0,0,0.35);
            border-radius: 12px;
            padding: 6px;
            border: 1px solid rgba(0, 245, 255, 0.15);
        }}
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, rgba(0, 245, 255, 0.2), rgba(57, 255, 20, 0.12)) !important;
            border-radius: 10px !important;
            color: {CYBER_CYAN} !important;
        }}

        div[data-testid="metric-container"] {{
            background: rgba(8, 12, 20, 0.75);
            border: 1px solid rgba(0, 245, 255, 0.15);
            border-radius: 14px;
            padding: 0.75rem 1rem;
        }}

        .stDownloadButton button {{
            background: linear-gradient(135deg, {CYBER_CYAN}, {CYBER_GREEN}) !important;
            color: #000 !important;
            font-weight: 600 !important;
            border: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def envolver_contenedor_landing(html_interior: str) -> str:
    """Envuelve el HTML de la landing con fondo de rejilla y capa centrada."""
    return f"""
    <div class="cyber-grid-bg"></div>
    <div style="position:relative; z-index:1; min-height: 88vh; display:flex; flex-direction:column; justify-content:center; padding: 2rem 1rem;">
      {html_interior}
    </div>
    """
