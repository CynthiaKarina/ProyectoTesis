from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.database.connection import get_db_connection
from app.utils.permissions import permission_required

# Crear el Blueprint para el API de institución
institucion_bp = Blueprint('institucion', __name__, url_prefix='/api/institucion')

@institucion_bp.route('/', methods=['GET'])
def get_instituciones():
    """Obtener todas las instituciones"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_institucion, nombre_institucion FROM institucion ORDER BY nombre_institucion")
            instituciones = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'instituciones': instituciones}), 200
        # Fallback si no hay conexión
        return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    except Exception as e:
        print(f"Error al obtener instituciones: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener instituciones'}), 500

@institucion_bp.route('/<int:id>', methods=['GET'])
def get_institucion(id):
    """Obtener una institución específica por ID"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_institucion, nombre_institucion FROM institucion WHERE id_institucion = %s", (id,))
            institucion = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if institucion:
                return jsonify({'success': True, 'institucion': institucion}), 200
            return jsonify({'success': False, 'message': 'Institución no encontrada'}), 404
    except Exception as e:
        print(f"Error al obtener la institución: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener la institución'}), 500

@institucion_bp.route('/', methods=['POST'])
@login_required
@permission_required('crear_institucion')
def create_institucion():
    """Crear una nueva institución"""
    try:
        data = request.get_json()
        if not data or 'nombre_institucion' not in data:
            return jsonify({'success': False, 'message': 'Nombre de institución requerido'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT INTO institucion (nombre_institucion) VALUES (%s)", (data['nombre_institucion'],))
            connection.commit()
            
            new_institucion_id = cursor.lastrowid
            cursor.execute("SELECT id_institucion, nombre_institucion FROM institucion WHERE id_institucion = %s", (new_institucion_id,))
            new_institucion = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'institucion': new_institucion}), 201
    except Exception as e:
        print(f"Error al crear la institución: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al crear la institución'}), 500

@institucion_bp.route('/<int:id>', methods=['PUT'])
@login_required
@permission_required('editar_institucion')
def update_institucion(id):
    """Actualizar una institución existente"""
    try:
        data = request.get_json()
        if not data or 'nombre_institucion' not in data:
            return jsonify({'success': False, 'message': 'Nombre de institución requerido'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("UPDATE institucion SET nombre_institucion = %s WHERE id_institucion = %s", 
                         (data['nombre_institucion'], id))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Institución no encontrada'}), 404
                
            cursor.execute("SELECT id_institucion, nombre_institucion FROM institucion WHERE id_institucion = %s", (id,))
            updated_institucion = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'institucion': updated_institucion}), 200
    except Exception as e:
        print(f"Error al actualizar la institución: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar la institución'}), 500

@institucion_bp.route('/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_institucion')
def delete_institucion(id):
    """Eliminar una institución"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM institucion WHERE id_institucion = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Institución no encontrada'}), 404
                
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'message': 'Institución eliminada correctamente'}), 200
    except Exception as e:
        print(f"Error al eliminar la institución: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al eliminar la institución'}), 500