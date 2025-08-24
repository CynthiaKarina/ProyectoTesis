from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User
from app.models.laboratorio import Laboratorio
from app.models.laboratorio_admin import LaboratorioAdmin
from app import db
from app.utils.permissions import permission_required
from datetime import datetime
from app.models.role_request import RoleRequest
from app.utils.email_service import send_email
from app.utils.email_service import generate_approval_token, confirm_approval_token

admin_roles_bp = Blueprint('admin_roles', __name__)

@admin_roles_bp.route('/admin/roles')
@login_required
@permission_required('gestionar_roles')
def admin_roles():
    roles = Roles.query.all()
    permisos = Permiso.query.all()

    # Filtrado y paginación de solicitudes
    status = request.args.get('status', '')  # pendiente | aprobado | rechazado
    rtype = request.args.get('rtype', '')    # administrativo | admin_laboratorio
    page = max(int(request.args.get('page', 1) or 1), 1)
    per_page = max(min(int(request.args.get('per_page', 10) or 10), 50), 5)

    req_q = RoleRequest.query
    if status:
        req_q = req_q.filter(RoleRequest.status == status)
    if rtype:
        req_q = req_q.filter(RoleRequest.requested_role == rtype)
    total_requests = req_q.count()
    req_q = req_q.order_by(RoleRequest.created_at.desc())
    role_requests = req_q.offset((page - 1) * per_page).limit(per_page).all()
    # Precargar info de usuarios y laboratorios para la tabla
    user_ids = sorted({r.id_usuario for r in role_requests})
    lab_ids = sorted({r.id_laboratorio for r in role_requests if getattr(r, 'id_laboratorio', None)})
    users_map = {u.id_usuario: u for u in User.query.filter(User.id_usuario.in_(user_ids)).all()} if user_ids else {}
    labs_map = {l.id_laboratorio: l for l in Laboratorio.query.filter(Laboratorio.id_laboratorio.in_(lab_ids)).all()} if lab_ids else {}
    total_pages = (total_requests + per_page - 1) // per_page
    
    # Calcular estadísticas
    total_roles = len(roles)
    total_permisos_asignados = db.session.query(PermisoRol).count()
    total_usuarios_con_roles = db.session.query(User).filter(User.id_rol.isnot(None)).count()
    
    # Convertir roles a dict para serializar con información completa
    roles_dict = []
    for rol in roles:
        # Contar usuarios con este rol
        usuarios_con_rol = db.session.query(User).filter(User.id_rol == rol.id_rol).count()
        
        roles_dict.append({
            'id_rol': rol.id_rol,
            'nombre_rol': rol.nombre_rol,
            'descripcion': rol.descripcion,
            'usuarios_count': usuarios_con_rol,
            'permisos_rol': [
                {
                    'permiso': {
                        'id_permiso': pr.permiso.id_permiso,
                        'nombre_permiso': pr.permiso.nombre_permiso,
                        'descripcion': pr.permiso.descripcion
                    }
                } for pr in rol.permisos_rol
            ]
        })
    
    # Convertir permisos a dict
    permisos_dict = []
    for permiso in permisos:
        permisos_dict.append({
            'id_permiso': permiso.id_permiso,
            'nombre_permiso': permiso.nombre_permiso,
            'descripcion': permiso.descripcion
        })
    
    # Estadísticas para el template
    estadisticas = {
        'total_roles': total_roles,
        'total_permisos_asignados': total_permisos_asignados,
        'total_usuarios_con_roles': total_usuarios_con_roles
    }
    
    return render_template(
        'admin_roles.html',
        roles=roles,
        permisos=permisos,
        roles_json=roles_dict,
        permisos_json=permisos_dict,
        estadisticas=estadisticas,
        role_requests=role_requests,
        req_status_filter=status,
        req_rtype_filter=rtype,
        req_page=page,
        req_total_pages=total_pages,
        req_total=total_requests,
        req_per_page=per_page,
        users_map=users_map,
        labs_map=labs_map
    )


@admin_roles_bp.route('/admin/roles/role_request/approve_token/<token>', methods=['GET'])
def approve_with_token(token):
    """Aprobar/rechazar solicitud por enlace con token (sin login)."""
    data = confirm_approval_token(token, expiration_seconds=86400)
    if not data:
        flash('El enlace no es válido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))
    request_id = data.get('request_id')
    action = data.get('action')
    if action not in ['aprobar', 'rechazar', 'aprobar_asignar']:
        flash('Acción inválida en el enlace.', 'error')
        return redirect(url_for('auth.login'))
    # Reutilizar flujo existente
    return resolver_role_request(request_id, action)

# Aprobar/rechazar solicitudes de rol
@admin_roles_bp.route('/admin/roles/role_request/<int:request_id>/<action>', methods=['POST'])
@login_required
@permission_required('gestionar_roles')
def resolver_role_request(request_id, action):
    req = RoleRequest.query.get_or_404(request_id)
    if req.status != 'pendiente':
        flash('La solicitud ya fue atendida.', 'info')
        return redirect(url_for('admin_roles.admin_roles'))

    if action not in ['aprobar', 'rechazar', 'aprobar_asignar']:
        flash('Acción inválida.', 'error')
        return redirect(url_for('admin_roles.admin_roles'))

    req.status = 'aprobado' if action == 'aprobar' else 'rechazado'
    req.reviewed_at = datetime.utcnow()

    if action in ['aprobar', 'aprobar_asignar']:
        # Asignar rol correspondiente
        user = User.query.get(req.id_usuario)
        if not user:
            flash('Usuario no encontrado para la solicitud.', 'error')
            return redirect(url_for('admin_roles.admin_roles'))

        # Resolver id_rol por nombre exacto o alias
        def resolve_role_for_request(requested_role: str):
            aliases = {
                'administrativo': ['Gestor de Usuarios', 'Administrador', 'User_admin_leer'],
                'admin_laboratorio': ['Lab_Responsable', 'Gestor de Laboratorios'],
                'investigador': ['Investigador']
            }
            names = aliases.get(requested_role, [])
            if not names:
                return None
            return Roles.query.filter(Roles.nombre_rol.in_(names)).first()

        target_role = resolve_role_for_request(req.requested_role)
        if not target_role:
            # Fallback por búsqueda parcial
            if req.requested_role == 'administrativo':
                target_role = Roles.query.filter(Roles.nombre_rol.ilike('%admin%')).first()
            elif req.requested_role == 'admin_laboratorio':
                target_role = Roles.query.filter(Roles.nombre_rol.ilike('%laboratorio%')).first()
            elif req.requested_role == 'investigador':
                target_role = Roles.query.filter(Roles.nombre_rol.ilike('%investig%')).first()

        if target_role:
            # Política solicitada: el usuario solo tiene un rol; actualizar id_rol siempre
            try:
                from datetime import datetime
                user.id_rol = target_role.id_rol
                # Limpiar rol_adicional si existe el campo
                if hasattr(user, 'rol_adicional'):
                    user.rol_adicional = None
                # Actualizar marca de cambio para invalidar sesiones previas
                if hasattr(user, 'fecha_cambio'):
                    user.fecha_cambio = datetime.utcnow()
                db.session.commit()
                # Log de asignación de rol
                try:
                    from app.utils.audit import log_user_action
                    log_user_action(user.id_usuario, f'asignar_rol:{req.requested_role}', extra=f'request_id={req.id_request}')
                except Exception:
                    pass
                flash('Rol asignado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error asignando rol: {e}', 'error')
        else:
            flash('No se encontró un rol configurado que coincida con la solicitud.', 'warning')

        # Asignar como encargado del laboratorio si aplica
        try:
            if req.requested_role == 'admin_laboratorio' and req.id_laboratorio:
                lab = Laboratorio.query.get(req.id_laboratorio)
                if lab:
                    # Registrar también en la tabla puente (soporta múltiples admins)
                    exists = LaboratorioAdmin.query.filter_by(id_laboratorio=lab.id_laboratorio, id_usuario=user.id_usuario).first()
                    if not exists:
                        db.session.add(LaboratorioAdmin(id_laboratorio=lab.id_laboratorio, id_usuario=user.id_usuario))
                        db.session.commit()
                    # Asignación como encargado sola si se elige aprobar_asignar o si no hay encargado
                    should_assign = (action == 'aprobar_asignar') or (lab.id_encargado is None)
                    if should_assign:
                        lab.id_encargado = user.id_usuario
                        db.session.commit()
                        flash(f"Asignado como encargado del laboratorio '{lab.nombre_laboratorio}'.", 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al registrar admin de laboratorio: {e}', 'error')

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash('Error actualizando la solicitud.', 'error')

    # Enviar email de notificación al usuario solicitante
    try:
        user = User.query.get(req.id_usuario)
        if user and getattr(user, 'email', None):
            estado_txt = 'aprobada' if req.status == 'aprobado' else 'rechazada'
            # Determinar nombre de rol final asignado (si aprobado)
            try:
                nuevo_rol_nombre = user.roles.nombre_rol if user.roles else req.requested_role
            except Exception:
                nuevo_rol_nombre = req.requested_role
            detalle_lab = ''
            try:
                if req.requested_role == 'admin_laboratorio' and req.id_laboratorio:
                    lab = Laboratorio.query.get(req.id_laboratorio)
                    if lab:
                        detalle_lab = f"<p>Laboratorio asignado: {lab.nombre_laboratorio}</p>"
            except Exception:
                detalle_lab = ''

            extra_sesion = ''
            if req.status == 'aprobado':
                extra_sesion = "<p>Por seguridad, tu sesión actual fue cerrada y deberás iniciar sesión nuevamente para reflejar los nuevos permisos.</p>"

            try:
                from app.models.monthly_report import SystemKV
                subj = (SystemKV.query.get('email.role_request_result.subject') or SystemKV(key='email.role_request_result.subject', value='SIGRAL - Resultado de tu solicitud de rol')).value
                html_tmpl = (SystemKV.query.get('email.role_request_result.html') or SystemKV(key='email.role_request_result.html', value='<div style="font-family: Arial, sans-serif; line-height:1.6;"><h3>Resultado de tu solicitud de rol</h3><p>Hola {{ display_name }},</p><p>Tu solicitud para el rol <strong>{{ role_name }}</strong> ha sido <strong>{{ status }}</strong>.</p>{{ lab_name }}{{ session_notice }}<p style="color:#6b7280;font-size:12px">Este es un mensaje automático.</p></div>')).value
                display_name = (getattr(user, 'nombre', None) or user.username or '')
                html = (html_tmpl
                        .replace('{{ display_name }}', display_name)
                        .replace('{{ role_name }}', nuevo_rol_nombre or '')
                        .replace('{{ status }}', estado_txt or '')
                        .replace('{{ lab_name }}', detalle_lab or '')
                        .replace('{{ session_notice }}', extra_sesion or ''))
                send_email(subject=subj, to_email=user.email, html_body=html)
            except Exception:
                html = f"""
                <div style='font-family:Arial,sans-serif;line-height:1.6'>
                  <h3 style='margin:0 0 8px 0'>Resultado de tu solicitud de rol</h3>
                  <p>Hola {getattr(user, 'nombre', user.username) or user.username},</p>
                  <p>Tu solicitud para el rol <strong>{nuevo_rol_nombre}</strong> ha sido <strong>{estado_txt}</strong>.</p>
                  {detalle_lab}
                  {extra_sesion}
                  <p style='color:#6b7280;font-size:12px'>Este es un mensaje automático.</p>
                </div>
                """
                send_email(subject='SIGRAL - Resultado de tu solicitud de rol', to_email=user.email, html_body=html)
    except Exception as e:
        # No bloquear el flujo por fallo de correo
        try:
            print(f"Aviso: fallo enviando correo al usuario {req.id_usuario}: {e}")
        except Exception:
            pass

    return redirect(url_for('admin_roles.admin_roles'))

@admin_roles_bp.route('/admin/roles/crear', methods=['POST'])
@login_required
@permission_required('crear_rol')
def crear_rol():
    # Bloqueado por política: los roles son fijos y se gestionan por semillas
    flash('La creación de nuevos roles está deshabilitada por política del sistema.', 'warning')
    return redirect(url_for('admin_roles.admin_roles'))

@admin_roles_bp.route('/admin/roles/asignar_permisos', methods=['POST'])
@login_required
@permission_required('asignar_permisos')
def asignar_permisos():
    id_rol = request.form.get('id_rol')
    permisos_ids = request.form.getlist('permisos')
    # Eliminar permisos actuales
    PermisoRol.query.filter_by(id_rol=id_rol).delete()
    # Asignar nuevos permisos
    for id_permiso in permisos_ids:
        pr = PermisoRol(id_rol=id_rol, id_permiso=id_permiso)
        db.session.add(pr)
    db.session.commit()
    flash('Permisos actualizados', 'success')
    return redirect(url_for('admin_roles.admin_roles'))

@admin_roles_bp.route('/admin/roles/editar', methods=['POST'])
@login_required
@permission_required('editar_rol')
def editar_rol():
    id_rol = request.form.get('id_rol')
    descripcion = request.form.get('descripcion')
    rol = Roles.query.get_or_404(id_rol)
    # Política: no permitir renombrar roles; solo actualizar descripción
    rol.descripcion = descripcion
    db.session.commit()
    flash('Descripción del rol actualizada. El nombre del rol no se puede modificar.', 'success')
    return redirect(url_for('admin_roles.admin_roles'))

@admin_roles_bp.route('/admin/roles/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_rol')
def eliminar_rol(id):
    return jsonify({'error': 'La eliminación de roles está deshabilitada por política del sistema.'}), 403