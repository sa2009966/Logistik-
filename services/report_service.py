"""Orquestación de exportación de reportes y auditoría asociada."""

import pandas as pd

from services.audit_service import AuditService
from services.contracts import IReportExporter
from services.models import ReportPayload


class ReportService:
    """Coordina exportación y trazabilidad sin acoplar UI ni infraestructura."""

    def __init__(self, exporter_excel: IReportExporter, audit_service: AuditService) -> None:
        self._excel = exporter_excel
        self._audit = audit_service

    def preparar_excel(
        self,
        df_reporte: pd.DataFrame,
        nombre_base: str,
    ) -> ReportPayload:
        """Genera reporte Excel listo para descarga.

        Args:
            df_reporte: DataFrame a exportar.
            nombre_base: Nombre base del archivo.

        Returns:
            ReportPayload listo para `st.download_button`.
        """
        return self._excel.exportar(df_reporte=df_reporte, nombre_base=nombre_base)

    def registrar_descarga_excel(
        self,
        usar_demo: bool,
        usuario: str,
        filas: int,
        nombre_archivo: str,
    ) -> None:
        """Registra evento de descarga de reporte en auditoría."""
        self._audit.registrar_evento(
            usar_demo=usar_demo,
            accion="REPORTE_EXPORTADO",
            detalle=f"Reporte Excel descargado: {nombre_archivo}",
            usuario=usuario or "system",
            severidad="INFO",
            contexto={"filas": str(filas)},
        )
