"""Casos de uso de administración: gestión de usuarios y asignación de roles."""

from typing import TYPE_CHECKING, Dict, List, Tuple

from services.contracts import IUsuarioAdminRepository
from services.models import UsuarioInfo

if TYPE_CHECKING:
    from services.audit_service import AuditService


class AdminService:
    """Gestiona el CRUD de usuarios con soporte para modo demo y MySQL.

    Sigue el mismo patrón Dict-strategy que LogisticaService y AuditService:
    ``{usar_demo: repositorio}`` para conmutar entre implementaciones sin if/else.
    """

    def __init__(
        self,
        repos_por_modo: Dict[bool, IUsuarioAdminRepository],
        audit_service: "AuditService",
    ) -> None:
        """Inicializa el servicio de administración.

        Args:
            repos_por_modo: Mapa ``{usar_demo: repositorio}`` para MySQL y demo.
            audit_service: Servicio de trazabilidad.
        """
        self._repos = repos_por_modo
        self._audit = audit_service

    def _repo(self, usar_demo: bool) -> IUsuarioAdminRepository:
        return self._repos[usar_demo]

    def listar_usuarios(self, usar_demo: bool) -> List[UsuarioInfo]:
        """Lista todos los usuarios del sistema.

        Args:
            usar_demo: ``True`` para fuente en memoria; ``False`` para MySQL.

        Returns:
            Lista de ``UsuarioInfo`` ordenada por id.
        """
        return self._repo(usar_demo).listar_usuarios()

    def actualizar_rol(
        self,
        usar_demo: bool,
        id_usuario: int,
        nuevo_rol: str,
        quien_cambia: str,
    ) -> Tuple[bool, str]:
        """Cambia el rol de un usuario.

        Args:
            usar_demo: Modo de operación.
            id_usuario: ID del usuario a modificar.
            nuevo_rol: Rol destino.
            quien_cambia: Usuario administrador que realiza el cambio.

        Returns:
            Tupla ``(exito, mensaje)``.
        """
        try:
            ok = self._repo(usar_demo).actualizar_rol(id_usuario, nuevo_rol)
            if not ok:
                return False, f"No se encontró el usuario con id {id_usuario}."
            self._audit.registrar_evento(
                usar_demo=usar_demo,
                accion="ROL_ACTUALIZADO",
                detalle=f"Rol del usuario id={id_usuario} cambiado a '{nuevo_rol}'.",
                usuario=quien_cambia,
                contexto={"id_usuario": str(id_usuario), "nuevo_rol": nuevo_rol},
            )
            return True, f"Rol actualizado a '{nuevo_rol}' correctamente."
        except Exception as e:
            self._audit.registrar_evento(
                usar_demo=usar_demo,
                accion="ROL_ERROR",
                detalle=f"Error al actualizar rol del usuario id={id_usuario}: {e}",
                usuario=quien_cambia,
                severidad="ERROR",
            )
            return False, f"No se pudo actualizar el rol: {e}"

    def eliminar_usuario(
        self,
        usar_demo: bool,
        id_usuario: int,
        quien_elimina: str,
    ) -> Tuple[bool, str]:
        """Elimina un usuario del sistema.

        Args:
            usar_demo: Modo de operación.
            id_usuario: ID del usuario a eliminar.
            quien_elimina: Usuario administrador que ejecuta la acción.

        Returns:
            Tupla ``(exito, mensaje)``.
        """
        try:
            ok = self._repo(usar_demo).eliminar_usuario(id_usuario)
            if not ok:
                return False, f"No se encontró el usuario con id {id_usuario}."
            self._audit.registrar_evento(
                usar_demo=usar_demo,
                accion="USUARIO_ELIMINADO",
                detalle=f"Usuario id={id_usuario} eliminado del sistema.",
                usuario=quien_elimina,
                severidad="WARN",
                contexto={"id_usuario": str(id_usuario)},
            )
            return True, "Usuario eliminado correctamente."
        except Exception as e:
            self._audit.registrar_evento(
                usar_demo=usar_demo,
                accion="ELIMINAR_ERROR",
                detalle=f"Error al eliminar usuario id={id_usuario}: {e}",
                usuario=quien_elimina,
                severidad="ERROR",
            )
            return False, f"No se pudo eliminar el usuario: {e}"
