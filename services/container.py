"""Composición raíz: ensambla dependencias entre capas (DI centralizada)."""

from dataclasses import dataclass

import streamlit as st

from core.auth import AuthSessionController
from core.config import ConfiguracionAplicacion
from core.security import SecurityHandler
from database.audit_repository import MysqlAuditRepository
from database.connection import GestorConexionMySQL
from database.repository import LogistikRepository
from services.alert_manager import AlertManager
from services.analytics import AnalyticsService
from services.audit_service import AuditService
from services.auth_service import AuthService
from services.contracts import (
    IAuditRepository,
    IAuthRepository,
    IBootstrapRepository,
    ITransaccionesDataSource,
)
from services.csv_loader import CsvDataLoaderService
from services.dashboard_service import DashboardService
from services.data_sources import DemoTransaccionesDataSource, MysqlTransaccionesDataSource
from services.demo_data import DemoDataStore
from services.in_memory_audit_repository import InMemoryAuditRepository
from services.logistica_service import LogisticaService
from services.report_exporters import ExcelReportExporter
from services.report_service import ReportService
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
    auditoria_mysql: IAuditRepository
    auditoria_demo: IAuditRepository
    sesion: AuthSessionController
    audit: AuditService
    auth: AuthService
    demo: DemoDataStore
    logistica: LogisticaService
    analytics: AnalyticsService
    alert_manager: AlertManager
    csv_loader: CsvDataLoaderService
    dashboard: DashboardService
    reportes: ReportService
    graficos: RenderizadorGraficosBi


def fabricar_contenedor() -> ContenedorAplicacion:
    """Crea el grafo de dependencias contra puertos (interfaces/ABCs)."""
    configuracion = ConfiguracionAplicacion()
    gestor_mysql = GestorConexionMySQL(configuracion)
    security_handler = SecurityHandler()
    repositorio_concreto = LogistikRepository(gestor_mysql, security_handler, configuracion)
    auditoria_mysql: IAuditRepository = MysqlAuditRepository(gestor_mysql)
    auditoria_demo: IAuditRepository = InMemoryAuditRepository()
    audit_service = AuditService({False: auditoria_mysql, True: auditoria_demo})
    repo_auth: IAuthRepository = repositorio_concreto
    repo_bootstrap: IBootstrapRepository = repositorio_concreto
    fuente_mysql: ITransaccionesDataSource = MysqlTransaccionesDataSource(repositorio_concreto)
    sesion = AuthSessionController()
    auth = AuthService(repo_auth, security_handler, sesion, configuracion, audit_service)
    demo_store = DemoDataStore()
    fuente_demo: ITransaccionesDataSource = DemoTransaccionesDataSource(demo_store)
    logistica = LogisticaService({True: fuente_demo, False: fuente_mysql}, audit_service)
    analytics = AnalyticsService()
    alert_manager = AlertManager()
    csv_loader = CsvDataLoaderService()
    dashboard = DashboardService(analytics, csv_loader, logistica, alert_manager, audit_service)
    reportes = ReportService(ExcelReportExporter(), audit_service)
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
        auditoria_mysql=auditoria_mysql,
        auditoria_demo=auditoria_demo,
        sesion=sesion,
        audit=audit_service,
        auth=auth,
        demo=demo_store,
        logistica=logistica,
        analytics=analytics,
        alert_manager=alert_manager,
        csv_loader=csv_loader,
        dashboard=dashboard,
        reportes=reportes,
        graficos=graficos,
    )


def obtener_contenedor() -> ContenedorAplicacion:
    """Acceso al contenedor inyectado en la sesión de Streamlit (tras app.principal)."""
    c = st.session_state.get("_contenedor")
    if c is None:
        raise RuntimeError("Contenedor de aplicación no inicializado.")
    return c
