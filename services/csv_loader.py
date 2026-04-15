"""Servicio SRP para lectura y normalización de CSV externo."""

from typing import Any, List

import pandas as pd

from core.constants import ConstantesNegocio


class CsvDataLoaderService:
    """Responsable exclusivo de cargar/validar/preparar CSV."""

    def cargar_csv(self, archivo_csv: Any) -> pd.DataFrame:
        return pd.read_csv(archivo_csv)

    def validar_columnas_csv(self, df_csv: pd.DataFrame) -> List[str]:
        return [col for col in ConstantesNegocio.CSV_REQUIRED_COLUMNS if col not in df_csv.columns]

    def preparar_dataframe_csv(self, df_csv: pd.DataFrame) -> pd.DataFrame:
        df_csv = df_csv.copy()
        if "fecha" not in df_csv.columns:
            df_csv["fecha"] = pd.Timestamp.today().date()
        df_csv["fecha"] = pd.to_datetime(df_csv["fecha"], errors="coerce").fillna(
            pd.Timestamp.today()
        )
        df_csv["monto_total"] = pd.to_numeric(df_csv["monto_total"], errors="coerce").fillna(0.0)
        df_csv["estado"] = df_csv["estado"].astype(str)
        df_csv["tipo_servicio"] = df_csv["tipo_servicio"].astype(str)
        return df_csv
