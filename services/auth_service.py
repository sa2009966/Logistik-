"""Casos de uso de autenticación y registro (orquesta repositorio + seguridad + sesión)."""

from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from core.auth import AuthSessionController
    from core.config import ConfiguracionAplicacion
    from core.security import SecurityHandler
    from services.contracts import IAuthRepository


class AuthService:
    def __init__(
        self,
        repositorio: "IAuthRepository",
        security_handler: "SecurityHandler",
        sesion: "AuthSessionController",
        configuracion: "ConfiguracionAplicacion",
    ) -> None:
        self._repo = repositorio
        self._security = security_handler
        self._sesion = sesion
        self._config = configuracion

    def iniciar_sesion(
        self, nombre_usuario: str, contrasena: str, modo_demostracion: bool = False
    ) -> Tuple[bool, str]:
        u = nombre_usuario.strip()
        if not u or not contrasena:
            return False, "Usuario y contraseña son obligatorios."
        if modo_demostracion:
            if u == "admin" and contrasena == "demo123":
                self._sesion.establecer_sesion_autenticada(u, 0)
                return True, ""
            return False, "Credenciales inválidas (modo demo: admin / demo123)."
        fila = self._repo.obtener_usuario_por_nombre(u)
        if not fila:
            return False, "Usuario o contraseña incorrectos."
        _uid, _name, pwd_hash = fila
        if not self._security.verificar_contrasena(contrasena, pwd_hash):
            return False, "Usuario o contraseña incorrectos."
        self._sesion.establecer_sesion_autenticada(u, int(_uid))
        return True, ""

    def registrar_usuario(
        self,
        nombre_usuario: str,
        contrasena: str,
        confirmacion: str,
        modo_demostracion: bool = False,
    ) -> Tuple[bool, str]:
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
                return False, "Ese nombre de usuario ya está registrado."
            return True, "Cuenta creada. Ya puede iniciar sesión."
        except Exception as e:
            return False, f"No se pudo registrar: {e}"
