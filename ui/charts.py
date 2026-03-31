"""
Figuras Plotly con plantilla oscura y acentos cian / verde neón (Logistik BI).
"""

from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.styles import CYBER_CYAN, CYBER_GREEN, CYBER_VIOLET

_PLANTILLA = "plotly_dark"

_ESCALA_CIBER = [
    CYBER_CYAN,
    CYBER_GREEN,
    CYBER_VIOLET,
    "#ff6b35",
    "#00c853",
    "#7c4dff",
]


def _aplicar_diseno_ciber(fig: go.Figure, titulo: Optional[str] = None) -> go.Figure:
    """Unifica fondos transparentes, rejillas y tipografía con el resto de la UI."""
    kwargs = dict(
        template=_PLANTILLA,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,12,20,0.5)",
        font=dict(color="#e0e8f0", family="Outfit, sans-serif"),
        margin=dict(l=40, r=20, t=60 if titulo else 40, b=40),
        xaxis=dict(gridcolor="rgba(0,245,255,0.12)", zerolinecolor="rgba(0,245,255,0.2)"),
        yaxis=dict(gridcolor="rgba(0,245,255,0.12)", zerolinecolor="rgba(0,245,255,0.2)"),
        legend=dict(
            bgcolor="rgba(0,0,0,0.4)",
            bordercolor="rgba(0,245,255,0.25)",
            borderwidth=1,
        ),
    )
    if titulo:
        kwargs["title"] = dict(text=titulo, font=dict(size=16, color=CYBER_CYAN))
    fig.update_layout(**kwargs)
    return fig


def grafico_linea_tendencia_ingresos(df_linea: pd.DataFrame) -> go.Figure:
    """Serie temporal de ingresos agrupados por día."""
    fig = px.line(
        df_linea,
        x="fecha",
        y="monto_total",
        markers=True,
        color_discrete_sequence=[CYBER_CYAN],
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=8))
    return _aplicar_diseno_ciber(fig, "Tendencia de Ingresos")


def grafico_barras_ingresos_servicio(df_servicio: pd.DataFrame) -> go.Figure:
    """Barras por tipo de servicio con leyenda de color."""
    fig = px.bar(
        df_servicio,
        x="tipo_servicio",
        y="monto_total",
        color="tipo_servicio",
        color_discrete_sequence=_ESCALA_CIBER,
    )
    fig.update_xaxes(tickangle=-25)
    return _aplicar_diseno_ciber(fig, "Ingresos por tipo de servicio")


def grafico_pastel_participacion_estado(df_estado: pd.DataFrame) -> go.Figure:
    """Distribución de montos por estado operativo."""
    fig = px.pie(
        df_estado,
        names="estado",
        values="monto_total",
        color="estado",
        color_discrete_sequence=_ESCALA_CIBER,
        hole=0.42,
    )
    fig.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#0a0e14", width=1.5)),
    )
    return _aplicar_diseno_ciber(fig, "Participación por estado")
