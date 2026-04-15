"""Repositorio de auditoría en memoria para modo demo/offline."""

from services.contracts import IAuditRepository
from services.models import AuditEvent


class InMemoryAuditRepository(IAuditRepository):
    """Implementación de auditoría en memoria (sin dependencias externas)."""

    def __init__(self) -> None:
        self._eventos: list[AuditEvent] = []

    def inicializar_almacen_auditoria(self) -> None:
        """No requiere inicialización explícita para almacenamiento en memoria."""
        return None

    def registrar_evento(self, evento: AuditEvent) -> None:
        """Añade el evento al buffer en memoria."""
        self._eventos.append(evento)

    def listar_eventos_recientes(self, limite: int = 50) -> list[AuditEvent]:
        """Devuelve los últimos eventos almacenados."""
        safe_limit = max(1, int(limite))
        return list(reversed(self._eventos[-safe_limit:]))
