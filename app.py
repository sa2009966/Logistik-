import streamlit as st  # Importa Streamlit para construir la interfaz web interactiva.
import pandas as pd  # Importa Pandas para manipular datos tabulares y consultas SQL.
import plotly.express as px  # Importa Plotly Express para crear graficos interactivos.
import mysql.connector  # Importa el conector oficial de MySQL para Python.
from mysql.connector import Error  # Importa el tipo de excepcion para manejar errores de MySQL.
from annotated_text import annotated_text  # Importa el componente para texto anotado (st-annotated-text).
from datetime import date  # Importa date para el campo de fecha del formulario.

# Configura la pagina con layout amplio para experiencia de dashboard.
st.set_page_config(page_title="Logistik BI Dashboard", layout="wide")

# Define parametros de conexion al servidor MySQL local.
DB_HOST = "localhost"  # Host del servidor MySQL.
DB_PORT = 3306  # Puerto por defecto de MySQL.
DB_USER = "root"  # Usuario de conexion a MySQL.
DB_PASSWORD = "1234"  # Password del usuario MySQL.
DB_NAME = "db_bi_alex"  # Nombre de la base de datos objetivo.
DB_TABLE = "transacciones_logistik"  # Nombre de la tabla profesional de Logistik.

# Lista oficial de tipos de servicio para selectbox de negocio.
TIPOS_SERVICIO = [
    "Fletes Nacionales",
    "Fletes Internacionales",
    "Almacenaje",
    "Distribucion Local",
    "Gestion Aduanera",
    "Transporte Refrigerado",
    "Logistica de Ultima Milla",
    "Consolidacion de Carga",
    "Seguros de Mercancia",
    "Servicios Express",
]

# Lista oficial de estados de transaccion.
ESTADOS = ["Completado", "Pendiente", "Cancelado"]

# Lista de metodos de pago para operaciones financieras.
METODOS_PAGO = ["Transferencia", "Efectivo", "Tarjeta", "Credito", "Deposito"]
CSV_REQUIRED_COLUMNS = ["monto_total", "estado", "tipo_servicio"]  # Columnas minimas para analitica.


def get_server_connection():
    # Abre una conexion al servidor MySQL (sin base seleccionada) para tareas DDL.
    return mysql.connector.connect(
        host=DB_HOST,  # Define el host de MySQL.
        port=DB_PORT,  # Define el puerto de MySQL.
        user=DB_USER,  # Define el usuario de autenticacion.
        password=DB_PASSWORD,  # Define la contrasena de autenticacion.
        autocommit=True,  # Activa autocommit para comandos CREATE DATABASE.
    )


def get_app_connection():
    # Abre conexion a la base de datos de la app para consultas y escrituras.
    return mysql.connector.connect(
        host=DB_HOST,  # Define el host de MySQL.
        port=DB_PORT,  # Define el puerto de MySQL.
        user=DB_USER,  # Define el usuario de autenticacion.
        password=DB_PASSWORD,  # Define la contrasena de autenticacion.
        database=DB_NAME,  # Selecciona la base de datos de trabajo.
    )


def init_database():
    # Crea la base y la tabla transacciones_logistik si no existen.
    conn = None  # Declara conexion para cierre seguro en finally.
    cursor = None  # Declara cursor para cierre seguro en finally.
    try:
        conn = get_server_connection()  # Conecta al servidor MySQL.
        cursor = conn.cursor()  # Crea cursor para ejecutar sentencias SQL.

        # SQL DDL: crea la base de datos solo si no existe.
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

        # SQL USE: selecciona la base donde se creara la tabla.
        cursor.execute(f"USE {DB_NAME}")

        # SQL DDL: crea la tabla principal de transacciones logistic-as.
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {DB_TABLE} (
            id_transaccion INT AUTO_INCREMENT PRIMARY KEY,
            fecha DATE NOT NULL,
            cliente VARCHAR(100) NOT NULL,
            tipo_servicio VARCHAR(100) NOT NULL,
            descripcion VARCHAR(255) NOT NULL,
            origen VARCHAR(100) NOT NULL,
            destino VARCHAR(100) NOT NULL,
            monto_total DECIMAL(10, 2) NOT NULL,
            estado VARCHAR(50) NOT NULL,
            metodo_pago VARCHAR(50) NOT NULL,
            usuario_registro VARCHAR(50) NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(create_table_sql)  # Ejecuta CREATE TABLE.
    finally:
        # Cierra el cursor si fue creado para evitar fugas de recursos.
        if cursor is not None:
            cursor.close()
        # Cierra la conexion si sigue activa.
        if conn is not None and conn.is_connected():
            conn.close()


def insert_transaction(fecha, cliente, tipo_servicio, descripcion, origen, destino, monto_total, estado, metodo_pago, usuario_registro):
    # Inserta una nueva transaccion logistica en MySQL usando parametros seguros.
    conn = None  # Declara conexion para cierre seguro.
    cursor = None  # Declara cursor para cierre seguro.
    try:
        conn = get_app_connection()  # Conecta a la base de trabajo.
        cursor = conn.cursor()  # Crea cursor para ejecutar INSERT.

        # SQL DML INSERT: inserta columnas de negocio; fecha_registro usa valor por defecto.
        insert_sql = f"""
        INSERT INTO {DB_TABLE}
        (fecha, cliente, tipo_servicio, descripcion, origen, destino, monto_total, estado, metodo_pago, usuario_registro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(
            insert_sql,
            (fecha, cliente, tipo_servicio, descripcion, origen, destino, monto_total, estado, metodo_pago, usuario_registro),
        )
        conn.commit()  # Confirma la transaccion para persistir el registro.
    finally:
        # Cierra cursor de insercion.
        if cursor is not None:
            cursor.close()
        # Cierra conexion a MySQL.
        if conn is not None and conn.is_connected():
            conn.close()


def load_transactions_df():
    # Consulta todas las transacciones para analitica BI.
    conn = None  # Declara conexion para cierre seguro.
    try:
        conn = get_app_connection()  # Conecta a base de datos.
        # SQL SELECT: obtiene dataset completo ordenado por fecha.
        query = f"""
        SELECT id_transaccion, fecha, cliente, tipo_servicio, descripcion, origen, destino,
               monto_total, estado, metodo_pago, usuario_registro, fecha_registro
        FROM {DB_TABLE}
        ORDER BY fecha ASC, id_transaccion ASC
        """
        return pd.read_sql(query, conn)  # Carga resultados en DataFrame.
    finally:
        # Cierra conexion luego de la consulta.
        if conn is not None and conn.is_connected():
            conn.close()


def init_demo_data():
    # Crea 10 registros demo realistas para presentaciones offline.
    if "demo_transactions_df" not in st.session_state:
        st.session_state.demo_transactions_df = pd.DataFrame(
            [
                {"id_transaccion": 1, "fecha": "2026-03-10", "cliente": "Empresa A", "tipo_servicio": "Fletes Nacionales", "descripcion": "Traslado de mercancia seca", "origen": "San Salvador", "destino": "Santa Ana", "monto_total": 1250.00, "estado": "Completado", "metodo_pago": "Transferencia", "usuario_registro": "admin", "fecha_registro": "2026-03-10 08:10:00"},
                {"id_transaccion": 2, "fecha": "2026-03-10", "cliente": "Empresa B", "tipo_servicio": "Fletes Internacionales", "descripcion": "Exportacion de repuestos", "origen": "San Salvador", "destino": "Guatemala", "monto_total": 3890.00, "estado": "Completado", "metodo_pago": "Credito", "usuario_registro": "admin", "fecha_registro": "2026-03-10 09:45:00"},
                {"id_transaccion": 3, "fecha": "2026-03-11", "cliente": "Empresa C", "tipo_servicio": "Almacenaje", "descripcion": "Resguardo de inventario por semana", "origen": "Bodega Central", "destino": "Bodega Central", "monto_total": 780.00, "estado": "Pendiente", "metodo_pago": "Transferencia", "usuario_registro": "analista1", "fecha_registro": "2026-03-11 10:00:00"},
                {"id_transaccion": 4, "fecha": "2026-03-12", "cliente": "Empresa D", "tipo_servicio": "Distribucion Local", "descripcion": "Entrega en rutas urbanas", "origen": "Soyapango", "destino": "San Miguel", "monto_total": 980.00, "estado": "Completado", "metodo_pago": "Efectivo", "usuario_registro": "analista1", "fecha_registro": "2026-03-12 11:30:00"},
                {"id_transaccion": 5, "fecha": "2026-03-12", "cliente": "Empresa E", "tipo_servicio": "Gestion Aduanera", "descripcion": "Tramite de importacion consolidada", "origen": "Acajutla", "destino": "San Salvador", "monto_total": 2210.00, "estado": "Pendiente", "metodo_pago": "Deposito", "usuario_registro": "coordinador", "fecha_registro": "2026-03-12 15:25:00"},
                {"id_transaccion": 6, "fecha": "2026-03-13", "cliente": "Empresa F", "tipo_servicio": "Transporte Refrigerado", "descripcion": "Cadena de frio para lacteos", "origen": "La Libertad", "destino": "Santa Ana", "monto_total": 3120.00, "estado": "Completado", "metodo_pago": "Transferencia", "usuario_registro": "coordinador", "fecha_registro": "2026-03-13 08:05:00"},
                {"id_transaccion": 7, "fecha": "2026-03-14", "cliente": "Empresa G", "tipo_servicio": "Logistica de Ultima Milla", "descripcion": "Entrega domiciliaria ecommerce", "origen": "Apopa", "destino": "San Salvador", "monto_total": 640.00, "estado": "Completado", "metodo_pago": "Tarjeta", "usuario_registro": "operador2", "fecha_registro": "2026-03-14 09:12:00"},
                {"id_transaccion": 8, "fecha": "2026-03-15", "cliente": "Empresa H", "tipo_servicio": "Consolidacion de Carga", "descripcion": "Consolidado semanal de pallets", "origen": "Sonsonate", "destino": "San Salvador", "monto_total": 1740.00, "estado": "Pendiente", "metodo_pago": "Credito", "usuario_registro": "operador2", "fecha_registro": "2026-03-15 13:20:00"},
                {"id_transaccion": 9, "fecha": "2026-03-16", "cliente": "Empresa I", "tipo_servicio": "Seguros de Mercancia", "descripcion": "Poliza para equipo electronico", "origen": "San Salvador", "destino": "San Vicente", "monto_total": 560.00, "estado": "Cancelado", "metodo_pago": "Transferencia", "usuario_registro": "supervisor", "fecha_registro": "2026-03-16 16:50:00"},
                {"id_transaccion": 10, "fecha": "2026-03-17", "cliente": "Empresa J", "tipo_servicio": "Servicios Express", "descripcion": "Envio urgente de documentos", "origen": "San Miguel", "destino": "San Salvador", "monto_total": 420.00, "estado": "Completado", "metodo_pago": "Efectivo", "usuario_registro": "supervisor", "fecha_registro": "2026-03-17 17:10:00"},
            ]
        )
        st.session_state.demo_transactions_df["fecha"] = pd.to_datetime(st.session_state.demo_transactions_df["fecha"])
        st.session_state.demo_transactions_df["fecha_registro"] = pd.to_datetime(st.session_state.demo_transactions_df["fecha_registro"])


def insert_transaction_demo(fecha, cliente, tipo_servicio, descripcion, origen, destino, monto_total, estado, metodo_pago, usuario_registro):
    # Inserta una transaccion en memoria para simulacion offline en tiempo real.
    df_demo = st.session_state.demo_transactions_df.copy()
    next_id = int(df_demo["id_transaccion"].max()) + 1 if not df_demo.empty else 1
    new_row = pd.DataFrame(
        [
            {
                "id_transaccion": next_id,
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
    st.session_state.demo_transactions_df = pd.concat([df_demo, new_row], ignore_index=True)


def load_transactions_demo_df():
    # Devuelve copia ordenada del dataset demo para dashboard.
    return st.session_state.demo_transactions_df.sort_values(by=["fecha", "id_transaccion"]).reset_index(drop=True)


def compute_kpis(df_data):
    # Calcula KPIs financieros del panel ejecutivo.
    total_ingresos = float(df_data["monto_total"].sum()) if not df_data.empty else 0.0
    servicios_realizados = int(len(df_data))
    monto_promedio = total_ingresos / servicios_realizados if servicios_realizados > 0 else 0.0
    return total_ingresos, servicios_realizados, monto_promedio


def validate_csv_columns(df_csv):
    # Valida que el CSV tenga las columnas requeridas para graficas y KPIs.
    missing = [col for col in CSV_REQUIRED_COLUMNS if col not in df_csv.columns]
    return missing


def prepare_csv_dataframe(df_csv):
    # Normaliza el dataframe del CSV para alinearlo con el esquema esperado por el dashboard.
    df_csv = df_csv.copy()
    if "fecha" not in df_csv.columns:
        # Si no existe fecha en el CSV, asigna fecha actual para habilitar grafico de linea.
        df_csv["fecha"] = pd.Timestamp.today().date()
    df_csv["fecha"] = pd.to_datetime(df_csv["fecha"], errors="coerce").fillna(pd.Timestamp.today())
    df_csv["monto_total"] = pd.to_numeric(df_csv["monto_total"], errors="coerce").fillna(0.0)
    df_csv["estado"] = df_csv["estado"].astype(str)
    df_csv["tipo_servicio"] = df_csv["tipo_servicio"].astype(str)
    return df_csv


# Control de modo de operacion (MySQL real o demo offline).
USE_DEMO_MODE = False
try:
    init_database()  # Inicializa objetos de base de datos.
    st.success("Conexion con MySQL lista. Operando con datos reales.")
except Error as init_error:
    USE_DEMO_MODE = True  # Activa demo si falla conexion/DDL.
    init_demo_data()  # Carga dataset demo inicial.
    st.error(f"No fue posible conectar a MySQL. Se activa modo demo: {init_error}")

# Encabezado principal del dashboard BI.
st.title("Dashboard BI Interactivo - Logistik S.A. de C.V.")
st.caption("Panel en tiempo real para registrar transacciones logistic-as y analizar indicadores financieros.")

# Sidebar para importar fuente externa de datos en formato CSV.
st.sidebar.header("Carga de Datos")
uploaded_csv = st.sidebar.file_uploader(
    "Importar CSV para analisis externo",
    type=["csv"],
    help="Si cargas un CSV valido, se priorizara sobre MySQL/demo para el dashboard.",
)

# Crea tabs para captura de datos y visualizacion.
tab_ingreso, tab_dashboard = st.tabs(["Ingresar Nueva Transaccion", "Dashboard BI"])

with tab_ingreso:
    # Encabezado del formulario de captura.
    st.subheader("Formulario de Registro Operativo")
    with st.form("form_transaccion_logistik", clear_on_submit=True):
        # Campo de fecha de la transaccion.
        fecha = st.date_input("Fecha", value=date.today())
        # Campo de cliente para identificar empresa.
        cliente = st.text_input("Cliente")
        # Campo obligatorio con opciones de servicios logisticos.
        tipo_servicio = st.selectbox("Tipo de Servicio", TIPOS_SERVICIO)
        # Campo de descripcion corta de la operacion.
        descripcion = st.text_input("Descripcion")
        # Campo de origen logistico.
        origen = st.text_input("Origen")
        # Campo de destino logistico.
        destino = st.text_input("Destino")
        # Campo monetario principal del registro.
        monto_total = st.number_input("Monto Total", min_value=0.0, step=0.01, format="%.2f")
        # Campo de estado del servicio.
        estado = st.selectbox("Estado", ESTADOS)
        # Campo de metodo de pago.
        metodo_pago = st.selectbox("Metodo de Pago", METODOS_PAGO)
        # Campo de usuario que registra la transaccion.
        usuario_registro = st.text_input("Usuario Registro", value="admin")
        # Boton de envio del formulario.
        submit = st.form_submit_button("Registrar Transaccion")

    # Valida y procesa insercion de la transaccion.
    if submit:
        if not cliente.strip() or not origen.strip() or not destino.strip() or not descripcion.strip() or not usuario_registro.strip():
            st.error("Completa todos los campos de texto requeridos.")
        elif monto_total <= 0:
            st.error("El monto total debe ser mayor que cero.")
        else:
            if USE_DEMO_MODE:
                # Inserta en memoria y actualiza panel en tiempo real.
                insert_transaction_demo(
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
                st.success("Transaccion registrada en modo demo.")
                st.rerun()
            else:
                try:
                    # Inserta registro real en MySQL y recarga panel.
                    insert_transaction(
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
                    st.success("Transaccion registrada en MySQL.")
                    st.rerun()
                except Error as insert_error:
                    st.error(f"Error al registrar en base de datos: {insert_error}")

with tab_dashboard:
    # Encabezado de analitica principal.
    st.subheader("Visualizacion Dinamica de Operaciones")
    data_source_label = ""  # Etiqueta para indicar la fuente activa de datos.

    # Prioriza CSV si el usuario lo carga en la barra lateral.
    if uploaded_csv is not None:
        try:
            # Lee el archivo CSV subido por el usuario.
            df_csv = pd.read_csv(uploaded_csv)
            # Valida columnas requeridas para analisis.
            missing_columns = validate_csv_columns(df_csv)
            if missing_columns:
                # Informa columnas faltantes con mensaje claro y accionable.
                st.error(
                    "El archivo CSV no tiene la estructura necesaria. "
                    f"Faltan estas columnas: {', '.join(missing_columns)}. "
                    "Columnas minimas requeridas: monto_total, estado, tipo_servicio."
                )
                st.stop()
            # Prepara datos para uso consistente en graficas y KPI.
            df_data = prepare_csv_dataframe(df_csv)
            data_source_label = "CSV EXTERNO"
            st.success("CSV cargado correctamente. El dashboard usa esta fuente de datos.")
        except Exception as csv_error:
            st.error(f"No se pudo procesar el CSV cargado: {csv_error}")
            st.stop()
    elif USE_DEMO_MODE:
        # Carga datos de sesion para modo sin servidor.
        df_data = load_transactions_demo_df()
        data_source_label = "DEMO OFFLINE"
    else:
        try:
            # Carga datos reales desde MySQL.
            df_data = load_transactions_df()
            data_source_label = "MYSQL ONLINE"
        except Error as read_error:
            st.error(f"Error al leer transacciones de MySQL: {read_error}")
            st.stop()

    # Muestra modo de operacion activo.
    st.caption(f"Fuente activa de datos: {data_source_label}")

    # Normaliza la fecha para filtros y analitica temporal.
    df_data["fecha"] = pd.to_datetime(df_data["fecha"], errors="coerce")

    # Panel de filtros interactivos para analizar subconjuntos del dataset.
    st.markdown("### Filtros de Analisis")
    f1, f2, f3 = st.columns(3)

    # Filtro por estado (multiseleccion) con todas las opciones marcadas por defecto.
    estados_disponibles = sorted(df_data["estado"].dropna().astype(str).unique().tolist())
    estados_sel = f1.multiselect("Filtrar por Estado", estados_disponibles, default=estados_disponibles)

    # Filtro por tipo de servicio (multiseleccion) con todas las opciones marcadas por defecto.
    servicios_disponibles = sorted(df_data["tipo_servicio"].dropna().astype(str).unique().tolist())
    servicios_sel = f2.multiselect(
        "Filtrar por Tipo de Servicio",
        servicios_disponibles,
        default=servicios_disponibles,
    )

    # Filtro por rango de fecha usando los limites reales del dataset.
    fechas_validas = df_data["fecha"].dropna()
    if fechas_validas.empty:
        fecha_min = date.today()
        fecha_max = date.today()
    else:
        fecha_min = fechas_validas.min().date()
        fecha_max = fechas_validas.max().date()
    fecha_rango = f3.date_input(
        "Rango de Fechas",
        value=(fecha_min, fecha_max),
        min_value=fecha_min,
        max_value=fecha_max,
    )

    # Aplica filtros seleccionados para construir el dataframe activo del dashboard.
    if isinstance(fecha_rango, tuple) and len(fecha_rango) == 2:
        fecha_inicio, fecha_fin = fecha_rango
    else:
        fecha_inicio, fecha_fin = fecha_min, fecha_max

    df_filtered = df_data.copy()
    df_filtered = df_filtered[df_filtered["estado"].astype(str).isin(estados_sel)]
    df_filtered = df_filtered[df_filtered["tipo_servicio"].astype(str).isin(servicios_sel)]
    df_filtered = df_filtered[
        (df_filtered["fecha"].dt.date >= fecha_inicio) & (df_filtered["fecha"].dt.date <= fecha_fin)
    ]

    # Calcula KPIs sobre el dataset filtrado para analisis contextual.
    total_ingresos, servicios_realizados, monto_promedio = compute_kpis(df_filtered)

    # Muestra KPI principal con texto anotado.
    annotated_text(
        "Total Ingresos: ",
        (f"${total_ingresos:,.2f}", "SUM(monto_total)", "#1f77b4"),
    )

    # Renderiza tres KPIs ejecutivos solicitados.
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
    k2.metric("Servicios Realizados", f"{servicios_realizados}")
    k3.metric("Monto Promedio", f"${monto_promedio:,.2f}")

    # Muestra resumen estadistico automatico de ingresos logisticos.
    st.markdown("### Insights Estadisticos")
    insights_stats = df_filtered[["monto_total"]].describe().T
    insights_view = insights_stats[["mean", "min", "max"]].rename(
        columns={"mean": "Promedio", "min": "Minimo", "max": "Maximo"}
    )
    st.dataframe(insights_view, use_container_width=True)

    # Evita graficacion si la tabla esta vacia.
    if df_filtered.empty:
        st.info("No hay datos para los filtros seleccionados.")
    else:
        # Agrupa por fecha y suma monto_total, aplicando reset_index() para evitar Length mismatch.
        df_line = df_filtered.groupby(df_filtered["fecha"].dt.date)["monto_total"].sum().reset_index()
        df_line.columns = ["fecha", "monto_total"]

        # Agrupa por tipo_servicio y suma monto_total, aplicando reset_index() obligatorio.
        df_servicio = df_filtered.groupby("tipo_servicio")["monto_total"].sum().reset_index()

        # Agrupa por estado y suma monto_total, aplicando reset_index() obligatorio.
        df_estado = df_filtered.groupby("estado")["monto_total"].sum().reset_index()

        # Distribuye 3 graficos en columnas.
        c1, c2, c3 = st.columns(3)

        # Grafico Line: tendencia por fecha usando monto_total.
        fig_line = px.line(
            df_line,
            x="fecha",
            y="monto_total",
            title="Tendencia de Ingresos",
            template="plotly_dark",
            markers=True,
        )
        c1.plotly_chart(fig_line, use_container_width=True)

        # Grafico Bar: ingresos por tipo de servicio usando monto_total.
        fig_bar = px.bar(
            df_servicio,
            x="tipo_servicio",
            y="monto_total",
            title="Ingresos por Tipo de Servicio",
            template="plotly_dark",
            color="tipo_servicio",
        )
        c2.plotly_chart(fig_bar, use_container_width=True)

        # Grafico Pie: participacion por estado basada en monto_total.
        fig_pie = px.pie(
            df_estado,
            names="estado",
            values="monto_total",
            title="Participacion por Estado",
            template="plotly_dark",
        )
        c3.plotly_chart(fig_pie, use_container_width=True)

    # Muestra tabla consolidada para auditoria y detalle operativo.
    st.dataframe(df_filtered, use_container_width=True)

    # Seccion final para exportar datos en CSV UTF-8.
    st.markdown("### Centro de Reportes")
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Descargar reporte CSV",
        data=csv_bytes,
        file_name="reporte_logistik.csv",
        mime="text/csv",
    )