"""Servicio SRP para lectura, mapeo y normalización de CSV externo."""

from typing import TYPE_CHECKING, Any, List
import pandas as pd
import logging

from core.constants import ConstantesNegocio

if TYPE_CHECKING:
    from services.models import MapeoColumnas

class CsvDataLoaderService:
    """Responsable exclusivo de cargar/validar/mapear/preparar CSV."""

    def cargar_csv(self, archivo_csv: Any) -> pd.DataFrame:
        """
        Carga el CSV de forma robusta con reintentos para separadores y control de puntero.
        """
        # 1. RESET DEL PUNTERO: Vital para archivos subidos en Streamlit
        if hasattr(archivo_csv, 'seek'):
            archivo_csv.seek(0)

        # 2. Intento 1: Detección automática (Motor Python)
        try:
            df = pd.read_csv(archivo_csv, sep=None, engine='python', encoding='utf-8-sig')
            if not df.empty and len(df.columns) > 1:
                return df
        except Exception:
            pass # Si falla, seguimos intentando

        # 3. Intento 2: Bucle de fuerza bruta para separadores comunes
        separadores_comunes = [',', ';', '\t']
        for sep in separadores_comunes:
            try:
                archivo_csv.seek(0) # Reiniciamos antes de cada intento
                df = pd.read_csv(archivo_csv, sep=sep, encoding='utf-8-sig')
                if len(df.columns) > 1:
                    return df
            except Exception:
                continue

        # 4. Fallo total
        logging.error("Error crítico: No se pudo determinar el formato del CSV.")
        raise ValueError("No se pudo procesar el archivo CSV. Asegúrate de que no sea un archivo de Excel (.xlsx) y que contenga comas o puntos y coma.")

    def validar_columnas_csv(self, df_csv: pd.DataFrame) -> List[str]:
        return [col for col in ConstantesNegocio.CSV_REQUIRED_COLUMNS if col not in df_csv.columns]

    def columnas_faltantes_para_mapeo(self, df_csv: pd.DataFrame) -> List[str]:
        """Devuelve las columnas requeridas que no están presentes en el CSV."""
        return self.validar_columnas_csv(df_csv)

    def aplicar_mapeo_columnas(
        self, df_csv: pd.DataFrame, mapeo: "MapeoColumnas"
    ) -> pd.DataFrame:
        """Renombra columnas del CSV del usuario a los nombres canónicos del sistema."""
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
        """Limpia los tipos de datos y asegura valores mínimos."""
        df_csv = df_csv.copy()
        
        # Normalizar fecha
        if "fecha" not in df_csv.columns:
            df_csv["fecha"] = pd.Timestamp.today().date()
        df_csv["fecha"] = pd.to_datetime(df_csv["fecha"], errors="coerce").fillna(
            pd.Timestamp.today()
        )
        
        # Asegurar tipos numéricos y strings
        df_csv["monto_total"] = pd.to_numeric(df_csv["monto_total"], errors="coerce").fillna(0.0)
        df_csv["estado"] = df_csv["estado"].astype(str)
        df_csv["tipo_servicio"] = df_csv["tipo_servicio"].astype(str)
        
        return df_csv