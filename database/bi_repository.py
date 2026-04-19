"""Repositorio BI dinámico: consultas SQL filtradas para análisis en tiempo real."""

from typing import TYPE_CHECKING

import pandas as pd

from core.constants import ConstantesNegocio
from services.contracts import IBiDinamicoRepository
from services.models import FiltrosBi

if TYPE_CHECKING:
    from database.connection import GestorConexionMySQL


class MysqlBiDinamicoRepository(IBiDinamicoRepository):
    """Ejecuta consultas SQL con filtros de fecha, estado y tipo de servicio."""

    def __init__(self, gestor_mysql: "GestorConexionMySQL") -> None:
        self._gestor = gestor_mysql

    def cargar_transacciones_filtradas(self, filtros: FiltrosBi) -> pd.DataFrame:
        """Devuelve solo las filas que cumplen el filtro, evaluado en el servidor MySQL."""
        conn = self._gestor.obtener()
        tbl_tx = ConstantesNegocio.DB_TABLE_TRANSACTIONS

        # Placeholders dinámicos para las listas IN (evita SQL injection)
        estados_ph = ", ".join(["%s"] * len(filtros.estados)) if filtros.estados else "''"
        servicios_ph = (
            ", ".join(["%s"] * len(filtros.tipos_servicio)) if filtros.tipos_servicio else "''"
        )

        consulta = f"""
            SELECT id_transaccion, fecha, cliente, tipo_servicio, descripcion, origen, destino,
                   monto_total, estado, metodo_pago, usuario_registro, fecha_registro
            FROM {tbl_tx}
            WHERE fecha BETWEEN %s AND %s
              AND estado IN ({estados_ph})
              AND tipo_servicio IN ({servicios_ph})
            ORDER BY fecha ASC, id_transaccion ASC
        """
        params = (
            [filtros.fecha_inicio, filtros.fecha_fin]
            + list(filtros.estados)
            + list(filtros.tipos_servicio)
        )
        return pd.read_sql(consulta, conn, params=params)
