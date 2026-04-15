# Logistik BI Dashboard 🚛📊

## Gestión de datos logísticos con Arquitectura Enterprise (SOLID)

Sistema de inteligencia de negocios de alto rendimiento que transforma registros operativos en KPIs estratégicos. Diseñado bajo el paradigma de Clean Architecture, el sistema garantiza escalabilidad, mantenibilidad y un desacoplamiento total entre la lógica de negocio y la infraestructura.

## ✨ Características Principales

- **Arquitectura Desacoplada:** Implementación estricta de POO y SOLID para un código limpio y profesional.
- **Doble Persistencia:** Conexión nativa a MySQL con un robusto sistema de fallback a Modo Demo (InMemory) si la base de datos no está disponible.
- **Auditoría de Grado Industrial:** Trazabilidad completa de acciones de usuario (Logins, Cargas de datos, Exportaciones) integrada mediante Inyección de Dependencias.
- **Reporting Proactivo:** Generación de reportes en Excel y sistema de Alertas de KPIs dinámicas.
- **UI Profesional:** Interfaz responsiva "Slate & Steel" con animaciones fluidas y optimización para móviles.

## 🏗️ Arquitectura de Capas (SOLID Implementation)

El proyecto se rige por la Inversión de Dependencias (DIP), donde la UI y los servicios dependen de abstracciones, no de implementaciones.


| Capa        | Componentes Clave                                   | Responsabilidad (Single Responsibility)                                       |
| ----------- | --------------------------------------------------- | ----------------------------------------------------------------------------- |
| `core/`     | `SecurityHandler`, `AuthSession`                    | Configuración global, seguridad (bcrypt) y gestión de estados de sesión.      |
| `database/` | `LogistikRepository`, `AuditRepository`             | Implementación concreta de la persistencia (MySQL / InMemory).                |
| `services/` | `AnalyticsService`, `AuditService`, `ExportService` | Casos de Uso: lógica de negocio, orquestación de auditoría y cálculo de KPIs. |
| `ui/`       | `TemaInterfaz`, `RenderizadorGraficos`              | Presentación responsiva, visualización de datos y componentes de usuario.     |


### Cumplimiento de Principios SOLID

- **S (Single Responsibility):** Cada clase tiene una única razón de cambio. Ej: `ExportService` solo gestiona formatos, no conoce la base de datos.
- **O (Open/Closed):** Sistema de gráficos extensible mediante la clase base `BaseGraficoPlotly` sin modificar el núcleo.
- **L (Liskov Substitution):** Los repositorios MySQL y Demo son totalmente intercambiables a través de interfaces (`contracts.py`).
- **I (Interface Segregation):** Interfaces de repositorio específicas para evitar que los servicios dependan de métodos que no utilizan.
- **D (Dependency Inversion):** Los servicios inyectan interfaces; `container.py` se encarga de fabricar los objetos necesarios.

## 🛠️ Stack Tecnológico

- **Core:** Python 3.12+ (tipado fuerte y docstrings estilo Google).
- **Frontend:** Streamlit (personalizado con CSS profesional).
- **Data Engine:** MySQL / MariaDB y Pandas.
- **Seguridad:** BCrypt para hashing de credenciales.
- **Visualización:** Plotly (elegante dark theme).

## 🚀 Instalación y Uso Rápido

### Clonación y Entorno

```bash
git clone https://github.com/sa2009966/Logistik-.git
cd Logistik-
python3 -m venv env_dashboard
source env_dashboard/bin/activate
pip install -r requirements.txt
```

### Configuración de Variables (`.env`)

Crea un archivo `.env` en la raíz con las credenciales de tu base de datos y configuración de administrador.

Variables recomendadas:

- `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`
- `ALLOW_SELF_REGISTRATION`

### Ejecución

```bash
streamlit run app.py
```

## 🔐 Seguridad y Auditoría

El sistema implementa un `AuditService` orquestado por POO que registra:

- **Trazabilidad:** Quién, cuándo y qué acción se realizó.
- **Alertas de KPIs:** El sistema identifica automáticamente desviaciones críticas en la eficiencia logística y lo notifica visualmente.
- **Protección de Datos:** Cifrado de nivel industrial para toda la gestión de usuarios.

## 🛣️ Roadmap de Desarrollo

- Refactorización completa a SOLID y Clean Architecture.
- Interfaz responsiva y Mobile-First.
- Módulo de Auditoría y Exportación avanzada.
- Fase futura: implementación de Docker y modelos de Machine Learning para predicción de demanda.

