from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User
from app import db
from app.utils.permissions import permission_required, admin_required

admin_permisos_bp = Blueprint('admin_permisos', __name__)

@admin_permisos_bp.route('/admin/permisos')
@login_required
@permission_required('gestionar_permisos')
def admin_permisos():
    roles = Roles.query.all()
    permisos = Permiso.query.all()
    
    # Calcular estadísticas
    total_permisos = len(permisos)
    total_roles = len(roles)
    total_asignaciones = db.session.query(PermisoRol).count()
    total_usuarios_con_permisos = db.session.query(User).join(Roles).join(PermisoRol).distinct().count()
    
    # Calcular permisos más utilizados
    permisos_uso = db.session.query(
        Permiso.nombre_permiso,
        db.func.count(PermisoRol.id_permiso_rol).label('uso_count')
    ).join(PermisoRol).group_by(Permiso.id_permiso).order_by(
        db.func.count(PermisoRol.id_permiso_rol).desc()
    ).limit(5).all()
    
    # Convertir roles a dict para serializar
    roles_dict = []
    for rol in roles:
        roles_dict.append({
            'id_rol': rol.id_rol,
            'nombre_rol': rol.nombre_rol,
            'descripcion': rol.descripcion,
            'permisos_count': len(rol.permisos_rol),
            'usuarios_count': len(rol.usuarios)
        })
    
    # Preparar permisos con información de roles asignados
    permisos_con_roles = []
    for permiso in permisos:
        roles_asignados = [pr.id_rol for pr in permiso.permisos_rol]
        permiso.roles_asignados = roles_asignados
        permiso.roles_count = len(roles_asignados)
        permisos_con_roles.append(permiso)
    
    return render_template(
        'admin_permisos.html',
        roles=roles,
        permisos=permisos_con_roles,
        roles_json=roles_dict,
        total_permisos=total_permisos,
        total_roles=total_roles,
        total_asignaciones=total_asignaciones,
        total_usuarios_con_permisos=total_usuarios_con_permisos,
        permisos_uso=permisos_uso
    )

@admin_permisos_bp.route('/admin/permisos/crear', methods=['POST'])
@login_required
@permission_required('crear_permiso')
def crear_permiso():
    nombre_permiso = request.form.get('nombre_permiso')
    descripcion = request.form.get('descripcion')
    if not nombre_permiso:
        flash('El nombre del permiso es obligatorio', 'error')
        return redirect(url_for('admin_permisos.admin_permisos'))
    # Verificar que no exista
    if Permiso.query.filter_by(nombre_permiso=nombre_permiso).first():
        flash('Ya existe un permiso con ese nombre', 'error')
        return redirect(url_for('admin_permisos.admin_permisos'))
    nuevo_permiso = Permiso(nombre_permiso=nombre_permiso, descripcion=descripcion)
    db.session.add(nuevo_permiso)
    db.session.commit()
    flash('Permiso creado exitosamente', 'success')
    return redirect(url_for('admin_permisos.admin_permisos'))

@admin_permisos_bp.route('/admin/permisos/asignar', methods=['POST'])
@login_required
@permission_required('asignar_permisos')
def asignar_permisos():
    # Verificar si es una asignación individual (AJAX) o masiva (formulario)
    if request.is_json:
        # Asignación individual desde la matriz
        data = request.get_json()
        rol_id = data.get('rol_id')
        permiso_id = data.get('permiso_id')
        asignar = data.get('asignar', False)
        
        if not rol_id or not permiso_id:
            return jsonify({'error': 'Faltan parámetros requeridos'}), 400
        
        # Verificar que el rol y permiso existan
        rol = Roles.query.get(rol_id)
        permiso = Permiso.query.get(permiso_id)
        
        if not rol or not permiso:
            return jsonify({'error': 'Rol o permiso no encontrado'}), 404
        
        if asignar:
            # Verificar si ya existe la asignación
            existing = PermisoRol.query.filter_by(id_rol=rol_id, id_permiso=permiso_id).first()
            if not existing:
                pr = PermisoRol(id_rol=rol_id, id_permiso=permiso_id)
                db.session.add(pr)
                mensaje = f'Permiso "{permiso.nombre_permiso}" asignado al rol "{rol.nombre_rol}"'
            else:
                mensaje = 'El permiso ya estaba asignado'
        else:
            # Eliminar la asignación
            PermisoRol.query.filter_by(id_rol=rol_id, id_permiso=permiso_id).delete()
            mensaje = f'Permiso "{permiso.nombre_permiso}" removido del rol "{rol.nombre_rol}"'
        
        db.session.commit()
        return jsonify({'success': True, 'mensaje': mensaje})
    
    else:
        # Asignación masiva desde formulario
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
        return redirect(url_for('admin_permisos.admin_permisos'))

@admin_permisos_bp.route('/admin/permisos/editar', methods=['POST'])
@login_required
@permission_required('editar_permiso')
def editar_permiso():
    id_permiso = request.form.get('id_permiso')
    nombre_permiso = request.form.get('nombre_permiso')
    descripcion = request.form.get('descripcion')
    
    if not id_permiso or not nombre_permiso:
        flash('ID del permiso y nombre son obligatorios', 'error')
        return redirect(url_for('admin_permisos.admin_permisos'))
    
    permiso = Permiso.query.get_or_404(id_permiso)
    
    # Verificar que no exista otro permiso con el mismo nombre
    existing = Permiso.query.filter(Permiso.nombre_permiso == nombre_permiso, Permiso.id_permiso != id_permiso).first()
    if existing:
        flash('Ya existe otro permiso con ese nombre', 'error')
        return redirect(url_for('admin_permisos.admin_permisos'))
    
    permiso.nombre_permiso = nombre_permiso
    permiso.descripcion = descripcion
    
    db.session.commit()
    flash('Permiso actualizado exitosamente', 'success')
    return redirect(url_for('admin_permisos.admin_permisos'))

@admin_permisos_bp.route('/admin/permisos/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_permiso')
def eliminar_permiso(id):
    permiso = Permiso.query.get_or_404(id)
    # Verificar si está en uso
    if PermisoRol.query.filter_by(id_permiso=id).first():
        return jsonify({'error': 'No se puede eliminar un permiso que está en uso'}), 400
    db.session.delete(permiso)
    db.session.commit()
    return jsonify({'success': True, 'mensaje': 'Permiso eliminado'}) 