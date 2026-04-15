"""Casos de uso de autenticación y registro."""

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from core.auth import AuthSessionController
    from core.config import ConfiguracionAplicacion
    from core.security import SecurityHandler
    from services.audit_service import AuditService
    from services.contracts import IAuthRepository


class AuthService:
    """Gestiona login y registro con validaciones de negocio."""

    def __init__(
        self,
        repositorio: "IAuthRepository",
        security_handler: "SecurityHandler",
        sesion: "AuthSessionController",
        configuracion: "ConfiguracionAplicacion",
        audit_service: "AuditService",
    ) -> None:
        """Inicializa dependencias de autenticación.

        Args:
            repositorio: Puerto de usuarios.
            security_handler: Componente de hashing/validación de contraseñas.
            sesion: Gestor de sesión para Streamlit.
            configuracion: Configuración global.
            audit_service: Servicio de trazabilidad.
        """
        self._repo = repositorio
        self._security = security_handler
        self._sesion = sesion
        self._config = configuracion
        self._audit = audit_service

    def iniciar_sesion(
        self, nombre_usuario: str, contrasena: str, modo_demostracion: bool = False
    ) -> Tuple[bool, str]:
        """Autentica usuario y crea sesión.

        Args:
            nombre_usuario: Usuario ingresado.
            contrasena: Contraseña ingresada.
            modo_demostracion: ``True`` si aplica credencial fija demo.

        Returns:
            Tupla ``(exito, mensaje)``.
        """
        u = nombre_usuario.strip()
        if not u or not contrasena:
            return False, "Usuario y contraseña son obligatorios."
        if modo_demostracion:
            if u == "admin" and contrasena == "demo123":
                self._sesion.establecer_sesion_autenticada(u, 0)
                self._audit.registrar_evento(
                    usar_demo=True,
                    accion="LOGIN_OK",
                    detalle="Inicio de sesión exitoso en modo demo.",
                    usuario=u,
                )
                return True, ""
            self._audit.registrar_evento(
                usar_demo=True,
                accion="LOGIN_FAIL",
                detalle="Intento de login fallido en modo demo.",
                usuario=u or "desconocido",
                severidad="WARN",
            )
            return False, "Credenciales inválidas (modo demo: admin / demo123)."
        fila = self._repo.obtener_usuario_por_nombre(u)
        if not fila:
            self._audit.registrar_evento(
                usar_demo=False,
                accion="LOGIN_FAIL",
                detalle="Usuario no encontrado.",
                usuario=u or "desconocido",
                severidad="WARN",
            )
            return False, "Usuario o contraseña incorrectos."
        _uid, _name, pwd_hash = fila
        if not self._security.verificar_contrasena(contrasena, pwd_hash):
            self._audit.registrar_evento(
                usar_demo=False,
                accion="LOGIN_FAIL",
                detalle="Contraseña inválida.",
                usuario=u,
                severidad="WARN",
            )
            return False, "Usuario o contraseña incorrectos."
        self._sesion.establecer_sesion_autenticada(u, int(_uid))
        self._audit.registrar_evento(
            usar_demo=False,
            accion="LOGIN_OK",
            detalle="Inicio de sesión exitoso.",
            usuario=u,
        )
        return True, ""

    def registrar_usuario(
        self,
        nombre_usuario: str,
        contrasena: str,
        confirmacion: str,
        modo_demostracion: bool = False,
    ) -> Tuple[bool, str]:
        """Registra un nuevo usuario local.

        Args:
            nombre_usuario: Usuario deseado.
            contrasena: Contraseña principal.
            confirmacion: Confirmación de contraseña.
            modo_demostracion: ``True`` si se opera sin MySQL.

        Returns:
            Tupla ``(exito, mensaje)``.
        """
        if modo_demostracion:
            return False, "El registro no está disponible en modo demo (sin MySQL)."
        if not self._config.allow_self_registration:
            return False, "El registro público está deshabilitado."
        u = nombre_usuario.strip()
        if len(u) < 3:
            return False, "El usuario debe tener al menos 3 caracteres."
        if len(contrasena) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres."
        if contrasena != confirmacion:
            return False, "Las contraseñas no coinciden."
        try:
            ok = self._repo.crear_usuario(u, contrasena)
            if not ok:
                self._audit.registrar_evento(
                    usar_demo=False,
                    accion="REGISTER_FAIL",
                    detalle="Intento de registro con usuario existente.",
                    usuario=u,
                    severidad="WARN",
                )
                return False, "Ese nombre de usuario ya está registrado."
            self._audit.registrar_evento(
                usar_demo=False,
                accion="REGISTER_OK",
                detalle="Usuario registrado correctamente.",
                usuario=u,
            )
            return True, "Cuenta creada. Ya puede iniciar sesión."
        except Exception as e:
            self._audit.registrar_evento(
                usar_demo=False,
                accion="REGISTER_ERROR",
                detalle="Error inesperado durante registro.",
                usuario=u or "desconocido",
                severidad="ERROR",
            )
            return False, f"No se pudo registrar: {e}"
