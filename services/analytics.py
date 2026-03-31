"""Cálculos de KPIs y utilidades para datos importados desde CSV."""

import pandas as pd

from core.constants import CSV_REQUIRED_COLUMNS


def calcular_indicadores(df_datos: pd.DataFrame):
    """
    Devuelve (total ingresos, cantidad de servicios, monto promedio)
    sobre el DataFrame ya filtrado.
    """
    total_ingresos = float(df_datos["monto_total"].sum()) if not df_datos.empty else 0.0
    servicios_realizados = int(len(df_datos))
    monto_promedio = (
        total_ingresos / servicios_realizados if servicios_realizados > 0 else 0.0
    )
    return total_ingresos, servicios_realizados, monto_promedio


def validar_columnas_csv(df_csv: pd.DataFrame):
    """Lista las columnas obligatorias que faltan en el CSV importado."""
    faltantes = [col for col in CSV_REQUIRED_COLUMNS if col not in df_csv.columns]
    return faltantes


def preparar_dataframe_csv(df_csv: pd.DataFrame) -> pd.DataFrame:
    """Normaliza tipos y fechas para alinear el CSV con el esquema del tablero."""
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
