"""Casos de uso de registro y lectura de transacciones (MySQL o demo)."""

from datetime import date
from typing import Dict

import pandas as pd

from services.contracts import ITransaccionesDataSource


class LogisticaService:
    def __init__(
        self,
        fuentes_por_modo: Dict[bool, ITransaccionesDataSource],
    ) -> None:
        self._fuentes = fuentes_por_modo

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

    def cargar_transacciones_operativas(self, usar_demo: bool) -> pd.DataFrame:
        return self._resolver_fuente(usar_demo).cargar_transacciones_dataframe()
