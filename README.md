# Logistik BI Dashboard

### Gestión de datos logísticos y Business Intelligence

Sistema de análisis logístico que convierte registros operativos en KPIs accionables. Stack en Python con **Streamlit**, **MySQL** (con fallback a **modo demo** en memoria), **Plotly** (tema oscuro) y **bcrypt** para contraseñas.

---

## El proyecto

- **Autenticación:** Sesión en Streamlit y contraseñas con **bcrypt** (`SecurityHandler` en `core/`).
- **Datos:** Conexión a **MySQL**; si falla el arranque, **modo demo** con datos en `session_state`.
- **BI:** KPIs, filtros y gráficos Plotly; opción de **CSV externo** para el tablero.
- **Arquitectura:** Capas **core → database → services → ui**, con **POO**, **inyección de dependencias** y contratos **SOLID** en `services/`.

---

## Arquitectura de capas


| Carpeta     | Responsabilidad                                                                                                                                                               |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `core/`     | Configuración (`ConfiguracionAplicacion`), constantes (`ConstantesNegocio`), sesión Streamlit (`AuthSessionController`), seguridad (`SecurityHandler`).                       |
| `database/` | Infraestructura: `GestorConexionMySQL` y `LogistikRepository` (implementa los puertos definidos en `services/contracts.py`).                                                  |
| `services/` | Casos de uso: `AuthService`, `LogisticaService`, `DashboardService`, `AnalyticsService` (KPIs), `CsvDataLoaderService` (CSV), `DemoDataStore`, composición en `container.py`. |
| `ui/`       | Vistas Streamlit, tema (`TemaInterfaz`) y gráficos extensibles (`BaseGraficoPlotly` + `RenderizadorGraficosBi`).                                                              |


**Flujo de dependencias:** la UI consume el **contenedor** (`fabricar_contenedor`) y llama a **servicios**; los servicios dependen de **interfaces** (`IAuthRepository`, `IBootstrapRepository`, `ITransaccionesDataSource`), no de clases concretas de `database/`.

**Principios SOLID (resumen):**

- **S:** CSV (`CsvDataLoaderService`) separado de KPIs (`AnalyticsService`).
- **O:** Nuevos gráficos: subclase de `BaseGraficoPlotly` y registro en `RenderizadorGraficosBi`.
- **L:** Fuentes de transacciones intercambiables vía `ITransaccionesDataSource` (MySQL / demo).
- **I:** Puertos segregados en `services/contracts.py`.
- **D:** Servicios inyectan abstracciones; la implementación MySQL vive en `database/`.

---

## Stack tecnológico

- **Lenguaje:** Python 3.12+
- **UI:** [Streamlit](https://streamlit.io/)
- **Base de datos:** MySQL / MariaDB
- **Seguridad:** bcrypt
- **Gráficos:** Plotly (tema oscuro)

---

## Instalación y uso

1. **Clonar el repositorio** (ajusta la URL si usas un fork distinto):
  ```bash
   git clone https://github.com/sa2009966/Logistik-.git
   cd Logistik-
  ```
2. **Entorno virtual y dependencias:**
  ```bash
   python3 -m venv env_dashboard
   source env_dashboard/bin/activate
   pip install -r requirements.txt
  ```
3. **Variables de entorno (`.env` en la raíz del proyecto, junto a `app.py`):**

  | Variable                                                  | Descripción                                            |
  | --------------------------------------------------------- | ------------------------------------------------------ |
  | `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME` | Conexión MySQL                                         |
  | `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`        | Usuario admin inicial si no existe                     |
  | `ALLOW_SELF_REGISTRATION`                                 | `true` / `false` — registro desde la pantalla de login |

4. **Punto de entrada (sin cambios):** el arranque sigue siendo `**app.py`**.
  ```bash
   streamlit run app.py
  ```
   También puedes ejecutar `python app.py` si tu entorno invoca Streamlit correctamente; la forma recomendada es `streamlit run app.py`.

---

## Seguridad y buenas prácticas

- Las contraseñas se almacenan hasheadas (no en texto plano).
- El dashboard solo es accesible con sesión autenticada.
- Credenciales y secretos deben ir en `.env` (no versionar secretos reales).

---

## Vistas del sistema

1. **Landing:** Presentación y acceso al login.
2. **Login:** Acceso y registro opcional (si `ALLOW_SELF_REGISTRATION` lo permite).
3. **Dashboard BI:** Registro de transacciones, KPIs, filtros, CSV opcional y exportación.

