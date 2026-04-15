"""Orquestación de fuentes de datos para el panel BI (CSV, demo o MySQL)."""

from typing import TYPE_CHECKING, Any, Optional, Tuple

import pandas as pd

if TYPE_CHECKING:
    from services.analytics import AnalyticsService
    from services.csv_loader import CsvDataLoaderService
    from services.logistica_service import LogisticaService


class DashboardService:
    def __init__(
        self,
        servicio_analitica: "AnalyticsService",
        servicio_csv: "CsvDataLoaderService",
        servicio_logistica: "LogisticaService",
    ) -> None:
        self._analytics = servicio_analitica
        self._csv = servicio_csv
        self._logistica = servicio_logistica

    def construir_dataset_visualizacion(
        self,
        usar_demo: bool,
        archivo_csv: Optional[Any],
    ) -> Tuple[Optional[pd.DataFrame], str, Optional[str]]:
        """
        Devuelve (dataframe, etiqueta_fuente, mensaje_error).
        Si hay error de validación o lectura, dataframe es None y mensaje_error describe el fallo.
        """
        if archivo_csv is not None:
            try:
                df_csv = self._csv.cargar_csv(archivo_csv)
            except Exception as e:
                return None, "", f"No se pudo procesar el CSV: {e}"
            faltantes = self._csv.validar_columnas_csv(df_csv)
            if faltantes:
                cols = ", ".join(faltantes)
                return (
                    None,
                    "",
                    "El archivo CSV no tiene la estructura necesaria. "
                    f"Faltan: {cols}. "
                    "Columnas mínimas: monto_total, estado, tipo_servicio.",
                )
            df = self._csv.preparar_dataframe_csv(df_csv)
            return df, "CSV EXTERNO", None

        if usar_demo:
            return self._logistica.cargar_transacciones_operativas(True), "DEMO OFFLINE", None

        try:
            df = self._logistica.cargar_transacciones_operativas(False)
            return df, "MYSQL ONLINE", None
        except Exception as e:
            return None, "", f"Error al leer transacciones de MySQL: {e}"

    def calcular_indicadores(self, df_filtrado: pd.DataFrame):
        return self._analytics.calcular_indicadores(df_filtrado)
