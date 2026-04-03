# 🚀 Logistik BI Dashboard

### Gestión de Datos Logísticos & Business Intelligence

Sistema profesional de análisis logístico diseñado para transformar registros crudos en indicadores de negocio (KPIs) accionables. Construido sobre un stack moderno de Python, priorizando la **seguridad**, la **escalabilidad** y una experiencia de usuario **Cyber-Dark**.

---

## 🎯 El Proyecto
Este dashboard no es solo una interfaz; es un ecosistema completo que permite:
* **Autenticación Blindada:** Gestión de sesiones y seguridad de contraseñas con **bcrypt**.
* **Dualidad de Datos:** Conexión nativa a **MySQL** con un "Fallback" automático a **Modo Demo** (en memoria) si el servidor no está disponible.
* **Analítica en Tiempo Real:** Visualización de ingresos, estados de servicio y ticket promedio mediante gráficos interactivos de **Plotly**.
* **Flexibilidad:** Soporte para carga dinámica de archivos **CSV** que sobreescriben la vista actual para auditorías rápidas.

---

## 🏗️ Arquitectura de Capas (Clean Code)
Para este proyecto, implementé una estructura organizada que separa las responsabilidades, facilitando el mantenimiento y el crecimiento del código:

* 📂 `core/`: Cerebro del sistema (Configuración global, constantes y lógica de `auth/security`).
* 📂 `database/`: Capa de persistencia (Patrón Singleton para conexión y Repositorios SQL).
* 📂 `services/`: Lógica de negocio (Procesamiento de analíticas y generación de datasets).
* 📂 `ui/`: Capa visual (Vistas de Landing, Login y Dashboard con estilos CSS inyectados).

---

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.12+
* **Framework UI:** [Streamlit](https://streamlit.io/)
* **Base de Datos:** MySQL / MariaDB
* **Seguridad:** Bcrypt (Hashing)
* **Gráficos:** Plotly (Dark Theme)

---

## 🚀 Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/sa2009966/Logistik-.git](https://github.com/sa2009966/Logistik-.git)
    cd Logistik-
    ```

2.  **Preparar el entorno:**
    ```bash
    python3 -m venv env_dashboard
    source env_dashboard/bin/activate
    pip install -r requirements.txt
    ```

3.  **Configuración de Variables (`.env`):**
    Crea un archivo `.env` en la raíz (ignorado por Git) con tus credenciales:
    ```env
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=tu_password
    DB_NAME=db_bi_alex
    ALLOW_SELF_REGISTRATION=true
    ```

4.  **Correr la aplicación:**
    ```bash
    streamlit run app.py
    ```

---

## 🛡️ Seguridad y Buenas Prácticas
* **Zero Plain Text:** No se almacenan contraseñas en texto plano; todo pasa por un proceso de hashing robusto.
* **Protección de Rutas:** El Dashboard está bloqueado por un middleware de autenticación; sin sesión no hay acceso a la data.
* **Entornos Seguros:** Uso estricto de variables de entorno para proteger las llaves de la base de datos.

---

## 📊 Vistas del Sistema
1.  **Landing Page:** Presentación animada con CSS personalizado.
2.  **Módulo de Login:** Acceso seguro y registro de nuevos usuarios (opcional).
3.  **Dashboard BI:** Panel principal con filtros dinámicos, KPIs de ingresos y herramientas de exportación CSV.

