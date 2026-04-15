"""Dataset en memoria cuando MySQL no está disponible (modo demostración)."""

from datetime import date
from typing import Union

import pandas as pd
import streamlit as st


class DemoDataStore:
    """Encapsula el DataFrame de demostración en session_state de Streamlit."""

    _KEY_DF = "demo_transactions_df"

    def inicializar_demostracion_si_ausente(self) -> None:
        """Carga filas de ejemplo una sola vez por sesión."""
        if self._KEY_DF not in st.session_state:
            st.session_state[self._KEY_DF] = pd.DataFrame(
                [
                    {
                        "id_transaccion": 1,
                        "fecha": "2026-03-10",
                        "cliente": "Empresa A",
                        "tipo_servicio": "Fletes Nacionales",
                        "descripcion": "Traslado de mercancia seca",
                        "origen": "San Salvador",
                        "destino": "Santa Ana",
                        "monto_total": 1250.00,
                        "estado": "Completado",
                        "metodo_pago": "Transferencia",
                        "usuario_registro": "admin",
                        "fecha_registro": "2026-03-10 08:10:00",
                    },
                    {
                        "id_transaccion": 2,
                        "fecha": "2026-03-10",
                        "cliente": "Empresa B",
                        "tipo_servicio": "Fletes Internacionales",
                        "descripcion": "Exportacion de repuestos",
                        "origen": "San Salvador",
                        "destino": "Guatemala",
                        "monto_total": 3890.00,
                        "estado": "Completado",
                        "metodo_pago": "Credito",
                        "usuario_registro": "admin",
                        "fecha_registro": "2026-03-10 09:45:00",
                    },
                    {
                        "id_transaccion": 3,
                        "fecha": "2026-03-11",
                        "cliente": "Empresa C",
                        "tipo_servicio": "Almacenaje",
                        "descripcion": "Resguardo de inventario por semana",
                        "origen": "Bodega Central",
                        "destino": "Bodega Central",
                        "monto_total": 780.00,
                        "estado": "Pendiente",
                        "metodo_pago": "Transferencia",
                        "usuario_registro": "analista1",
                        "fecha_registro": "2026-03-11 10:00:00",
                    },
                    {
                        "id_transaccion": 4,
                        "fecha": "2026-03-12",
                        "cliente": "Empresa D",
                        "tipo_servicio": "Distribucion Local",
                        "descripcion": "Entrega en rutas urbanas",
                        "origen": "Soyapango",
                        "destino": "San Miguel",
                        "monto_total": 980.00,
                        "estado": "Completado",
                        "metodo_pago": "Efectivo",
                        "usuario_registro": "analista1",
                        "fecha_registro": "2026-03-12 11:30:00",
                    },
                    {
                        "id_transaccion": 5,
                        "fecha": "2026-03-12",
                        "cliente": "Empresa E",
                        "tipo_servicio": "Gestion Aduanera",
                        "descripcion": "Tramite de importacion consolidada",
                        "origen": "Acajutla",
                        "destino": "San Salvador",
                        "monto_total": 2210.00,
                        "estado": "Pendiente",
                        "metodo_pago": "Deposito",
                        "usuario_registro": "coordinador",
                        "fecha_registro": "2026-03-12 15:25:00",
                    },
                    {
                        "id_transaccion": 6,
                        "fecha": "2026-03-13",
                        "cliente": "Empresa F",
                        "tipo_servicio": "Transporte Refrigerado",
                        "descripcion": "Cadena de frio para lacteos",
                        "origen": "La Libertad",
                        "destino": "Santa Ana",
                        "monto_total": 3120.00,
                        "estado": "Completado",
                        "metodo_pago": "Transferencia",
                        "usuario_registro": "coordinador",
                        "fecha_registro": "2026-03-13 08:05:00",
                    },
                    {
                        "id_transaccion": 7,
                        "fecha": "2026-03-14",
                        "cliente": "Empresa G",
                        "tipo_servicio": "Logistica de Ultima Milla",
                        "descripcion": "Entrega domiciliaria ecommerce",
                        "origen": "Apopa",
                        "destino": "San Salvador",
                        "monto_total": 640.00,
                        "estado": "Completado",
                        "metodo_pago": "Tarjeta",
                        "usuario_registro": "operador2",
                        "fecha_registro": "2026-03-14 09:12:00",
                    },
                    {
                        "id_transaccion": 8,
                        "fecha": "2026-03-15",
                        "cliente": "Empresa H",
                        "tipo_servicio": "Consolidacion de Carga",
                        "descripcion": "Consolidado semanal de pallets",
                        "origen": "Sonsonate",
                        "destino": "San Salvador",
                        "monto_total": 1740.00,
                        "estado": "Pendiente",
                        "metodo_pago": "Credito",
                        "usuario_registro": "operador2",
                        "fecha_registro": "2026-03-15 13:20:00",
                    },
                    {
                        "id_transaccion": 9,
                        "fecha": "2026-03-16",
                        "cliente": "Empresa I",
                        "tipo_servicio": "Seguros de Mercancia",
                        "descripcion": "Poliza para equipo electronico",
                        "origen": "San Salvador",
                        "destino": "San Vicente",
                        "monto_total": 560.00,
                        "estado": "Cancelado",
                        "metodo_pago": "Transferencia",
                        "usuario_registro": "supervisor",
                        "fecha_registro": "2026-03-16 16:50:00",
                    },
                    {
                        "id_transaccion": 10,
                        "fecha": "2026-03-17",
                        "cliente": "Empresa J",
                        "tipo_servicio": "Servicios Express",
                        "descripcion": "Envio urgente de documentos",
                        "origen": "San Miguel",
                        "destino": "San Salvador",
                        "monto_total": 420.00,
                        "estado": "Completado",
                        "metodo_pago": "Efectivo",
                        "usuario_registro": "supervisor",
                        "fecha_registro": "2026-03-17 17:10:00",
                    },
                ]
            )
            df = st.session_state[self._KEY_DF]
            df["fecha"] = pd.to_datetime(df["fecha"])
            df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])

    def insertar_transaccion(
        self,
        fecha: Union[date, pd.Timestamp],
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
        df_demo = st.session_state[self._KEY_DF].copy()
        siguiente_id = int(df_demo["id_transaccion"].max()) + 1 if not df_demo.empty else 1
        nueva_fila = pd.DataFrame(
            [
                {
                    "id_transaccion": siguiente_id,
                    "fecha": pd.to_datetime(fecha),
                    "cliente": cliente,
                    "tipo_servicio": tipo_servicio,
                    "descripcion": descripcion,
                    "origen": origen,
                    "destino": destino,
                    "monto_total": float(monto_total),
                    "estado": estado,
                    "metodo_pago": metodo_pago,
                    "usuario_registro": usuario_registro,
                    "fecha_registro": pd.Timestamp.now(),
                }
            ]
        )
        st.session_state[self._KEY_DF] = pd.concat([df_demo, nueva_fila], ignore_index=True)

    def cargar_transacciones_dataframe(self) -> pd.DataFrame:
        return st.session_state[self._KEY_DF].sort_values(
            by=["fecha", "id_transaccion"]
        ).reset_index(drop=True)
