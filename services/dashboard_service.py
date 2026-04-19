"""Orquestación de fuentes de datos para el panel BI (CSV, demo o MySQL)."""

from typing import TYPE_CHECKING, Any, Optional, Tuple

import pandas as pd
from services.models import KpiAlert

if TYPE_CHECKING:
    from services.alert_manager import AlertManager
    from services.analytics import AnalyticsService
    from services.audit_service import AuditService
    from services.csv_loader import CsvDataLoaderService
    from services.logistica_service import LogisticaService
    from services.models import MapeoColumnas


class DashboardService:
    """Coordina carga de datos, cálculo KPI y reglas de alertas."""

    def __init__(
        self,
        servicio_analitica: "AnalyticsService",
        servicio_csv: "CsvDataLoaderService",
        servicio_logistica: "LogisticaService",
        alert_manager: "AlertManager",
        audit_service: "AuditService",
    ) -> None:
        """Inicializa dependencias del dashboard.

        Args:
            servicio_analitica: Servicio de KPIs.
            servicio_csv: Servicio de carga/normalización CSV.
            servicio_logistica: Servicio de lectura de transacciones.
            alert_manager: Motor de alertas de negocio.
            audit_service: Servicio de auditoría.
        """
        self._analytics = servicio_analitica
        self._csv = servicio_csv
        self._logistica = servicio_logistica
        self._alerts = alert_manager
        self._audit = audit_service

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
                self._audit.registrar_evento(
                    usar_demo=usar_demo,
                    accion="CSV_ERROR",
                    detalle="No se pudo procesar CSV externo.",
                    usuario="dashboard",
                    severidad="WARN",
                )
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
            self._audit.registrar_evento(
                usar_demo=usar_demo,
                accion="CSV_OK",
                detalle="CSV externo cargado correctamente.",
                usuario="dashboard",
            )
            return df, "CSV EXTERNO", None

        if usar_demo:
            return self._logistica.cargar_transacciones_operativas(True), "DEMO OFFLINE", None

        try:
            df = self._logistica.cargar_transacciones_operativas(False)
            return df, "MYSQL ONLINE", None
        except Exception as e:
            self._audit.registrar_evento(
                usar_demo=False,
                accion="DATA_READ_ERROR",
                detalle="Error al leer transacciones desde MySQL.",
                usuario="dashboard",
                severidad="ERROR",
            )
            return None, "", f"Error al leer transacciones de MySQL: {e}"

    def aplicar_mapeo_y_preparar(
        self,
        df_raw: pd.DataFrame,
        mapeo: "MapeoColumnas",
        usar_demo: bool,
    ) -> Tuple[Optional[pd.DataFrame], str, Optional[str]]:
        """Aplica un mapeo de columnas, re-valida y prepara el DataFrame CSV.

        Extensión OCP: no modifica ``construir_dataset_visualizacion``.
        Se usa cuando el CSV original no tiene las columnas canónicas y el usuario
        define el mapeo desde la UI.

        Args:
            df_raw: DataFrame crudo tal como salió de ``cargar_csv``.
            mapeo: Asignación columna_usuario → columna_sistema.
            usar_demo: Modo activo (solo para auditoría).

        Returns:
            Tupla ``(dataframe, etiqueta_fuente, mensaje_error)``.
        """
        df_mapeado = self._csv.aplicar_mapeo_columnas(df_raw, mapeo)
        faltantes = self._csv.validar_columnas_csv(df_mapeado)
        if faltantes:
            return (
                None,
                "",
                f"Tras el mapeo aún faltan columnas requeridas: {', '.join(faltantes)}.",
            )
        df_preparado = self._csv.preparar_dataframe_csv(df_mapeado)
        self._audit.registrar_evento(
            usar_demo=usar_demo,
            accion="CSV_MAPEADO_OK",
            detalle="CSV externo cargado tras mapeo manual de columnas.",
            usuario="dashboard",
        )
        return df_preparado, "CSV EXTERNO (MAPEADO)", None

    def calcular_indicadores(self, df_filtrado: pd.DataFrame) -> tuple[float, int, float]:
        """Calcula total, volumen y ticket promedio."""
        return self._analytics.calcular_indicadores(df_filtrado)

    def evaluar_alertas_kpi(
        self,
        total_ingresos: float,
        servicios_realizados: int,
        monto_promedio: float,
    ) -> list[KpiAlert]:
        """Evalúa alertas de salud para KPIs agregados."""
        return self._alerts.evaluar_kpis(
            total_ingresos=total_ingresos,
            servicios_realizados=servicios_realizados,
            monto_promedio=monto_promedio,
        )
