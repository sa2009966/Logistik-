"""Tablero principal: formulario de transacciones, BI dinámico, administración y exportación."""

from datetime import date
from typing import Optional

import pandas as pd
import streamlit as st
from annotated_text import annotated_text
from mysql.connector import Error

from core.constants import ConstantesNegocio
from services.container import obtener_contenedor
from services.models import FiltrosBi, MapeoColumnas
from ui.styles import COLOR_ACCENT, html_skeleton_block

# Claves de session_state para el mapper CSV
_KEY_CSV_SIG = "_csv_mapper_sig"           # firma del archivo activo (nombre + tamaño)
_KEY_CSV_RAW = "_csv_mapper_raw_df"        # DataFrame crudo cacheado
_KEY_CSV_MAPEADO = "_csv_mapper_df_final"  # DataFrame ya mapeado y preparado
_KEY_CSV_ETIQUETA = "_csv_mapper_etiqueta" # etiqueta de fuente para el mapper confirmado


def mostrar_panel_principal() -> None:
    """Orquesta sidebar, pestañas de ingreso, BI y administración (solo usuarios autenticados)."""
    contenedor = obtener_contenedor()
    usar_demo = st.session_state.get("use_demo_mode", False)

    usuario_actual = contenedor.sesion.obtener_usuario_actual()

    # Determinar si el usuario tiene rol admin para mostrar la pestaña de administración.
    # En modo demo usamos los usuarios del repo en memoria; en MySQL los de la BD.
    try:
        usuarios = contenedor.admin.listar_usuarios(usar_demo)
        info_usuario = next((u for u in usuarios if u.nombre_usuario == usuario_actual), None)
        es_admin = info_usuario is not None and info_usuario.rol == "admin"
    except Exception:
        # Si falla la consulta de roles, sólo el usuario literal "admin" accede al panel
        es_admin = usuario_actual == "admin"

    with st.sidebar:
        st.markdown(f"**Usuario:** `{usuario_actual}`")
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

    pestañas = ["Nueva transacción", "Dashboard BI"]
    if es_admin:
        pestañas.append("Administración")

    tabs = st.tabs(pestañas)

    with tabs[0]:
        _mostrar_formulario_transaccion(contenedor, usar_demo)

    with tabs[1]:
        _mostrar_panel_bi(contenedor, usar_demo, archivo_csv)

    if es_admin:
        with tabs[2]:
            from ui.views.admin import mostrar_panel_admin
            mostrar_panel_admin()


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


def _mostrar_panel_bi(contenedor, usar_demo: bool, archivo_csv) -> None:
    """Resuelve fuente de datos y visualización vía DashboardService / BiDinamicoService."""
    st.subheader("Visualización dinámica de operaciones")

    # ------------------------------------------------------------------ #
    # Fuente CSV externa — con mapper dinámico si las columnas no coinciden
    # ------------------------------------------------------------------ #
    if archivo_csv is not None:
        df_datos, etiqueta_fuente = _resolver_csv(contenedor, usar_demo, archivo_csv)
        if df_datos is None:
            # El mapper está activo o hubo un error irrecuperable; ya se renderizó en _resolver_csv
            return

        st.success("CSV cargado. El dashboard usa esta fuente.")
        st.caption(f"Fuente activa de datos: **{etiqueta_fuente}**")
        df_datos["fecha"] = pd.to_datetime(df_datos["fecha"], errors="coerce")
        _renderizar_bi_con_dataframe(contenedor, usar_demo, df_datos)
        return

    # ------------------------------------------------------------------ #
    # Filtros de BI dinámico (construye FiltrosBi antes de la consulta)   #
    # ------------------------------------------------------------------ #
    st.caption(
        f"Fuente activa: **{'DEMO OFFLINE' if usar_demo else 'MYSQL ONLINE'}**"
    )

    # Carga rápida del dataset completo sólo para obtener rangos de filtros
    with st.spinner("Preparando filtros…"):
        try:
            df_meta = contenedor.logistica.cargar_transacciones_operativas(usar_demo)
        except Exception:
            df_meta = pd.DataFrame()

    df_meta["fecha"] = pd.to_datetime(df_meta.get("fecha", pd.Series(dtype="datetime64[ns]")), errors="coerce")
    fechas_validas = df_meta["fecha"].dropna() if not df_meta.empty else pd.Series(dtype="datetime64[ns]")

    if fechas_validas.empty:
        fecha_min = date.today()
        fecha_max = date.today()
    else:
        fecha_min = fechas_validas.min().date()
        fecha_max = fechas_validas.max().date()

    estados_disponibles = (
        sorted(df_meta["estado"].dropna().astype(str).unique().tolist())
        if not df_meta.empty
        else ConstantesNegocio.ESTADOS
    )
    servicios_disponibles = (
        sorted(df_meta["tipo_servicio"].dropna().astype(str).unique().tolist())
        if not df_meta.empty
        else ConstantesNegocio.TIPOS_SERVICIO
    )

    with st.expander("Filtros de análisis", expanded=True):
        st.caption(
            "Los filtros se envían directamente a la capa de datos. "
            "En MySQL se traduce a una consulta SQL con WHERE; en modo demo filtra en memoria."
        )
        f1, f2, f3 = st.columns(3)
        estados_sel = f1.multiselect(
            "Filtrar por estado", estados_disponibles, default=estados_disponibles
        )
        servicios_sel = f2.multiselect(
            "Filtrar por tipo de servicio",
            servicios_disponibles,
            default=servicios_disponibles,
        )
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

    filtros = FiltrosBi(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estados=estados_sel or estados_disponibles,
        tipos_servicio=servicios_sel or servicios_disponibles,
    )

    # ------------------------------------------------------------------ #
    # Consulta filtrada vía BiDinamicoService                             #
    # ------------------------------------------------------------------ #
    placeholder = st.empty()
    placeholder.markdown(
        f'<div class="fade-in-up">{html_skeleton_block()}</div>',
        unsafe_allow_html=True,
    )
    with st.spinner("Calculando estadísticas…"):
        try:
            snapshot = contenedor.bi_dinamico.calcular_estadisticas(
                usar_demo=usar_demo,
                filtros=filtros,
                usuario=contenedor.sesion.obtener_usuario_actual() or "dashboard",
            )
        except Exception as e:
            placeholder.empty()
            st.error(f"Error al consultar datos: {e}")
            st.stop()
    placeholder.empty()

    _renderizar_bi_con_snapshot(contenedor, usar_demo, snapshot)


def _firma_archivo(archivo_csv) -> str:
    """Genera una firma estable a partir del nombre y tamaño del archivo subido."""
    return f"{archivo_csv.name}::{archivo_csv.size}"


def _resolver_csv(
    contenedor, usar_demo: bool, archivo_csv
) -> tuple[Optional[pd.DataFrame], str]:
    """Gestiona la carga del CSV con mapper dinámico.

    Devuelve ``(DataFrame preparado, etiqueta)`` si el CSV está listo para usar,
    o ``(None, "")`` si el mapper está mostrándose (la UI ya fue renderizada).

    La firma del archivo se usa para resetear el estado cuando el usuario sube
    un archivo diferente, evitando que un mapeo anterior contamine el nuevo CSV.
    """
    firma = _firma_archivo(archivo_csv)

    # Si el archivo cambió, limpiar estado previo del mapper
    if st.session_state.get(_KEY_CSV_SIG) != firma:
        for key in (_KEY_CSV_RAW, _KEY_CSV_MAPEADO, _KEY_CSV_ETIQUETA):
            st.session_state.pop(key, None)
        st.session_state[_KEY_CSV_SIG] = firma

    # Si ya tenemos un DataFrame mapeado confirmado, devolvemos directamente
    if _KEY_CSV_MAPEADO in st.session_state:
        return st.session_state[_KEY_CSV_MAPEADO], st.session_state[_KEY_CSV_ETIQUETA]

    # Cargar el CSV crudo (una sola vez por archivo)
    if _KEY_CSV_RAW not in st.session_state:
        try:
            st.session_state[_KEY_CSV_RAW] = contenedor.csv_loader.cargar_csv(archivo_csv)
        except Exception as e:
            st.error(f"No se pudo leer el archivo CSV: {e}")
            return None, ""

    df_raw: pd.DataFrame = st.session_state[_KEY_CSV_RAW]

    # Validar columnas
    faltantes = contenedor.csv_loader.validar_columnas_csv(df_raw)

    if not faltantes:
        # Todas las columnas requeridas están presentes → flujo normal
        df_ok, etiqueta, error = contenedor.dashboard.construir_dataset_visualizacion(
            usar_demo, archivo_csv
        )
        if error:
            st.error(error)
            return None, ""
        return df_ok, etiqueta

    # Columnas faltantes → mostrar mapper
    _mostrar_mapper_csv(contenedor, usar_demo, df_raw, faltantes)
    return None, ""


def _mostrar_mapper_csv(
    contenedor, usar_demo: bool, df_raw: pd.DataFrame, faltantes: list
) -> None:
    """Renderiza la UI del mapper de columnas y persiste el resultado en session_state.

    El mapper muestra un selectbox por cada columna requerida que no se encontró
    en el CSV. Cuando el usuario confirma, aplica el mapeo a través de
    ``DashboardService.aplicar_mapeo_y_preparar()`` y almacena el resultado.
    """
    columnas_csv = list(df_raw.columns)

    st.warning(
        f"El archivo CSV no contiene las columnas requeridas: "
        f"**{', '.join(faltantes)}**. "
        "Selecciona qué columna de tu archivo corresponde a cada campo del sistema."
    )

    with st.expander("Mapeo de columnas", expanded=True):
        st.caption(
            "Selecciona la columna de tu CSV que equivale a cada campo requerido. "
            "Las columnas que ya tienen el nombre correcto se omiten automáticamente."
        )

        col_izq, col_der = st.columns(2)

        col_izq.markdown("**Columnas detectadas en tu CSV:**")
        col_izq.dataframe(
            pd.DataFrame({"Columna": columnas_csv, "Ejemplo": [
                str(df_raw[c].iloc[0]) if not df_raw.empty else "—"
                for c in columnas_csv
            ]}),
            use_container_width=True,
            hide_index=True,
        )

        col_der.markdown("**Asignar columnas requeridas:**")

        opciones = ["— no asignar —"] + columnas_csv

        def _selectbox_col(campo: str, key_suffix: str) -> str:
            """Devuelve la columna seleccionada, o el nombre canónico si ya existe."""
            if campo not in faltantes:
                return campo  # ya existe con el nombre correcto
            return col_der.selectbox(
                f"`{campo}` ← columna de tu CSV",
                opciones,
                key=f"_csv_map_{key_suffix}",
                help=f"Elige qué columna de tu archivo contiene los datos de '{campo}'.",
            )

        sel_monto = _selectbox_col("monto_total", "monto_total")
        sel_estado = _selectbox_col("estado", "estado")
        sel_servicio = _selectbox_col("tipo_servicio", "tipo_servicio")

        mapeo_valido = all(
            sel not in ("— no asignar —", "")
            for campo, sel in [
                ("monto_total", sel_monto),
                ("estado", sel_estado),
                ("tipo_servicio", sel_servicio),
            ]
            if campo in faltantes
        )

        if not mapeo_valido:
            col_der.warning("Asigna todas las columnas requeridas antes de continuar.")

        aplicar = col_der.button(
            "Aplicar mapeo y cargar datos",
            disabled=not mapeo_valido,
            use_container_width=True,
            type="primary",
        )

    if aplicar and mapeo_valido:
        mapeo = MapeoColumnas(
            monto_total=sel_monto if sel_monto != "— no asignar —" else "monto_total",
            estado=sel_estado if sel_estado != "— no asignar —" else "estado",
            tipo_servicio=sel_servicio if sel_servicio != "— no asignar —" else "tipo_servicio",
        )
        df_final, etiqueta, error = contenedor.dashboard.aplicar_mapeo_y_preparar(
            df_raw, mapeo, usar_demo
        )
        if error:
            st.error(error)
            return
        st.session_state[_KEY_CSV_MAPEADO] = df_final
        st.session_state[_KEY_CSV_ETIQUETA] = etiqueta
        st.rerun()


def _renderizar_bi_con_dataframe(contenedor, usar_demo: bool, df_datos: pd.DataFrame) -> None:
    """Renderiza el panel BI a partir de un DataFrame ya cargado (fuente CSV)."""
    with st.expander("Filtros de análisis", expanded=True):
        f1, f2, f3 = st.columns(3)
        estados_disponibles = sorted(df_datos["estado"].dropna().astype(str).unique().tolist())
        estados_sel = f1.multiselect(
            "Filtrar por estado", estados_disponibles, default=estados_disponibles
        )
        servicios_disponibles = sorted(
            df_datos["tipo_servicio"].dropna().astype(str).unique().tolist()
        )
        servicios_sel = f2.multiselect(
            "Filtrar por tipo de servicio", servicios_disponibles, default=servicios_disponibles
        )
        fechas_validas = df_datos["fecha"].dropna()
        fecha_min = fechas_validas.min().date() if not fechas_validas.empty else date.today()
        fecha_max = fechas_validas.max().date() if not fechas_validas.empty else date.today()
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
    alertas = contenedor.dashboard.evaluar_alertas_kpi(total_ingresos, servicios_realizados, monto_promedio)

    _mostrar_kpis_y_graficos(contenedor, usar_demo, df_filtrado, total_ingresos, servicios_realizados, monto_promedio, alertas)


def _renderizar_bi_con_snapshot(contenedor, usar_demo: bool, snapshot) -> None:
    """Renderiza el panel BI a partir de un BiSnapshot (fuente MySQL o demo filtrada)."""
    alertas = contenedor.dashboard.evaluar_alertas_kpi(
        snapshot.total_ingresos, snapshot.servicios_realizados, snapshot.monto_promedio
    )
    _mostrar_kpis_y_graficos(
        contenedor,
        usar_demo,
        snapshot.df_filtrado,
        snapshot.total_ingresos,
        snapshot.servicios_realizados,
        snapshot.monto_promedio,
        alertas,
    )


def _mostrar_kpis_y_graficos(
    contenedor,
    usar_demo: bool,
    df_filtrado: pd.DataFrame,
    total_ingresos: float,
    servicios_realizados: int,
    monto_promedio: float,
    alertas: list,
) -> None:
    """Renderiza métricas, alertas, gráficos, tabla e insight estadístico."""
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
    if not df_filtrado.empty and "monto_total" in df_filtrado.columns:
        insights_stats = df_filtrado[["monto_total"]].describe().T
        insights_view = insights_stats[["mean", "min", "max"]].rename(
            columns={"mean": "Promedio", "min": "Mínimo", "max": "Máximo"}
        )
        st.dataframe(insights_view, use_container_width=True)
    else:
        st.info("No hay datos para los filtros seleccionados.")
        return

    if df_filtrado.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        df_filtrado = df_filtrado.copy()
        df_filtrado["fecha"] = pd.to_datetime(df_filtrado["fecha"], errors="coerce")

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
