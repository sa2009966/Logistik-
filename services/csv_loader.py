"""Servicio SRP para lectura, mapeo y normalización de CSV externo."""

from typing import TYPE_CHECKING, Any, List

import pandas as pd

from core.constants import ConstantesNegocio

if TYPE_CHECKING:
    from services.models import MapeoColumnas


class CsvDataLoaderService:
    """Responsable exclusivo de cargar/validar/mapear/preparar CSV."""

    def cargar_csv(self, archivo_csv: Any) -> pd.DataFrame:
        return pd.read_csv(archivo_csv)

    def validar_columnas_csv(self, df_csv: pd.DataFrame) -> List[str]:
        return [col for col in ConstantesNegocio.CSV_REQUIRED_COLUMNS if col not in df_csv.columns]

    def columnas_faltantes_para_mapeo(self, df_csv: pd.DataFrame) -> List[str]:
        """Devuelve las columnas requeridas que no están presentes en el CSV."""
        return self.validar_columnas_csv(df_csv)

    def aplicar_mapeo_columnas(
        self, df_csv: pd.DataFrame, mapeo: "MapeoColumnas"
    ) -> pd.DataFrame:
        """Renombra columnas del CSV del usuario a los nombres canónicos del sistema.

        Solo renombra las columnas cuyo valor en el mapeo difiere del nombre destino,
        evitando sobreescrituras accidentales cuando la columna ya existe con el nombre
        correcto.

        Args:
            df_csv: DataFrame original tal como fue leído del archivo.
            mapeo: Objeto con la asignación usuario→sistema por cada columna requerida.

        Returns:
            Nuevo DataFrame con columnas renombradas (no modifica el original).
        """
        destinos = {
            "monto_total": mapeo.monto_total,
            "estado": mapeo.estado,
            "tipo_servicio": mapeo.tipo_servicio,
        }
        rename_map = {
            origen: destino
            for destino, origen in destinos.items()
            if origen and origen != destino and origen in df_csv.columns
        }
        return df_csv.rename(columns=rename_map)

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
