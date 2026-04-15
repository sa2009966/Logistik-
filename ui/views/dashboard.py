"""Tablero principal: formulario de transacciones, BI, filtros y exportación."""

from datetime import date

import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from mysql.connector import Error

from core.constants import ConstantesNegocio
from services.container import obtener_contenedor
from ui.styles import COLOR_ACCENT, html_skeleton_block


def mostrar_panel_principal() -> None:
    """Orquesta sidebar, pestañas de ingreso y dashboard (solo usuarios autenticados)."""
    contenedor = obtener_contenedor()
    usar_demo = st.session_state.get("use_demo_mode", False)

    with st.sidebar:
        st.markdown(f"**Usuario:** `{contenedor.sesion.obtener_usuario_actual()}`")
        if usar_demo:
            st.warning("Modo demo (datos en memoria).")
        else:
            st.success("MySQL conectado.")
        if st.button("Cerrar sesión", use_container_width=True):
            contenedor.sesion.cerrar_sesion()
            st.rerun()

        st.header("Carga de datos")
        archivo_csv = st.file_uploader(
            "Importar CSV para análisis externo",
            type=["csv"],
            help="Si cargas un CSV válido, se priorizará sobre MySQL/demo para el dashboard.",
        )
    st.session_state["_sidebar_csv"] = archivo_csv

    st.markdown(
        f'<h1 style="color:{COLOR_ACCENT};">Logistik BI · Dashboard</h1>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Panel en tiempo real para registrar transacciones logísticas y analizar indicadores financieros."
    )

    pestaña_ingreso, pestaña_dashboard = st.tabs(["Nueva transacción", "Dashboard BI"])

    with pestaña_ingreso:
        _mostrar_formulario_transaccion(contenedor, usar_demo)

    with pestaña_dashboard:
        _mostrar_panel_bi(contenedor, usar_demo)


def _mostrar_formulario_transaccion(contenedor, usar_demo: bool) -> None:
    """Alta de transacción vía capa de servicios (MySQL o demo)."""
    st.subheader("Formulario de registro operativo")
    usuario_por_defecto = contenedor.sesion.obtener_usuario_actual() or "admin"
    with st.form("form_transaccion_logistik", clear_on_submit=True):
        fecha = st.date_input("Fecha", value=date.today())
        cliente = st.text_input("Cliente")
        tipo_servicio = st.selectbox("Tipo de Servicio", ConstantesNegocio.TIPOS_SERVICIO)
        descripcion = st.text_input("Descripción")
        origen = st.text_input("Origen")
        destino = st.text_input("Destino")
        monto_total = st.number_input("Monto total", min_value=0.0, step=0.01, format="%.2f")
        estado = st.selectbox("Estado", ConstantesNegocio.ESTADOS)
        metodo_pago = st.selectbox("Método de pago", ConstantesNegocio.METODOS_PAGO)
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
            try:
                contenedor.logistica.registrar_transaccion(
                    usar_demo,
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
                st.success(
                    "Transacción registrada (modo demo)."
                    if usar_demo
                    else "Transacción registrada en MySQL."
                )
                st.rerun()
            except Error as err_insert:
                st.error(f"Error al registrar en base de datos: {err_insert}")


def _mostrar_panel_bi(contenedor, usar_demo: bool) -> None:
    """Resuelve fuente de datos y visualización vía DashboardService."""
    st.subheader("Visualización dinámica de operaciones")
    archivo_csv = st.session_state.get("_sidebar_csv")

    placeholder = st.empty()
    placeholder.markdown(
        f'<div class="fade-in-up">{html_skeleton_block()}</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Cargando datos del panel…"):
        df_datos, etiqueta_fuente, error_carga = contenedor.dashboard.construir_dataset_visualizacion(
            usar_demo, archivo_csv
        )
    placeholder.empty()

    if error_carga:
        st.error(error_carga)
        st.stop()
    if archivo_csv is not None and df_datos is not None:
        st.success("CSV cargado. El dashboard usa esta fuente.")

    assert df_datos is not None

    st.caption(f"Fuente activa de datos: **{etiqueta_fuente}**")

    df_datos["fecha"] = pd.to_datetime(df_datos["fecha"], errors="coerce")

    with st.expander("Filtros de análisis", expanded=True):
        st.caption(
            "Puedes colapsar este bloque en pantallas pequeñas para ahorrar espacio. "
            "En escritorio los tres filtros se muestran en columnas; en móvil se apilan."
        )
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

    total_ingresos, servicios_realizados, monto_promedio = contenedor.dashboard.calcular_indicadores(
        df_filtrado
    )
    alertas = contenedor.dashboard.evaluar_alertas_kpi(
        total_ingresos=total_ingresos,
        servicios_realizados=servicios_realizados,
        monto_promedio=monto_promedio,
    )

    annotated_text(
        "Total ingresos: ",
        (f"${total_ingresos:,.2f}", "SUM(monto_total)", COLOR_ACCENT),
    )

    k1, k2, k3 = st.columns(3)
    k1.metric("Total ingresos", f"${total_ingresos:,.2f}")
    k2.metric("Servicios realizados", f"{servicios_realizados}")
    k3.metric("Monto promedio", f"${monto_promedio:,.2f}")

    for alerta in alertas:
        if alerta.nivel == "error":
            st.error(f"{alerta.titulo}: {alerta.mensaje}")
        elif alerta.nivel == "warning":
            st.warning(f"{alerta.titulo}: {alerta.mensaje}")
        else:
            st.success(f"{alerta.titulo}: {alerta.mensaje}")

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
            contenedor.graficos.render("linea_tendencia_ingresos", df_linea),
            use_container_width=True,
        )
        c2.plotly_chart(
            contenedor.graficos.render("barras_ingresos_servicio", df_servicio),
            use_container_width=True,
        )
        c3.plotly_chart(
            contenedor.graficos.render("pastel_participacion_estado", df_estado),
            use_container_width=True,
        )

    st.dataframe(df_filtrado, use_container_width=True)

    st.markdown("### Centro de reportes")
    csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
    c_csv, c_xlsx = st.columns(2)
    c_csv.download_button(
        label="Descargar reporte CSV",
        data=csv_bytes,
        file_name="reporte_logistik.csv",
        mime="text/csv",
        use_container_width=True,
    )
    try:
        payload_excel = contenedor.reportes.preparar_excel(
            df_reporte=df_filtrado,
            nombre_base="reporte_logistik",
        )
        descargado_excel = c_xlsx.download_button(
            label="Descargar reporte Excel",
            data=payload_excel.contenido,
            file_name=payload_excel.nombre_archivo,
            mime=payload_excel.mime_type,
            use_container_width=True,
        )
        if descargado_excel:
            contenedor.reportes.registrar_descarga_excel(
                usar_demo=usar_demo,
                usuario=contenedor.sesion.obtener_usuario_actual() or "system",
                filas=len(df_filtrado),
                nombre_archivo=payload_excel.nombre_archivo,
            )
    except ValueError as export_validation_error:
        c_xlsx.info(str(export_validation_error))
    except RuntimeError as export_runtime_error:
        c_xlsx.warning(str(export_runtime_error))
    except Exception as export_unknown_error:
        c_xlsx.error(f"No se pudo preparar el reporte Excel: {export_unknown_error}")
