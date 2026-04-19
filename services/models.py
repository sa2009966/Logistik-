"""Modelos de aplicación para auditoría, alertas, exportación, admin y BI."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import TYPE_CHECKING, List, Mapping

if TYPE_CHECKING:
    import pandas as pd


@dataclass(slots=True)
class AuditEvent:
    """Representa un evento de trazabilidad del sistema."""

    accion: str
    detalle: str
    usuario: str
    severidad: str = "INFO"
    contexto: Mapping[str, str] = field(default_factory=dict)
    timestamp_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(slots=True)
class KpiAlert:
    """Representa un diagnóstico de salud de un KPI."""

    clave: str
    nivel: str
    titulo: str
    mensaje: str


@dataclass(slots=True)
class ReportPayload:
    """Representa un artefacto exportable."""

    nombre_archivo: str
    mime_type: str
    contenido: bytes


@dataclass(slots=True)
class UsuarioInfo:
    """Proyección de usuario para la capa de administración."""

    id_usuario: int
    nombre_usuario: str
    rol: str
    creado_en: str


@dataclass(slots=True)
class MapeoColumnas:
    """Asignación de columnas del CSV del usuario a las columnas requeridas por el sistema.

    Cada campo contiene el nombre de la columna tal como aparece en el CSV original.
    Un valor vacío significa que la columna requerida ya existe con ese mismo nombre.
    """

    monto_total: str
    estado: str
    tipo_servicio: str


@dataclass(slots=True)
class FiltrosBi:
    """Criterios de filtrado para consultas BI dinámicas."""

    fecha_inicio: date
    fecha_fin: date
    estados: List[str]
    tipos_servicio: List[str]


@dataclass
class BiSnapshot:
    """Resultado de una consulta BI filtrada."""

    df_filtrado: "pd.DataFrame"
    total_ingresos: float
    servicios_realizados: int
    monto_promedio: float
