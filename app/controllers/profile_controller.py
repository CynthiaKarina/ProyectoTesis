from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app.models.user import User
from app import db
from app.utils.init_folders import init_upload_folders
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.area import Area
from flask_login import login_required, current_user
# Crear el Blueprint para el perfil
profile_bp = Blueprint('profile', __name__)

# Configuración para las imágenes de perfil
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/mi-perfil')
@login_required
def ver_perfil():
    user = current_user
    
    # Obtener información de roles y permisos
    from app.utils.permissions import PermissionManager
    user_permissions = []
    user_role_name = None
    is_user_admin = False
    permission_categories = {}
    
    try:
        user_permissions = PermissionManager.get_user_permissions(user.id_usuario)
        user_role_name = PermissionManager.get_user_role_name(user)
        is_user_admin = PermissionManager.is_admin(user)
        
        # Organizar permisos por categorías
        permission_categories = {
            'Administración': [],
            'Usuarios': [],
            'Roles y Permisos': [],
            'Laboratorios': [],
            'Áreas e Instituciones': [],
            'Solicitudes': [],
            'Perfil': [],
            'Otros': []
        }
        
        for permission in user_permissions:
            if 'admin' in permission.lower():
                permission_categories['Administración'].append(permission)
            elif 'usuario' in permission.lower():
                permission_categories['Usuarios'].append(permission)
            elif 'rol' in permission.lower() or 'permiso' in permission.lower():
                permission_categories['Roles y Permisos'].append(permission)
            elif 'laboratorio' in permission.lower():
                permission_categories['Laboratorios'].append(permission)
            elif 'area' in permission.lower() or 'institucion' in permission.lower():
                permission_categories['Áreas e Instituciones'].append(permission)
            elif 'solicitud' in permission.lower():
                permission_categories['Solicitudes'].append(permission)
            elif 'perfil' in permission.lower() or 'password' in permission.lower():
                permission_categories['Perfil'].append(permission)
            else:
                permission_categories['Otros'].append(permission)
        
        # Filtrar categorías vacías
        permission_categories = {k: v for k, v in permission_categories.items() if v}
    except Exception as e:
        current_app.logger.error(f"Error obteniendo permisos del usuario: {str(e)}")
        flash('Error al cargar información de permisos', 'warning')
        
    return render_template('perfil.html', 
                         user=user,
                         user_permissions=user_permissions,
                         user_role_name=user_role_name,
                         is_user_admin=is_user_admin,
                         permission_categories=permission_categories)


@profile_bp.route('/editar-perfil', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    user = current_user
    
    if request.method == 'POST':
        try:
           
            # Validar y limpiar el número de teléfono
            telefono = request.form.get('telefono', '').strip()
            telefono = ''.join(filter(str.isdigit, telefono))
            
            # Verificar longitud del teléfono
            if len(telefono) > 20:
                flash('El número de teléfono es demasiado largo', 'error')
                return render_template('editar_perfil.html')

            # Procesar imagen de perfil
            if 'ruta_imagen' in request.files:
                file = request.files['ruta_imagen']
                if file and file.filename and allowed_file(file.filename):
                    upload_folder = init_upload_folders()
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    unique_filename = f"{user.username}_{timestamp}_{filename}"
                    file_path = os.path.join(upload_folder, unique_filename)
                    
                    # Eliminar imagen anterior si existe
                    if user.ruta_imagen:
                        old_file_path = os.path.join(upload_folder, user.ruta_imagen)
                        try:
                            if os.path.exists(old_file_path):
                                os.remove(old_file_path)
                        except Exception as e:
                            current_app.logger.error(f"Error eliminando imagen anterior: {e}")
                    
                    # Guardar nueva imagen
                    file.save(file_path)
                    user.ruta_imagen = unique_filename

            # Actualizar otros campos
            user.email = request.form.get('email')
            user.nombre = request.form.get('nombre')
            user.apellido_paterno = request.form.get('apellido_paterno')
            user.apellido_materno = request.form.get('apellido_materno')
            user.telefono = telefono
            
            # Manejar id_institucion
            id_institucion = request.form.get('id_institucion')
            if id_institucion:
                user.id_institucion = int(id_institucion)
            else:
                user.id_institucion = None
            
            # Actualizar la sesión
            session['email'] = user.email
            session['nombre'] = user.nombre if user.nombre else user.username
            session['apellido_paterno'] = user.apellido_paterno
            session['apellido_materno'] = user.apellido_materno
            session['telefono'] = user.telefono
            session['id_institucion'] = user.id_institucion
            
            
            flash('Perfil actualizado exitosamente', 'success')
            return redirect(url_for('profile.ver_perfil'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error actualizando perfil: {str(e)}")
            flash(f'Error al actualizar el perfil: {str(e)}', 'error')
    else:
        # Asegurarse de que el usuario tenga la relación con el área cargada
        if user and user.id_area:
            user.area = Area.query.get(user.id_area)
        
        return render_template('editar_perfil.html', user=user)


@profile_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    try:
        # Obtener el usuario actual
        user = current_user
        
        if request.method == 'POST':
            # Obtener datos del formulario
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Validaciones básicas
            if not all([current_password, new_password, confirm_password]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('cambiar_password.html')
            
            # Verificar contraseña actual
            # Si la contraseña está hasheada, usar check_password_hash
            if user.password.startswith('pbkdf2:sha256:') or user.password.startswith('scrypt:'):
                password_valid = check_password_hash(user.password, current_password)
            else:
                # Para contraseñas en texto plano (compatibilidad hacia atrás)
                password_valid = user.password == current_password
            
            if not password_valid:
                flash('La contraseña actual es incorrecta', 'error')
                registrar_intento_fallido(user, 'contraseña_incorrecta')
                return render_template('cambiar_password.html')
            
            # Validar nueva contraseña
            is_valid, message = validar_password_avanzada(new_password)
            if not is_valid:
                flash(message, 'error')
                return render_template('cambiar_password.html')
            
            # Verificar que las contraseñas nuevas coincidan
            if new_password != confirm_password:
                flash('Las contraseñas nuevas no coinciden', 'error')
                return render_template('cambiar_password.html')
            
            # Verificar que la nueva contraseña sea diferente a la actual
            if current_password == new_password:
                flash('La nueva contraseña debe ser diferente a la actual', 'error')
                return render_template('cambiar_password.html')
            
            try:
                # Hashear y actualizar la contraseña
                user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
                user.fecha_modificacion = datetime.utcnow()
                
                db.session.commit()
                
                # Mensaje de éxito
                flash('Contraseña actualizada exitosamente. Tu cuenta ahora es más segura.', 'success')
                
                # Registrar el cambio en el log
                current_app.logger.info(f'Contraseña actualizada exitosamente para el usuario: {user.username}')
                
                # Opcional: Actualizar timestamp de último acceso
                session['password_changed'] = True
                
                return redirect(url_for('profile.ver_perfil'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Error al actualizar contraseña para {user.username}: {str(e)}')
                flash('Error interno al actualizar la contraseña. Por favor intente nuevamente.', 'error')
                return render_template('cambiar_password.html')
                
    except Exception as e:
        current_app.logger.error(f'Error general en cambiar_password: {str(e)}')
        flash('Ha ocurrido un error inesperado. Por favor intente nuevamente.', 'error')
        return redirect(url_for('profile.ver_perfil'))
    
    # Si es GET o hay algún error, mostrar el formulario
    return render_template('cambiar_password.html')

# Función auxiliar para validar contraseña avanzada
def validar_password_avanzada(password):
    """
    Valida que la contraseña cumpla con los requisitos de seguridad
    """
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 128:
        return False, "La contraseña es demasiado larga (máximo 128 caracteres)"
    
    # Verificar que no sea una contraseña común
    contraseñas_comunes = [
        '123456', 'password', '123456789', '12345678', '12345',
        '1234567', '1234567890', 'qwerty', 'abc123', 'password123',
        'admin', 'letmein', 'welcome', 'monkey', '1234'
    ]
    
    if password.lower() in contraseñas_comunes:
        return False, "La contraseña es demasiado común. Elige una más segura."
    
    # Verificar que no contenga solo espacios
    if password.isspace():
        return False, "La contraseña no puede contener solo espacios"
    
    # Verificar caracteres válidos (opcional - permitir caracteres especiales)
    import re
    if not re.match(r'^[\w\s!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]+$', password):
        return False, "La contraseña contiene caracteres no válidos"
    
    return True, "Contraseña válida"

# Función para registrar intentos fallidos mejorada
def registrar_intento_fallido(user, tipo_error):
    """
    Registra los intentos fallidos de cambio de contraseña con más detalle
    """
    try:
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        current_app.logger.warning(
            f'[{timestamp}] Intento fallido de cambio de contraseña - '
            f'Usuario: {user.username} (ID: {user.id_usuario}), '
            f'Email: {user.email}, '
            f'Tipo de error: {tipo_error}, '
            f'IP: {request.remote_addr if request else "N/A"}'
        )
        
        # Opcional: Incrementar contador de intentos fallidos
        # Esto podría usarse para implementar bloqueo temporal
        
    except Exception as e:
        current_app.logger.error(f'Error al registrar intento fallido: {str(e)}')

@profile_bp.route('/eliminar-imagen-perfil')
@login_required
def eliminar_imagen_perfil():
    user = current_user

    try:
        if user.ruta_imagen:
            # Eliminar archivo
            file_path = os.path.join(current_app.root_path, 'static', user.ruta_imagen)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Actualizar base de datos
            user.ruta_imagen = None
            db.session.commit()
            
            flash('Imagen de perfil eliminada exitosamente', 'success')
        else:
            flash('No hay imagen de perfil para eliminar', 'info')
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error eliminando imagen de perfil: {e}")
        flash('Error al eliminar la imagen de perfil', 'error')
    
    return redirect(url_for('profile.editar_perfil')) 

@profile_bp.route('/actualizar-area', methods=['POST'])
@login_required
def actualizar_area():
    try:
        data = request.get_json()
        id_area = data.get('id_area')
        
        user = current_user
        if user:
            user.id_area = id_area
            db.session.commit()
            session['id_area'] = id_area
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error actualizando área: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500 