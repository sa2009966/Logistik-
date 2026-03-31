"""Tablero principal: formulario de transacciones, BI, filtros y exportación."""

from datetime import date

import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from mysql.connector import Error

from core import auth
from core.auth import obtener_usuario_actual
from core.constants import ESTADOS, METODOS_PAGO, TIPOS_SERVICIO
from database import repository
from services import analytics, demo_data
from ui.charts import (
    grafico_barras_ingresos_servicio,
    grafico_linea_tendencia_ingresos,
    grafico_pastel_participacion_estado,
)
from ui.styles import CYBER_CYAN


def mostrar_panel_principal() -> None:
    """Orquesta sidebar, pestañas de ingreso y dashboard (solo usuarios autenticados)."""
    usar_demo = st.session_state.get("use_demo_mode", False)

    with st.sidebar:
        st.markdown(f"**Usuario:** `{obtener_usuario_actual()}`")
        if usar_demo:
            st.warning("Modo demo (datos en memoria).")
        else:
            st.success("MySQL conectado.")
        if st.button("Cerrar sesión", use_container_width=True):
            auth.cerrar_sesion()
            st.rerun()

        st.header("Carga de datos")
        archivo_csv = st.file_uploader(
            "Importar CSV para análisis externo",
            type=["csv"],
            help="Si cargas un CSV válido, se priorizará sobre MySQL/demo para el dashboard.",
        )
    st.session_state["_sidebar_csv"] = archivo_csv

    st.markdown(
        f'<h1 style="color:{CYBER_CYAN};">Logistik BI · Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Panel en tiempo real para registrar transacciones logísticas y analizar indicadores financieros."
    )

    pestaña_ingreso, pestaña_dashboard = st.tabs(["Nueva transacción", "Dashboard BI"])

    with pestaña_ingreso:
        _mostrar_formulario_transaccion(usar_demo)

    with pestaña_dashboard:
        _mostrar_panel_bi(usar_demo)


def _mostrar_formulario_transaccion(usar_demo: bool) -> None:
    """Alta de transacción en MySQL o en memoria según el modo activo."""
    st.subheader("Formulario de registro operativo")
    usuario_por_defecto = obtener_usuario_actual() or "admin"
    with st.form("form_transaccion_logistik", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=date.today())
        cliente = st.text_input("Cliente")
        tipo_servicio = st.selectbox("Tipo de Servicio", TIPOS_SERVICIO)
        descripcion = st.text_input("Descripción")
        origen = st.text_input("Origen")
        destino = st.text_input("Destino")
        monto_total = st.number_input("Monto total", min_value=0.0, step=0.01, format="%.2f")
        estado = st.selectbox("Estado", ESTADOS)
        metodo_pago = st.selectbox("Método de pago", METODOS_PAGO)
        usuario_registro = st.text_input("Usuario registro", value=usuario_por_defecto)
        enviar = st.form_submit_button("Registrar transacción")

    if enviar:
        if (
            not cliente.strip()
            or not origen.strip()
            or not destino.strip()
            or not descripcion.strip()
            or not usuario_registro.strip()
        ):
            st.error("Completa todos los campos de texto requeridos.")
        elif monto_total <= 0:
            st.error("El monto total debe ser mayor que cero.")
        else:
            if usar_demo:
                demo_data.insertar_transaccion_demostracion(
                    fecha,
                    cliente.strip(),
                    tipo_servicio,
                    descripcion.strip(),
                    origen.strip(),
                    destino.strip(),
                    monto_total,
                    estado,
                    metodo_pago,
                    usuario_registro.strip(),
                )
                st.success("Transacción registrada (modo demo).")
                st.rerun()
            else:
                try:
                    repository.insertar_transaccion(
                        fecha,
                        cliente.strip(),
                        tipo_servicio,
                        descripcion.strip(),
                        origen.strip(),
                        destino.strip(),
                        monto_total,
                        estado,
                        metodo_pago,
                        usuario_registro.strip(),
                    )
                    st.success("Transacción registrada en MySQL.")
                    st.rerun()
                except Error as err_insert:
                    st.error(f"Error al registrar en base de datos: {err_insert}")


def _mostrar_panel_bi(usar_demo: bool) -> None:
    """Carga fuente de datos, aplica filtros, KPIs, gráficos y descarga CSV."""
    st.subheader("Visualización dinámica de operaciones")
    archivo_csv = st.session_state.get("_sidebar_csv")

    etiqueta_fuente = ""
    if archivo_csv is not None:
        try:
            df_csv = pd.read_csv(archivo_csv)
            columnas_faltantes = analytics.validar_columnas_csv(df_csv)
            if columnas_faltantes:
                st.error(
                    "El archivo CSV no tiene la estructura necesaria. "
                    f"Faltan: {', '.join(columnas_faltantes)}. "
                    "Columnas mínimas: monto_total, estado, tipo_servicio."
                )
                st.stop()
            df_datos = analytics.preparar_dataframe_csv(df_csv)
            etiqueta_fuente = "CSV EXTERNO"
            st.success("CSV cargado. El dashboard usa esta fuente.")
        except Exception as err_csv:
            st.error(f"No se pudo procesar el CSV: {err_csv}")
            st.stop()
    elif usar_demo:
        df_datos = demo_data.cargar_transacciones_demostracion_dataframe()
        etiqueta_fuente = "DEMO OFFLINE"
    else:
        try:
            df_datos = repository.cargar_transacciones_dataframe()
            etiqueta_fuente = "MYSQL ONLINE"
        except Error as err_lectura:
            st.error(f"Error al leer transacciones de MySQL: {err_lectura}")
            st.stop()

    st.caption(f"Fuente activa de datos: **{etiqueta_fuente}**")

    df_datos["fecha"] = pd.to_datetime(df_datos["fecha"], errors="coerce")

    st.markdown("### Filtros de análisis")
    f1, f2, f3 = st.columns(3)
    estados_disponibles = sorted(df_datos["estado"].dropna().astype(str).unique().tolist())
    estados_sel = f1.multiselect(
        "Filtrar por estado", estados_disponibles, default=estados_disponibles
    )
    servicios_disponibles = sorted(
        df_datos["tipo_servicio"].dropna().astype(str).unique().tolist()
    )
    servicios_sel = f2.multiselect(
        "Filtrar por tipo de servicio",
        servicios_disponibles,
        default=servicios_disponibles,
    )
    fechas_validas = df_datos["fecha"].dropna()
    if fechas_validas.empty:
        fecha_min = date.today()
        fecha_max = date.today()
    else:
        fecha_min = fechas_validas.min().date()
        fecha_max = fechas_validas.max().date()
    fecha_rango = f3.date_input(
        "Rango de fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    if isinstance(fecha_rango, tuple) and len(fecha_rango) == 2:
        fecha_inicio, fecha_fin = fecha_rango
    else:
        fecha_inicio, fecha_fin = fecha_min, fecha_max

    df_filtrado = df_datos.copy()
    df_filtrado = df_filtrado[df_filtrado["estado"].astype(str).isin(estados_sel)]
    df_filtrado = df_filtrado[df_filtrado["tipo_servicio"].astype(str).isin(servicios_sel)]
    df_filtrado = df_filtrado[
        (df_filtrado["fecha"].dt.date >= fecha_inicio)
        & (df_filtrado["fecha"].dt.date <= fecha_fin)
    ]

    total_ingresos, servicios_realizados, monto_promedio = analytics.calcular_indicadores(
        df_filtrado
    )

    annotated_text(
        "Total ingresos: ",
        (f"${total_ingresos:,.2f}", "SUM(monto_total)", CYBER_CYAN),
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Total ingresos", f"${total_ingresos:,.2f}")
    k2.metric("Servicios realizados", f"{servicios_realizados}")
    k3.metric("Monto promedio", f"${monto_promedio:,.2f}")

    st.markdown("### Insights estadísticos")
    insights_stats = df_filtrado[["monto_total"]].describe().T
    insights_view = insights_stats[["mean", "min", "max"]].rename(
        columns={"mean": "Promedio", "min": "Mínimo", "max": "Máximo"}
    )
    st.dataframe(insights_view, use_container_width=True)

    if df_filtrado.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        df_linea = (
            df_filtrado.groupby(df_filtrado["fecha"].dt.date)["monto_total"].sum().reset_index()
        )
        df_linea.columns = ["fecha", "monto_total"]
        df_servicio = df_filtrado.groupby("tipo_servicio")["monto_total"].sum().reset_index()
        df_estado = df_filtrado.groupby("estado")["monto_total"].sum().reset_index()

        c1, c2, c3 = st.columns(3)
        c1.plotly_chart(
            grafico_linea_tendencia_ingresos(df_linea), use_container_width=True
        )
        c2.plotly_chart(
            grafico_barras_ingresos_servicio(df_servicio), use_container_width=True
        )
        c3.plotly_chart(
            grafico_pastel_participacion_estado(df_estado), use_container_width=True
        )

    st.dataframe(df_filtrado, use_container_width=True)

    st.markdown("### Centro de reportes")
    csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar reporte CSV",
        data=csv_bytes,
        file_name="reporte_logistik.csv",
        mime="text/csv",
    )
