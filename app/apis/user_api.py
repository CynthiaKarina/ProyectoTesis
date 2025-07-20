from flask import Blueprint, jsonify, request, current_app
from app.models.area import Area
from app.models.user import User
from app import db
from werkzeug.security import generate_password_hash
from datetime import datetime

# Crear el Blueprint para la API de usuario
user_api_bp = Blueprint('user_api', __name__)

@user_api_bp.route('/api/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        return jsonify({
            'success': True,
            'users': [{
                'id_usuario': user.id_usuario,
                'nombre': user.nombre,
                'apellido_paterno': user.apellido_paterno,
                'apellido_materno': user.apellido_materno,
                'email': user.email,
                'username': user.username,
                'telefono': user.telefono,
                'id_institucion': user.id_institucion,
                'id_rol': user.id_rol,
                'ruta_imagen': user.ruta_imagen,
                'activo': user.activo,
                'id_area': user.id_area
            } for user in users]
        })
    except Exception as e:
        current_app.logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_api_bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'success': True,
            'user': {
                'id_usuario': user.id_usuario,
                'nombre': user.nombre,
                'apellido_paterno': user.apellido_paterno,
                'apellido_materno': user.apellido_materno,
                'email': user.email,
                'username': user.username,
                'telefono': user.telefono,
                'id_institucion': user.id_institucion,
                'id_rol': user.id_rol,
                'ruta_imagen': user.ruta_imagen,
                'activo': user.activo,
                'id_area': user.id_area
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error obteniendo usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_api_bp.route('/api/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        
        # Validaciones básicas
        if not all(k in data for k in ('username', 'email', 'password')):
            return jsonify({'success': False, 'message': 'Faltan campos requeridos'}), 400
            
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'success': False, 'message': 'El usuario ya existe'}), 400
            
        # Crear nuevo usuario
        new_user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            nombre=data.get('nombre'),
            apellido_paterno=data.get('apellido_paterno'),
            apellido_materno=data.get('apellido_materno'),
            telefono=data.get('telefono'),
            id_institucion=data.get('id_institucion'),
            id_rol=data.get('id_rol'),
            ruta_imagen=data.get('ruta_imagen'),
            activo=data.get('activo', True),
            id_area=data.get('id_area')
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario creado exitosamente',
            'user_id': new_user.id_usuario
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_api_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Actualizar campos permitidos
        allowed_fields = [
            'email', 'nombre', 'apellido_paterno', 'apellido_materno', 
            'telefono', 'id_institucion', 'id_rol', 
            'ruta_imagen', 'activo', 'id_area'
        ]
        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])
        
        if 'password' in data:
            user.password = generate_password_hash(data['password'])
            user.ultima_actualizacion_password = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error actualizando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@user_api_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Usuario eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error eliminando usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    
@user_api_bp.route('/api/users/<int:user_id>/area', methods=['PUT'])
def update_user_area(user_id):
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'id_area' not in data:
            return jsonify({
                'success': False,
                'message': 'El campo id_area es requerido'
            }), 400
        
        # Verificar si el área existe
        area = Area.query.get(data['id_area'])
        if not area:
            return jsonify({
                'success': False,
                'message': 'El área especificada no existe'
            }), 404
        
        user.id_area = data['id_area']
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Área del usuario actualizada exitosamente',
            'area': {
                'id_area': area.id_area,
                'nombre_area': area.nombre_area
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error actualizando área del usuario: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500