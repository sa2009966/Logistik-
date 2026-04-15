"""Implementaciones de ITransaccionesDataSource para LSP (Demo/MySQL)."""

from datetime import date
from typing import TYPE_CHECKING

import pandas as pd

from services.contracts import ITransaccionesDataSource

if TYPE_CHECKING:
    from services.demo_data import DemoDataStore


class MysqlTransaccionesDataSource(ITransaccionesDataSource):
    """Adaptador de repositorio SQL al puerto de transacciones."""

    def __init__(self, repositorio: ITransaccionesDataSource) -> None:
        self._repo = repositorio

    def insertar_transaccion(
        self,
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
        self._repo.insertar_transaccion(
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

    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        return self._repo.cargar_transacciones_dataframe()


class DemoTransaccionesDataSource(ITransaccionesDataSource):
    """Adaptador de store demo al puerto de transacciones."""

    def __init__(self, demo_store: "DemoDataStore") -> None:
        self._demo = demo_store

    def insertar_transaccion(
        self,
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
        self._demo.insertar_transaccion(
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

    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        return self._demo.cargar_transacciones_dataframe()
