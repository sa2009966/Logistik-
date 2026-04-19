"""Vista de administración: gestión de usuarios y asignación de roles."""

import streamlit as st

from core.constants import ConstantesNegocio
from services.container import obtener_contenedor


def mostrar_panel_admin() -> None:
    """Renderiza el panel de administración de usuarios (solo para rol 'admin')."""
    contenedor = obtener_contenedor()
    usar_demo = st.session_state.get("use_demo_mode", False)
    usuario_actual = contenedor.sesion.obtener_usuario_actual()

    st.subheader("Gestión de usuarios y roles")

    if usar_demo:
        st.info("Modo demo activo: los cambios se guardan en memoria y se perderán al cerrar sesión.")

    try:
        usuarios = contenedor.admin.listar_usuarios(usar_demo)
    except Exception as e:
        st.error(f"No se pudo cargar la lista de usuarios: {e}")
        return

    if not usuarios:
        st.info("No hay usuarios registrados.")
        return

    st.caption(f"{len(usuarios)} usuario(s) registrado(s) en el sistema.")

    # ------------------------------------------------------------------ #
    # Tabla editable de roles                                              #
    # ------------------------------------------------------------------ #
    st.markdown("#### Tabla de usuarios")

    for usuario in usuarios:
        es_el_mismo = usuario.nombre_usuario == usuario_actual

        with st.container():
            col_id, col_nombre, col_rol, col_accion = st.columns([1, 3, 3, 2])

            col_id.markdown(f"`{usuario.id_usuario}`")
            col_nombre.markdown(
                f"**{usuario.nombre_usuario}**"
                + (" _(tú)_" if es_el_mismo else "")
            )

            rol_index = (
                ConstantesNegocio.ROLES.index(usuario.rol)
                if usuario.rol in ConstantesNegocio.ROLES
                else 0
            )
            nuevo_rol = col_rol.selectbox(
                "Rol",
                ConstantesNegocio.ROLES,
                index=rol_index,
                key=f"rol_select_{usuario.id_usuario}",
                label_visibility="collapsed",
                disabled=es_el_mismo,
            )

            with col_accion:
                if not es_el_mismo:
                    if nuevo_rol != usuario.rol:
                        if st.button(
                            "Guardar rol",
                            key=f"guardar_rol_{usuario.id_usuario}",
                            use_container_width=True,
                        ):
                            ok, msg = contenedor.admin.actualizar_rol(
                                usar_demo,
                                usuario.id_usuario,
                                nuevo_rol,
                                usuario_actual,
                            )
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                    else:
                        if st.button(
                            "Eliminar",
                            key=f"eliminar_{usuario.id_usuario}",
                            use_container_width=True,
                            type="secondary",
                        ):
                            st.session_state[f"confirmar_eliminar_{usuario.id_usuario}"] = True

                    if st.session_state.get(f"confirmar_eliminar_{usuario.id_usuario}"):
                        st.warning(
                            f"¿Eliminar a **{usuario.nombre_usuario}**? Esta acción no se puede deshacer."
                        )
                        c_si, c_no = st.columns(2)
                        if c_si.button(
                            "Sí, eliminar",
                            key=f"si_eliminar_{usuario.id_usuario}",
                            type="primary",
                        ):
                            ok, msg = contenedor.admin.eliminar_usuario(
                                usar_demo, usuario.id_usuario, usuario_actual
                            )
                            st.session_state.pop(f"confirmar_eliminar_{usuario.id_usuario}", None)
                            if ok:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)
                        if c_no.button("Cancelar", key=f"no_eliminar_{usuario.id_usuario}"):
                            st.session_state.pop(f"confirmar_eliminar_{usuario.id_usuario}", None)
                            st.rerun()
                else:
                    col_accion.caption("_(tu cuenta)_")

        st.divider()

    # ------------------------------------------------------------------ #
    # Crear usuario nuevo (solo MySQL)                                     #
    # ------------------------------------------------------------------ #
    st.markdown("#### Crear usuario nuevo")

    if usar_demo:
        st.info("La creación de usuarios no está disponible en modo demo (sin MySQL).")
    else:
        with st.form("form_crear_usuario_admin", clear_on_submit=True):
            nuevo_nombre = st.text_input("Nombre de usuario")
            nueva_contrasena = st.text_input("Contraseña", type="password")
            confirmacion = st.text_input("Confirmar contraseña", type="password")
            rol_nuevo_usuario = st.selectbox("Rol inicial", ConstantesNegocio.ROLES)
            crear = st.form_submit_button("Crear usuario", use_container_width=True)

        if crear:
            ok, msg = contenedor.auth.registrar_usuario(
                nuevo_nombre,
                nueva_contrasena,
                confirmacion,
                modo_demostracion=False,
            )
            if ok:
                # Asignar el rol seleccionado (por defecto registrar_usuario crea con rol 'usuario')
                usuarios_actualizados = contenedor.admin.listar_usuarios(usar_demo=False)
                usuario_creado = next(
                    (u for u in usuarios_actualizados if u.nombre_usuario == nuevo_nombre.strip()),
                    None,
                )
                if usuario_creado and rol_nuevo_usuario != "usuario":
                    contenedor.admin.actualizar_rol(
                        usar_demo=False,
                        id_usuario=usuario_creado.id_usuario,
                        nuevo_rol=rol_nuevo_usuario,
                        quien_cambia=usuario_actual,
                    )
                st.success(f"Usuario '{nuevo_nombre.strip()}' creado con rol '{rol_nuevo_usuario}'.")
                st.rerun()
            else:
                st.error(msg)
