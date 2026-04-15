"""Composición raíz: ensambla dependencias entre capas (DI centralizada)."""

from dataclasses import dataclass

import streamlit as st

from core.auth import AuthSessionController
from core.config import ConfiguracionAplicacion
from core.security import SecurityHandler
from database.connection import GestorConexionMySQL
from database.repository import LogistikRepository
from services.analytics import AnalyticsService
from services.auth_service import AuthService
from services.contracts import IAuthRepository, IBootstrapRepository, ITransaccionesDataSource
from services.csv_loader import CsvDataLoaderService
from services.dashboard_service import DashboardService
from services.data_sources import DemoTransaccionesDataSource, MysqlTransaccionesDataSource
from services.demo_data import DemoDataStore
from services.logistica_service import LogisticaService
from ui.charts import (
    GraficoBarrasIngresosServicio,
    GraficoPastelParticipacionEstado,
    GraficoTendenciaIngresos,
    RenderizadorGraficosBi,
)


@dataclass
class ContenedorAplicacion:
    """Referencias compartidas a servicios y adaptadores de infraestructura."""

    configuracion: ConfiguracionAplicacion
    bootstrap_repo: IBootstrapRepository
    transacciones_mysql: ITransaccionesDataSource
    transacciones_demo: ITransaccionesDataSource
    sesion: AuthSessionController
    auth: AuthService
    demo: DemoDataStore
    logistica: LogisticaService
    analytics: AnalyticsService
    csv_loader: CsvDataLoaderService
    dashboard: DashboardService
    graficos: RenderizadorGraficosBi


def fabricar_contenedor() -> ContenedorAplicacion:
    """Crea el grafo de dependencias contra puertos (interfaces/ABCs)."""
    configuracion = ConfiguracionAplicacion()
    gestor_mysql = GestorConexionMySQL(configuracion)
    security_handler = SecurityHandler()
    repositorio_concreto = LogistikRepository(gestor_mysql, security_handler, configuracion)
    repo_auth: IAuthRepository = repositorio_concreto
    repo_bootstrap: IBootstrapRepository = repositorio_concreto
    fuente_mysql: ITransaccionesDataSource = MysqlTransaccionesDataSource(repositorio_concreto)
    sesion = AuthSessionController()
    auth = AuthService(repo_auth, security_handler, sesion, configuracion)
    demo_store = DemoDataStore()
    fuente_demo: ITransaccionesDataSource = DemoTransaccionesDataSource(demo_store)
    logistica = LogisticaService({True: fuente_demo, False: fuente_mysql})
    analytics = AnalyticsService()
    csv_loader = CsvDataLoaderService()
    dashboard = DashboardService(analytics, csv_loader, logistica)
    graficos = RenderizadorGraficosBi(
        [
            GraficoTendenciaIngresos(),
            GraficoBarrasIngresosServicio(),
            GraficoPastelParticipacionEstado(),
        ]
    )
    return ContenedorAplicacion(
        configuracion=configuracion,
        bootstrap_repo=repo_bootstrap,
        transacciones_mysql=fuente_mysql,
        transacciones_demo=fuente_demo,
        sesion=sesion,
        auth=auth,
        demo=demo_store,
        logistica=logistica,
        analytics=analytics,
        csv_loader=csv_loader,
        dashboard=dashboard,
        graficos=graficos,
    )


def obtener_contenedor() -> ContenedorAplicacion:
    """Acceso al contenedor inyectado en la sesión de Streamlit (tras app.principal)."""
    c = st.session_state.get("_contenedor")
    if c is None:
        raise RuntimeError("Contenedor de aplicación no inicializado.")
    return c
