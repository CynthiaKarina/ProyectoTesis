from flask import Blueprint, render_template, request, jsonify, current_app, session
from app.models.area import Area
from app import db
from flask_login import current_user, login_required
from datetime import datetime
from app.utils.permissions import permission_required

admin_areas_bp = Blueprint('admin_areas', __name__)


def get_current_user_name():
    """
    Función optimizada para obtener el nombre del usuario que inició sesión
    Prioriza: nombre_completo → nombre → username → sesión → fallback
    """
    try:
        current_app.logger.info(f"DEBUG: === OBTENIENDO NOMBRE DE USUARIO ===")
        
        # Caso 1: Usuario autenticado con Flask-Login
        if current_user and current_user.is_authenticated:
            current_app.logger.info(f"DEBUG: Usuario autenticado: {current_user}")
            current_app.logger.info(f"DEBUG: User ID: {current_user.id_usuario}")
            
            # Opción 1: Nombre completo (nombre + apellidos)
            if hasattr(current_user, 'nombre_completo') and current_user.nombre_completo.strip():
                result = current_user.nombre_completo.strip()
                current_app.logger.info(f"DEBUG: ✅ Usando nombre_completo: '{result}'")
                return result
            
            # Opción 2: Solo el nombre de pila
            if hasattr(current_user, 'nombre') and current_user.nombre and current_user.nombre.strip():
                result = current_user.nombre.strip()
                current_app.logger.info(f"DEBUG: ✅ Usando nombre: '{result}'")
                return result
            
            # Opción 3: Username como respaldo
            if hasattr(current_user, 'username') and current_user.username and current_user.username.strip():
                result = current_user.username.strip()
                current_app.logger.info(f"DEBUG: ✅ Usando username: '{result}'")
                return result
                
            current_app.logger.warning("DEBUG: Usuario autenticado pero sin nombre válido")
        
        # Caso 2: Usuario no autenticado, intentar obtener de sesión
        else:
            current_app.logger.info(f"DEBUG: current_user no disponible o no autenticado")
            current_app.logger.info(f"DEBUG: current_user = {current_user}")
            current_app.logger.info(f"DEBUG: session keys = {list(session.keys()) if session else 'No session'}")
        
        # Fallback 1: Datos de sesión Flask
        if 'nombre' in session and session['nombre'] and session['nombre'].strip():
            result = session['nombre'].strip()
            current_app.logger.info(f"DEBUG: ✅ Usando session['nombre']: '{result}'")
            return result
        
        # Fallback 2: Username de sesión
        if 'username' in session and session['username'] and session['username'].strip():
            result = session['username'].strip()
            current_app.logger.info(f"DEBUG: ✅ Usando session['username']: '{result}'")
            return result
        
        # Fallback 3: Obtener usuario por ID de sesión
        if 'user_id' in session and session['user_id']:
            try:
                from app.models.user import User
                user = User.query.get(session['user_id'])
                if user:
                    current_app.logger.info(f"DEBUG: Usuario encontrado por session['user_id']: {user.username}")
                    if user.nombre_completo.strip():
                        result = user.nombre_completo.strip()
                        current_app.logger.info(f"DEBUG: ✅ Usando BD nombre_completo: '{result}'")
                        return result
                    elif user.nombre and user.nombre.strip():
                        result = user.nombre.strip()
                        current_app.logger.info(f"DEBUG: ✅ Usando BD nombre: '{result}'")
                        return result
                    elif user.username.strip():
                        result = user.username.strip()
                        current_app.logger.info(f"DEBUG: ✅ Usando BD username: '{result}'")
                        return result
            except Exception as e:
                current_app.logger.error(f"DEBUG: Error obteniendo usuario por session ID: {e}")
        
        # Último recurso: Valor por defecto
        current_app.logger.warning("DEBUG: ⚠️ Usando valor por defecto: 'Sistema'")
        return 'Sistema'
        
    except Exception as e:
        current_app.logger.error(f"ERROR CRÍTICO en get_current_user_name: {str(e)}")
        return 'Sistema'

@admin_areas_bp.route('/admin/areas')
@login_required
@permission_required('gestionar_areas')
def index():
    areas = Area.query.all()
    return render_template('admin_areas.html', areas=areas)

@admin_areas_bp.route('/admin/areas/<int:id>')
@login_required
@permission_required('gestionar_areas')
def get_area(id):
    area = Area.query.get_or_404(id)
    return jsonify({
        'id_area': area.id_area,
        'nombre_area': area.nombre_area,
        'creado_por': area.creado_por,
        'fecha_creacion': area.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S') if area.fecha_creacion else None,
        'ultima_modificacion': area.ultima_modificacion.strftime('%Y-%m-%d %H:%M:%S') if area.ultima_modificacion else None,
        'modificado_por': area.modificado_por
    })

@admin_areas_bp.route('/admin/areas/agregar', methods=['POST'])
@login_required
@permission_required('crear_area')
def agregar_area():
    try:
        current_app.logger.info("=== INICIANDO CREACIÓN DE ÁREA ===")
        nombre_area = request.form.get('nombre_area') or (request.json.get('nombre_area') if request.is_json else None)
        current_app.logger.info(f"📝 Nombre del área: '{nombre_area}'")
        
        # Validar que el nombre no esté vacío
        if not nombre_area or not nombre_area.strip():
            current_app.logger.error("❌ Nombre de área vacío")
            return jsonify({'error': 'El nombre del área es obligatorio'}), 400
        
        # Verificar si ya existe un área con ese nombre
        area_existente = Area.query.filter_by(nombre_area=nombre_area.strip()).first()
        if area_existente:
            current_app.logger.warning(f"⚠️ Área ya existe: {nombre_area}")
            return jsonify({'error': f'Ya existe un área con el nombre "{nombre_area}"'}), 400
        
        # Obtener el nombre del usuario logueado (solo para creación)
        usuario_creador = get_current_user_name()
        current_app.logger.info(f"👤 Usuario creador: '{usuario_creador}'")
        
        # Validación final de seguridad
        if not usuario_creador or not usuario_creador.strip():
            usuario_creador = 'Sistema'
            current_app.logger.warning(f"⚠️ Forzando usuario creador a: '{usuario_creador}'")
        
        # Crear nueva área usando el método de clase seguro
        nueva_area = Area.crear_nueva(
            nombre_area=nombre_area,
            creado_por=usuario_creador
        )
        
        current_app.logger.info(f"✅ Área creada exitosamente:")
        current_app.logger.info(f"   - Nombre: '{nueva_area.nombre_area}'")
        current_app.logger.info(f"   - Creado por: '{nueva_area.creado_por}'")
        current_app.logger.info(f"   - Modificado por: '{nueva_area.modificado_por}'")
        
        # Guardar en la base de datos
        db.session.add(nueva_area)
        db.session.commit()
        
        current_app.logger.info("🎉 Área guardada en base de datos exitosamente")
        return jsonify({
            'mensaje': f'Área "{nueva_area.nombre_area}" creada exitosamente por {nueva_area.creado_por}',
            'area': {
                'id_area': nueva_area.id_area,
                'nombre_area': nueva_area.nombre_area,
                'creado_por': nueva_area.creado_por,
                'modificado_por': nueva_area.modificado_por
            }
        })
        
    except ValueError as ve:
        current_app.logger.error(f"❌ Error de validación: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"💥 ERROR CRÍTICO en agregar_area: {str(e)}")
        return jsonify({'error': f'Error al crear área: {str(e)}'}), 500

@admin_areas_bp.route('/admin/areas/editar/<int:id>', methods=['PUT'])
@login_required
@permission_required('editar_area')
def editar_area(id):
    try:
        area = Area.query.get_or_404(id)
        data = request.get_json()
        
        nuevo_nombre = data.get('nombre_area')
        if not nuevo_nombre or not nuevo_nombre.strip():
            return jsonify({'error': 'El nombre del área es obligatorio'}), 400
        
        # Obtener el usuario que modifica (solo para modificación, NO se toca creado_por)
        modificador = get_current_user_name()
        if not modificador or modificador.strip() == '':
            modificador = 'Administrador'
        
        # Usar el método de actualización segura
        area.actualizar(
            nombre_area=nuevo_nombre,
            modificado_por=modificador
        )
        
        db.session.commit()
        return jsonify({'mensaje': 'Área actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar área: {str(e)}'}), 400

@admin_areas_bp.route('/admin/areas/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_area')
def eliminar_area(id):
    try:
        area = Area.query.get_or_404(id)
        
        # Verificar si el área tiene usuarios asignados
        if hasattr(area, 'usuarios') and area.usuarios:
            usuarios_count = len(area.usuarios)
            return jsonify({
                'error': f'No se puede eliminar el área porque tiene {usuarios_count} usuario(s) asignado(s)'
            }), 400
        
        # Verificar si el área tiene laboratorios asignados
        if hasattr(area, 'laboratorios') and area.laboratorios:
            laboratorios_count = len(area.laboratorios)
            return jsonify({
                'error': f'No se puede eliminar el área porque tiene {laboratorios_count} laboratorio(s) asignado(s)'
            }), 400
        
        area_nombre = area.nombre_area  # Guardar para el mensaje
        db.session.delete(area)
        db.session.commit()
        return jsonify({'mensaje': f'Área "{area_nombre}" eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar área: {str(e)}'}), 400 