"""Repositorio MySQL para auditoría de eventos de sistema."""

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from services.contracts import IAuditRepository
from services.models import AuditEvent

if TYPE_CHECKING:
    from database.connection import GestorConexionMySQL


class MysqlAuditRepository(IAuditRepository):
    """Persistencia de auditoría en MySQL con tabla dedicada."""

    _TABLE_AUDIT = "auditoria_logistik"

    def __init__(self, gestor_mysql: "GestorConexionMySQL") -> None:
        self._gestor = gestor_mysql

    def inicializar_almacen_auditoria(self) -> None:
        """Crea la tabla de auditoría si no existe."""
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {self._TABLE_AUDIT} (
                    id_evento BIGINT AUTO_INCREMENT PRIMARY KEY,
                    timestamp_utc DATETIME NOT NULL,
                    accion VARCHAR(100) NOT NULL,
                    detalle TEXT NOT NULL,
                    usuario VARCHAR(100) NOT NULL,
                    severidad VARCHAR(20) NOT NULL,
                    contexto_json JSON NULL
                )
                """
            )
            conn.commit()
        finally:
            cursor.close()

    def registrar_evento(self, evento: AuditEvent) -> None:
        """Persiste un evento de auditoría."""
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                INSERT INTO {self._TABLE_AUDIT}
                (timestamp_utc, accion, detalle, usuario, severidad, contexto_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    evento.timestamp_utc.astimezone(timezone.utc).replace(tzinfo=None),
                    evento.accion,
                    evento.detalle,
                    evento.usuario,
                    evento.severidad,
                    json.dumps(dict(evento.contexto), ensure_ascii=True) if evento.contexto else None,
                ),
            )
            conn.commit()
        finally:
            cursor.close()

    def listar_eventos_recientes(self, limite: int = 50) -> list[AuditEvent]:
        """Devuelve eventos recientes ordenados por fecha descendente."""
        conn = self._gestor.obtener()
        cursor = conn.cursor()
        try:
            cursor.execute(
                f"""
                SELECT timestamp_utc, accion, detalle, usuario, severidad, contexto_json
                FROM {self._TABLE_AUDIT}
                ORDER BY id_evento DESC
                LIMIT %s
                """,
                (int(max(1, limite)),),
            )
            rows = cursor.fetchall()
        finally:
            cursor.close()

        eventos: list[AuditEvent] = []
        for ts, accion, detalle, usuario, severidad, contexto_json in rows:
            contexto = {}
            if contexto_json:
                try:
                    contexto = json.loads(contexto_json)
                except (ValueError, TypeError):
                    contexto = {}
            eventos.append(
                AuditEvent(
                    accion=str(accion),
                    detalle=str(detalle),
                    usuario=str(usuario),
                    severidad=str(severidad),
                    contexto=contexto,
                    timestamp_utc=datetime.fromtimestamp(ts.timestamp(), tz=timezone.utc),
                )
            )
        return eventos
