"""Casos de uso de BI dinámico: consultas filtradas y cálculo de KPIs en tiempo real."""

from typing import TYPE_CHECKING, Dict

from services.contracts import IBiDinamicoRepository
from services.models import BiSnapshot, FiltrosBi

if TYPE_CHECKING:
    from services.analytics import AnalyticsService
    from services.audit_service import AuditService


class BiDinamicoService:
    """Orquesta la consulta filtrada de datos y el cálculo de KPIs.

    Sigue el patrón Dict-strategy para conmutar entre fuente MySQL y demo
    sin if/else en la lógica de negocio.
    """

    def __init__(
        self,
        repos_por_modo: Dict[bool, IBiDinamicoRepository],
        analytics: "AnalyticsService",
        audit_service: "AuditService",
    ) -> None:
        """Inicializa el servicio BI dinámico.

        Args:
            repos_por_modo: Mapa ``{usar_demo: repositorio}`` para MySQL y demo.
            analytics: Servicio de cálculo de KPIs.
            audit_service: Servicio de trazabilidad.
        """
        self._repos = repos_por_modo
        self._analytics = analytics
        self._audit = audit_service

    def _repo(self, usar_demo: bool) -> IBiDinamicoRepository:
        return self._repos[usar_demo]

    def calcular_estadisticas(
        self,
        usar_demo: bool,
        filtros: FiltrosBi,
        usuario: str,
    ) -> BiSnapshot:
        """Consulta datos filtrados y calcula KPIs en una sola operación.

        Args:
            usar_demo: ``True`` para fuente en memoria; ``False`` para MySQL.
            filtros: Criterios de búsqueda (fechas, estados, tipos de servicio).
            usuario: Usuario que realiza la consulta (para auditoría).

        Returns:
            ``BiSnapshot`` con el DataFrame filtrado y los KPIs calculados.

        Raises:
            Exception: Si la fuente de datos falla (propagado para que la UI maneje el fallback).
        """
        df = self._repo(usar_demo).cargar_transacciones_filtradas(filtros)

        total, servicios, promedio = self._analytics.calcular_indicadores(df)

        self._audit.registrar_evento(
            usar_demo=usar_demo,
            accion="BI_CONSULTA",
            detalle=(
                f"Consulta BI filtrada: {filtros.fecha_inicio} → {filtros.fecha_fin}, "
                f"{len(filtros.estados)} estados, {len(filtros.tipos_servicio)} servicios. "
                f"Filas devueltas: {len(df)}."
            ),
            usuario=usuario,
            contexto={
                "fecha_inicio": str(filtros.fecha_inicio),
                "fecha_fin": str(filtros.fecha_fin),
                "filas": str(len(df)),
            },
        )

        return BiSnapshot(
            df_filtrado=df,
            total_ingresos=total,
            servicios_realizados=servicios,
            monto_promedio=promedio,
        )
