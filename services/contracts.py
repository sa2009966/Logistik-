"""Contratos (puertos) para desacoplar services de implementaciones concretas."""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Tuple

import pandas as pd

from services.models import AuditEvent, ReportPayload


class IAuthRepository(ABC):
    """Puerto mínimo requerido por la lógica de autenticación."""

    @abstractmethod
    def obtener_usuario_por_nombre(self, nombre_usuario: str) -> Optional[Tuple[int, str, str]]:
        """Obtiene usuario por nombre.

        Args:
            nombre_usuario: Nombre del usuario en texto plano.

        Returns:
            Tupla (id_usuario, nombre_usuario, password_hash) o ``None`` si no existe.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """

    @abstractmethod
    def crear_usuario(self, nombre_usuario: str, contrasena_texto: str) -> bool:
        """Crea un usuario nuevo.

        Args:
            nombre_usuario: Nombre único deseado.
            contrasena_texto: Contraseña en texto plano.

        Returns:
            ``True`` si se crea correctamente; ``False`` si el usuario ya existe.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """


class IBootstrapRepository(ABC):
    """Puerto para inicialización de esquema y datos base."""

    @abstractmethod
    def inicializar_esquema_base_datos(self) -> None:
        """Inicializa esquema principal de negocio.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """

    @abstractmethod
    def asegurar_usuario_admin_por_defecto(self) -> None:
        """Garantiza que exista usuario administrador inicial.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """


class ITransaccionesDataSource(ABC):
    """Fuente operativa de transacciones intercambiable (MySQL, demo, API)."""

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
        """Inserta una transacción operativa.

        Args:
            fecha: Fecha de la transacción.
            cliente: Nombre del cliente.
            tipo_servicio: Tipo de servicio logístico.
            descripcion: Descripción libre de la operación.
            origen: Origen logístico.
            destino: Destino logístico.
            monto_total: Monto monetario total.
            estado: Estado de la operación.
            metodo_pago: Método de pago.
            usuario_registro: Usuario que registra la transacción.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """

    @abstractmethod
    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        """Recupera transacciones en formato tabular.

        Returns:
            DataFrame con la información operativa.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """


class IAuditRepository(ABC):
    """Puerto de persistencia para auditoría y trazabilidad."""

    @abstractmethod
    def inicializar_almacen_auditoria(self) -> None:
        """Prepara el almacenamiento de auditoría.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """

    @abstractmethod
    def registrar_evento(self, evento: AuditEvent) -> None:
        """Registra un evento de auditoría.

        Args:
            evento: Evento enriquecido de auditoría.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """

    @abstractmethod
    def listar_eventos_recientes(self, limite: int = 50) -> list[AuditEvent]:
        """Lista eventos recientes.

        Args:
            limite: Máximo de eventos a devolver.

        Returns:
            Lista ordenada del más reciente al más antiguo.

        Raises:
            Exception: Error de infraestructura/persistencia.
        """


class IReportExporter(ABC):
    """Puerto para exportación de reportes en distintos formatos."""

    @abstractmethod
    def exportar(self, df_reporte: pd.DataFrame, nombre_base: str) -> ReportPayload:
        """Exporta un DataFrame a un artefacto descargable.

        Args:
            df_reporte: Dataset a exportar.
            nombre_base: Nombre base sugerido para el archivo.

        Returns:
            Objeto con contenido en bytes, nombre final y mime-type.

        Raises:
            ValueError: Si el DataFrame es inválido o no exportable.
            RuntimeError: Si falla la serialización del formato.
        """
