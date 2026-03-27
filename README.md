# Dashboard BI Logistik S.A. de C.V.

Aplicacion web en Streamlit para registro y analisis de transacciones logisticas con visualizacion BI en tiempo real.

## Caracteristicas principales

- Registro de transacciones en tiempo real con formulario operativo.
- Conexion a MySQL como fuente primaria de datos.
- Modo demo offline automatico cuando MySQL no esta disponible.
- Importacion de datos externos por CSV desde la barra lateral.
- Priorizacion automatica del CSV sobre MySQL/demo para analisis.
- KPIs financieros dinamicos:
  - Total Ingresos
  - Servicios Realizados
  - Monto Promedio
- Graficos interactivos con Plotly en tema oscuro:
  - Line (tendencia de ingresos por fecha)
  - Bar (ingresos por tipo de servicio)
  - Pie (participacion por estado)
- Insights estadisticos automaticos con `describe()` (promedio, minimo, maximo).
- Filtros interactivos por estado, tipo de servicio y rango de fechas.
- Centro de reportes para descargar el DataFrame actual filtrado en CSV UTF-8.

## Estructura de datos (MySQL)

La app crea automaticamente la base y tabla si existen permisos:

- Base de datos: `db_bi_alex`
- Tabla: `transacciones_logistik`

Campos:

- `id_transaccion` (PK, autoincrement)
- `fecha` (DATE)
- `cliente` (VARCHAR 100)
- `tipo_servicio` (VARCHAR 100)
- `descripcion` (VARCHAR 255)
- `origen` (VARCHAR 100)
- `destino` (VARCHAR 100)
- `monto_total` (DECIMAL 10,2)
- `estado` (VARCHAR 50)
- `metodo_pago` (VARCHAR 50)
- `usuario_registro` (VARCHAR 50)
- `fecha_registro` (TIMESTAMP)

## Requisitos

- Python 3.10+ (recomendado)
- Streamlit
- Pandas
- Plotly
- mysql-connector-python
- st-annotated-text
- Servidor MySQL (opcional, la app puede correr en modo demo)

## Instalacion rapida

Desde la raiz del proyecto:

```bash
python3 -m venv env_dashboard
source env_dashboard/bin/activate
pip install streamlit pandas plotly mysql-connector-python st-annotated-text
```

## Configuracion de MySQL

En `app.py` se usan estos parametros:

- `DB_HOST = "localhost"`
- `DB_PORT = 3306`
- `DB_USER = "root"`
- `DB_PASSWORD = "1234"`
- `DB_NAME = "db_bi_alex"`

Ajusta estos valores segun tu entorno local.

## Ejecutar la aplicacion

```bash
cd "/home/alex/Descargas/proyecto con python de gestion"
source env_dashboard/bin/activate
streamlit run app.py
```

## Sobre el servicio MySQL en Linux

Si tienes MySQL instalado:

```bash
sudo systemctl start mysql
sudo systemctl status mysql
```

Si no existe `mysql.service`, probablemente solo tienes cliente instalado. Instala servidor:

```bash
sudo apt update
sudo apt install mysql-server
```

Si tu distro usa MariaDB:

```bash
sudo systemctl start mariadb
sudo systemctl status mariadb
```

## Importar CSV (analisis externo)

1. Abre la app en el navegador.
2. En el sidebar, usa `Importar CSV para analisis externo`.
3. El CSV debe incluir al menos estas columnas:
   - `monto_total`
   - `estado`
   - `tipo_servicio`
4. Si el CSV es valido, la app lo usara como fuente activa para KPIs, graficas, insights, filtros y descarga.

## Filtros y reportes

En la pestana `Dashboard BI`:

- Filtra por estado.
- Filtra por tipo de servicio.
- Selecciona rango de fechas.

En `Centro de Reportes`:

- Descarga el dataset actual (filtrado) en CSV UTF-8 con `Descargar reporte CSV`.

## Modo demo offline

Si no hay conexion a MySQL, la app activa automaticamente modo demo con 10 registros iniciales (Empresa A a Empresa J), manteniendo:

- registro en tiempo real,
- recarga con `st.rerun()`,
- KPIs,
- graficas,
- filtros,
- exportacion CSV.
