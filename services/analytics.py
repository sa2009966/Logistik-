"""Cálculos de KPIs del dashboard."""

import pandas as pd


class AnalyticsService:
    """Reglas de analítica reutilizables (sin dependencia de Streamlit ni de la base)."""

    def calcular_indicadores(self, df_datos: pd.DataFrame):
        total_ingresos = float(df_datos["monto_total"].sum()) if not df_datos.empty else 0.0
        servicios_realizados = int(len(df_datos))
        monto_promedio = (
            total_ingresos / servicios_realizados if servicios_realizados > 0 else 0.0
        )
        return total_ingresos, servicios_realizados, monto_promedio
