"""Repositorio de administración de usuarios en memoria para modo demo/offline."""

from typing import List

import streamlit as st

from services.contracts import IUsuarioAdminRepository
from services.models import UsuarioInfo

_KEY_USUARIOS = "demo_usuarios_admin"

_USUARIOS_INICIALES: List[UsuarioInfo] = [
    UsuarioInfo(id_usuario=1, nombre_usuario="admin", rol="admin", creado_en="2026-01-01 00:00:00"),
    UsuarioInfo(id_usuario=2, nombre_usuario="analista1", rol="analista", creado_en="2026-01-02 00:00:00"),
    UsuarioInfo(id_usuario=3, nombre_usuario="coordinador", rol="analista", creado_en="2026-01-03 00:00:00"),
    UsuarioInfo(id_usuario=4, nombre_usuario="operador2", rol="operador", creado_en="2026-01-04 00:00:00"),
    UsuarioInfo(id_usuario=5, nombre_usuario="supervisor", rol="operador", creado_en="2026-01-05 00:00:00"),
]


class InMemoryUsuarioAdminRepository(IUsuarioAdminRepository):
    """Gestión de usuarios en session_state de Streamlit (sin base de datos)."""

    def _almacen(self) -> List[UsuarioInfo]:
        if _KEY_USUARIOS not in st.session_state:
            st.session_state[_KEY_USUARIOS] = [
                UsuarioInfo(
                    id_usuario=u.id_usuario,
                    nombre_usuario=u.nombre_usuario,
                    rol=u.rol,
                    creado_en=u.creado_en,
                )
                for u in _USUARIOS_INICIALES
            ]
        return st.session_state[_KEY_USUARIOS]  # type: ignore[return-value]

    def listar_usuarios(self) -> List[UsuarioInfo]:
        return list(self._almacen())

    def actualizar_rol(self, id_usuario: int, nuevo_rol: str) -> bool:
        almacen = self._almacen()
        for usuario in almacen:
            if usuario.id_usuario == id_usuario:
                st.session_state[_KEY_USUARIOS] = [
                    UsuarioInfo(
                        id_usuario=u.id_usuario,
                        nombre_usuario=u.nombre_usuario,
                        rol=nuevo_rol if u.id_usuario == id_usuario else u.rol,
                        creado_en=u.creado_en,
                    )
                    for u in almacen
                ]
                return True
        return False

    def eliminar_usuario(self, id_usuario: int) -> bool:
        almacen = self._almacen()
        nueva_lista = [u for u in almacen if u.id_usuario != id_usuario]
        if len(nueva_lista) == len(almacen):
            return False
        st.session_state[_KEY_USUARIOS] = nueva_lista
        return True
