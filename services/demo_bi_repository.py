"""Repositorio BI dinámico en memoria para modo demo/offline."""

from typing import TYPE_CHECKING

import pandas as pd

from services.contracts import IBiDinamicoRepository
from services.models import FiltrosBi

if TYPE_CHECKING:
    from services.demo_data import DemoDataStore


class DemoBiDinamicoRepository(IBiDinamicoRepository):
    """Aplica los filtros de FiltrosBi en memoria sobre el DemoDataStore."""

    def __init__(self, demo_store: "DemoDataStore") -> None:
        self._demo = demo_store

    def cargar_transacciones_filtradas(self, filtros: FiltrosBi) -> pd.DataFrame:
        df = self._demo.cargar_transacciones_dataframe().copy()

        if df.empty:
            return df

        df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")

        fecha_inicio = pd.Timestamp(filtros.fecha_inicio)
        fecha_fin = pd.Timestamp(filtros.fecha_fin)

        mascara = (
            (df["fecha"] >= fecha_inicio)
            & (df["fecha"] <= fecha_fin)
        )
        if filtros.estados:
            mascara &= df["estado"].astype(str).isin(filtros.estados)
        if filtros.tipos_servicio:
            mascara &= df["tipo_servicio"].astype(str).isin(filtros.tipos_servicio)

        return df[mascara].reset_index(drop=True)
