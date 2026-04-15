"""Modelos de aplicación para auditoría, alertas y exportación."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping


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
