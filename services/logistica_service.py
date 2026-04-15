"""Casos de uso de registro y lectura de transacciones (MySQL o demo)."""

from datetime import date
from typing import Dict

import pandas as pd

from services.audit_service import AuditService
from services.contracts import ITransaccionesDataSource


class LogisticaService:
    """Gestiona operaciones de transacciones con fuentes conmutables por modo."""

    def __init__(
        self,
        fuentes_por_modo: Dict[bool, ITransaccionesDataSource],
        audit_service: AuditService,
    ) -> None:
        """Inicializa servicio de transacciones.

        Args:
            fuentes_por_modo: Mapa ``{usar_demo: datasource}``.
            audit_service: Servicio de auditoría.
        """
        self._fuentes = fuentes_por_modo
        self._audit = audit_service

    def _resolver_fuente(self, usar_demo: bool) -> ITransaccionesDataSource:
        return self._fuentes[usar_demo]

    def registrar_transaccion(
        self,
        usar_demo: bool,
        fecha: date,
        cliente: str,
        tipo_servicio: str,
        descripcion: str,
        origen: str,
        destino: str,
        monto_total: float,
        estado: str,
        metodo_pago: str,
        usuario_registro: str,
    ) -> None:
        """Registra una transacción en el origen correspondiente.

        Args:
            usar_demo: Determina fuente demo o MySQL.
            fecha: Fecha de la transacción.
            cliente: Cliente de la operación.
            tipo_servicio: Tipo de servicio.
            descripcion: Descripción libre.
            origen: Origen logístico.
            destino: Destino logístico.
            monto_total: Monto total.
            estado: Estado operativo.
            metodo_pago: Medio de pago.
            usuario_registro: Usuario que registra.
        """
        self._resolver_fuente(usar_demo).insertar_transaccion(
            fecha,
            cliente,
            tipo_servicio,
            descripcion,
            origen,
            destino,
            monto_total,
            estado,
            metodo_pago,
            usuario_registro,
        )
        self._audit.registrar_evento(
            usar_demo=usar_demo,
            accion="TRANSACCION_CREADA",
            detalle=f"Transacción registrada para cliente '{cliente}'.",
            usuario=usuario_registro or "system",
            severidad="INFO",
            contexto={"monto_total": f"{monto_total:.2f}", "estado": estado},
        )

    def cargar_transacciones_operativas(self, usar_demo: bool) -> pd.DataFrame:
        """Carga transacciones desde la fuente activa.

        Args:
            usar_demo: Determina fuente demo o MySQL.

        Returns:
            DataFrame de transacciones.
        """
        return self._resolver_fuente(usar_demo).cargar_transacciones_dataframe()
