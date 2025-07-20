from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User
from app import db
from app.utils.permissions import permission_required

admin_roles_bp = Blueprint('admin_roles', __name__)

@admin_roles_bp.route('/admin/roles')
@login_required
@permission_required('gestionar_roles')
def admin_roles():
    roles = Roles.query.all()
    permisos = Permiso.query.all()
    
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
        estadisticas=estadisticas
    )

@admin_roles_bp.route('/admin/roles/crear', methods=['POST'])
@login_required
@permission_required('crear_rol')
def crear_rol():
    nombre_rol = request.form.get('nombre_rol')
    descripcion = request.form.get('descripcion')
    if not nombre_rol:
        flash('El nombre del rol es obligatorio', 'error')
        return redirect(url_for('admin_roles.admin_roles'))
    nuevo_rol = Roles(nombre_rol=nombre_rol, descripcion=descripcion)
    db.session.add(nuevo_rol)
    db.session.commit()
    flash('Rol creado exitosamente', 'success')
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
    nombre_rol = request.form.get('nombre_rol')
    descripcion = request.form.get('descripcion')
    if not nombre_rol:
        flash('El nombre del rol es obligatorio', 'error')
        return redirect(url_for('admin_roles.admin_roles'))
    rol = Roles.query.get_or_404(id_rol)
    rol.nombre_rol = nombre_rol
    rol.descripcion = descripcion
    db.session.commit()
    flash('Rol actualizado exitosamente', 'success')
    return redirect(url_for('admin_roles.admin_roles'))

@admin_roles_bp.route('/admin/roles/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_rol')
def eliminar_rol(id):
    rol = Roles.query.get_or_404(id)
    # Verificar si está en uso
    usuarios_con_rol = db.session.query(User).filter(User.id_rol == id).count()
    if usuarios_con_rol > 0:
        return jsonify({'error': 'No se puede eliminar un rol que tiene usuarios asignados'}), 400
    # Eliminar permisos del rol
    PermisoRol.query.filter_by(id_rol=id).delete()
    db.session.delete(rol)
    db.session.commit()
    return jsonify({'success': True, 'mensaje': 'Rol eliminado correctamente'}) 