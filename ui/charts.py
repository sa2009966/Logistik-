"""
Figuras Plotly alineadas al tema Slate & Steel (sin neón).
"""

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from ui.styles import COLOR_ACCENT, COLOR_BG, COLOR_BORDER, COLOR_CARD, COLOR_TEXT

_PLANTILLA = "plotly_dark"

_ESCALA_SLATE = [
    "#60A5FA",
    "#93C5FD",
    "#3B82F6",
    "#64748B",
    "#94A3B8",
    "#CBD5E1",
]


class BaseGraficoPlotly(ABC):
    """
    Base OCP para nuevos gráficos.
    Agregar un nuevo gráfico implica crear una subclase y registrarla.
    """

    key: str = ""

    def _aplicar_tema_slate(self, fig: go.Figure, titulo: Optional[str] = None) -> go.Figure:
        kwargs = dict(
            template=_PLANTILLA,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=COLOR_CARD,
            font=dict(color=COLOR_TEXT, family="Inter, system-ui, sans-serif"),
            margin=dict(l=40, r=20, t=60 if titulo else 40, b=40),
            xaxis=dict(
                gridcolor="rgba(48, 54, 61, 0.6)",
                zerolinecolor="rgba(96, 165, 250, 0.25)",
                linecolor=COLOR_BORDER,
            ),
            yaxis=dict(
                gridcolor="rgba(48, 54, 61, 0.6)",
                zerolinecolor="rgba(96, 165, 250, 0.25)",
                linecolor=COLOR_BORDER,
            ),
            legend=dict(
                bgcolor="rgba(22, 27, 34, 0.85)",
                bordercolor=COLOR_BORDER,
                borderwidth=1,
            ),
        )
        if titulo:
            kwargs["title"] = dict(text=titulo, font=dict(size=15, color=COLOR_ACCENT))
        fig.update_layout(**kwargs)
        return fig

    @abstractmethod
    def render(self, df: pd.DataFrame) -> go.Figure:
        pass


class GraficoTendenciaIngresos(BaseGraficoPlotly):
    key = "linea_tendencia_ingresos"

    def render(self, df: pd.DataFrame) -> go.Figure:
        fig = px.line(
            df,
            x="fecha",
            y="monto_total",
            markers=True,
            color_discrete_sequence=[COLOR_ACCENT],
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=7))
        return self._aplicar_tema_slate(fig, "Tendencia de ingresos")


class GraficoBarrasIngresosServicio(BaseGraficoPlotly):
    key = "barras_ingresos_servicio"

    def render(self, df: pd.DataFrame) -> go.Figure:
        fig = px.bar(
            df,
            x="tipo_servicio",
            y="monto_total",
            color="tipo_servicio",
            color_discrete_sequence=_ESCALA_SLATE,
        )
        fig.update_xaxes(tickangle=-25)
        return self._aplicar_tema_slate(fig, "Ingresos por tipo de servicio")


class GraficoPastelParticipacionEstado(BaseGraficoPlotly):
    key = "pastel_participacion_estado"

    def render(self, df: pd.DataFrame) -> go.Figure:
        fig = px.pie(
            df,
            names="estado",
            values="monto_total",
            color="estado",
            color_discrete_sequence=_ESCALA_SLATE,
            hole=0.42,
        )
        fig.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color=COLOR_BG, width=1.5)),
        )
        return self._aplicar_tema_slate(fig, "Participación por estado")


class RenderizadorGraficosBi:
    """Registro de gráficos OCP: añade nuevas subclases sin tocar esta clase."""

    def __init__(self, graficos: Iterable[BaseGraficoPlotly]) -> None:
        self._graficos: Dict[str, BaseGraficoPlotly] = {g.key: g for g in graficos}

    def render(self, key_grafico: str, df: pd.DataFrame) -> go.Figure:
        grafico = self._graficos.get(key_grafico)
        if grafico is None:
            raise KeyError(f"No existe un gráfico registrado con clave '{key_grafico}'.")
        return grafico.render(df)
