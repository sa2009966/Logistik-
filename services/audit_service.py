"""Servicio de auditoría y trazabilidad para casos de uso de negocio."""

from typing import Mapping

from services.contracts import IAuditRepository
from services.models import AuditEvent


class AuditService:
    """Gestiona el ciclo de vida de eventos de auditoría (SRP)."""

    def __init__(self, repos_por_modo: dict[bool, IAuditRepository]) -> None:
        """Inicializa el servicio.

        Args:
            repos_por_modo: Mapa ``{usar_demo: repositorio}`` para MySQL y demo.
        """
        self._repos = repos_por_modo

    def _repo(self, usar_demo: bool) -> IAuditRepository:
        return self._repos[usar_demo]

    def inicializar_almacen(self, usar_demo: bool) -> None:
        """Inicializa infraestructura de auditoría del modo seleccionado."""
        self._repo(usar_demo).inicializar_almacen_auditoria()

    def registrar_evento(
        self,
        usar_demo: bool,
        accion: str,
        detalle: str,
        usuario: str,
        severidad: str = "INFO",
        contexto: Mapping[str, str] | None = None,
    ) -> None:
        """Registra un evento de auditoría.

        Args:
            usar_demo: ``True`` si opera sobre el modo demo.
            accion: Acción auditada.
            detalle: Descripción human-readable del evento.
            usuario: Usuario responsable o técnico.
            severidad: Nivel de criticidad (INFO, WARN, ERROR).
            contexto: Datos adicionales serializables.
        """
        evento = AuditEvent(
            accion=accion,
            detalle=detalle,
            usuario=usuario,
            severidad=severidad,
            contexto=contexto or {},
        )
        self._repo(usar_demo).registrar_evento(evento)

    def listar_eventos_recientes(self, usar_demo: bool, limite: int = 50) -> list[AuditEvent]:
        """Consulta eventos recientes en el repositorio correspondiente."""
        return self._repo(usar_demo).listar_eventos_recientes(limite=limite)
