"""Contratos (puertos) para desacoplar services de implementaciones concretas."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Tuple

import pandas as pd


class IAuthRepository(ABC):
    """Puerto mínimo que requiere AuthService."""

    @abstractmethod
    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Tuple[int, str, str]]:
        pass

    @abstractmethod
    def crear_usuario(self, nombre_usuario: str, contrasena_texto: str) -> bool:
        pass


class IBootstrapRepository(ABC):
    """Puerto para inicialización de esquema y usuario admin."""

    @abstractmethod
    def inicializar_esquema_base_datos(self) -> None:
        pass

    @abstractmethod
    def asegurar_usuario_admin_por_defecto(self) -> None:
        pass


class ITransaccionesDataSource(ABC):
    """
    Fuente operativa de transacciones.
    Implementaciones intercambiables: MySQL, demo, API externa, etc.
    """

    @abstractmethod
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
        pass

    @abstractmethod
    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        pass
