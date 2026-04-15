"""Lógica de alertas de salud KPI desacoplada de la UI."""

from services.models import KpiAlert


class AlertManager:
    """Evalúa umbrales de KPI y retorna estados de salud consumibles por UI."""

    def __init__(
        self,
        umbral_ticket_bajo: float = 700.0,
        umbral_ticket_alto: float = 3000.0,
        umbral_servicios_bajos: int = 3,
        umbral_ingresos_bajos: float = 1500.0,
    ) -> None:
        self._ticket_bajo = umbral_ticket_bajo
        self._ticket_alto = umbral_ticket_alto
        self._servicios_bajos = umbral_servicios_bajos
        self._ingresos_bajos = umbral_ingresos_bajos

    def evaluar_kpis(
        self,
        total_ingresos: float,
        servicios_realizados: int,
        monto_promedio: float,
    ) -> list[KpiAlert]:
        """Calcula alertas de negocio en base a métricas agregadas.

        Args:
            total_ingresos: Suma de ingresos filtrados.
            servicios_realizados: Número de operaciones en el rango.
            monto_promedio: Ticket promedio calculado.

        Returns:
            Lista de alertas con nivel ``success``, ``warning`` o ``error``.
        """
        alertas: list[KpiAlert] = []

        if servicios_realizados <= 0:
            alertas.append(
                KpiAlert(
                    clave="sin_datos",
                    nivel="warning",
                    titulo="Sin operaciones",
                    mensaje="No hay transacciones para el rango y filtros seleccionados.",
                )
            )
            return alertas

        if total_ingresos < self._ingresos_bajos:
            alertas.append(
                KpiAlert(
                    clave="ingresos_bajos",
                    nivel="warning",
                    titulo="Ingresos por debajo del objetivo",
                    mensaje=(
                        f"Los ingresos (${total_ingresos:,.2f}) están debajo del umbral "
                        f"de ${self._ingresos_bajos:,.2f}."
                    ),
                )
            )
        else:
            alertas.append(
                KpiAlert(
                    clave="ingresos_saludables",
                    nivel="success",
                    titulo="Ingresos saludables",
                    mensaje="El nivel de ingresos se mantiene dentro del rango esperado.",
                )
            )

        if servicios_realizados < self._servicios_bajos:
            alertas.append(
                KpiAlert(
                    clave="volumen_bajo",
                    nivel="warning",
                    titulo="Volumen operativo bajo",
                    mensaje=(
                        f"Solo se registran {servicios_realizados} servicios; revisar captación o carga."
                    ),
                )
            )

        if monto_promedio < self._ticket_bajo:
            alertas.append(
                KpiAlert(
                    clave="ticket_bajo",
                    nivel="warning",
                    titulo="Ticket promedio bajo",
                    mensaje=(
                        f"El ticket promedio (${monto_promedio:,.2f}) está por debajo de "
                        f"${self._ticket_bajo:,.2f}."
                    ),
                )
            )
        elif monto_promedio > self._ticket_alto:
            alertas.append(
                KpiAlert(
                    clave="ticket_alto",
                    nivel="success",
                    titulo="Ticket promedio alto",
                    mensaje=(
                        f"Excelente nivel de ticket promedio (${monto_promedio:,.2f})."
                    ),
                )
            )

        return alertas
