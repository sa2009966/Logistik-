"""
Figuras Plotly con plantilla oscura y acentos cian / verde neón (Logistik BI).
"""

from abc import ABC, abstractmethod
from typing import Dict, Iterable, Optional

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


class BaseGraficoPlotly(ABC):
    """
    Base OCP para nuevos gráficos.
    Agregar un nuevo gráfico implica crear una subclase y registrarla.
    """

    key: str = ""

    def _aplicar_diseno_ciber(self, fig: go.Figure, titulo: Optional[str] = None) -> go.Figure:
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
            color_discrete_sequence=[CYBER_CYAN],
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        return self._aplicar_diseno_ciber(fig, "Tendencia de Ingresos")


class GraficoBarrasIngresosServicio(BaseGraficoPlotly):
    key = "barras_ingresos_servicio"

    def render(self, df: pd.DataFrame) -> go.Figure:
        fig = px.bar(
            df,
            x="tipo_servicio",
            y="monto_total",
            color="tipo_servicio",
            color_discrete_sequence=_ESCALA_CIBER,
        )
        fig.update_xaxes(tickangle=-25)
        return self._aplicar_diseno_ciber(fig, "Ingresos por tipo de servicio")


class GraficoPastelParticipacionEstado(BaseGraficoPlotly):
    key = "pastel_participacion_estado"

    def render(self, df: pd.DataFrame) -> go.Figure:
        fig = px.pie(
            df,
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
        return self._aplicar_diseno_ciber(fig, "Participación por estado")


class RenderizadorGraficosBi:
    """Registro de gráficos OCP: añade nuevas subclases sin tocar esta clase."""

    def __init__(self, graficos: Iterable[BaseGraficoPlotly]) -> None:
        self._graficos: Dict[str, BaseGraficoPlotly] = {g.key: g for g in graficos}

    def render(self, key_grafico: str, df: pd.DataFrame) -> go.Figure:
        grafico = self._graficos.get(key_grafico)
        if grafico is None:
            raise KeyError(f"No existe un gráfico registrado con clave '{key_grafico}'.")
        return grafico.render(df)
