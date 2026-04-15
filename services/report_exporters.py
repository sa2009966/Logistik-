"""Exportadores de reportes desacoplados de la fuente de datos."""

from io import BytesIO

import pandas as pd

from services.contracts import IReportExporter
from services.models import ReportPayload


def _asegurar_openpyxl_disponible() -> None:
    """Comprueba que openpyxl esté instalado (motor requerido por pandas para .xlsx)."""
    try:
        import openpyxl  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "Falta el paquete openpyxl. Instálelo en el entorno virtual: "
            "`pip install openpyxl` (o `pip install -r requirements.txt`)."
        ) from exc


class ExcelReportExporter(IReportExporter):
    """Exporta datasets a Excel (.xlsx)."""

    def exportar(self, df_reporte: pd.DataFrame, nombre_base: str) -> ReportPayload:
        """Serializa un DataFrame a bytes Excel.

        Args:
            df_reporte: DataFrame final filtrado.
            nombre_base: Nombre base del archivo.

        Returns:
            Contenedor con bytes del archivo, nombre y mime type.

        Raises:
            ValueError: Si el DataFrame es nulo o vacío.
            RuntimeError: Si falla el motor de exportación.
        """
        if df_reporte is None or df_reporte.empty:
            raise ValueError("No hay datos disponibles para exportar a Excel.")

        _asegurar_openpyxl_disponible()

        salida = BytesIO()
        try:
            with pd.ExcelWriter(salida, engine="openpyxl") as writer:
                df_reporte.to_excel(writer, index=False, sheet_name="reporte")
            contenido = salida.getvalue()
        except ImportError as exc:
            raise RuntimeError(
                "No se pudo cargar el motor openpyxl. Ejecute: pip install openpyxl"
            ) from exc
        except Exception as exc:
            raise RuntimeError(
                "No fue posible generar el archivo Excel. "
                f"Detalle técnico: {exc!s}. Si falta openpyxl: pip install openpyxl"
            ) from exc

        safe_name = nombre_base.strip() or "reporte_logistik"
        return ReportPayload(
            nombre_archivo=f"{safe_name}.xlsx",
            mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            contenido=contenido,
        )
