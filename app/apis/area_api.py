from flask import Blueprint, jsonify, request
from app.database.connection import get_db_connection

# Crear el Blueprint para el API de área
area_api_bp = Blueprint('area_api', __name__, url_prefix='/api/area')

@area_api_bp.route('/', methods=['GET'])
def get_areas():
    """Obtener todas las áreas"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_area, nombre_area FROM area ORDER BY nombre_area")
            areas = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'areas': areas}), 200
        # Fallback si no hay conexión
        return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500
    except Exception as e:
        print(f"Error al obtener áreas: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener áreas'}), 500

@area_api_bp.route('/<int:id>', methods=['GET'])
def get_area(id):
    """Obtener un área específica por ID"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id_area, nombre_area FROM area WHERE id_area = %s", (id,))
            area = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if area:
                return jsonify({'success': True, 'area': area}), 200
            return jsonify({'success': False, 'message': 'Área no encontrada'}), 404
    except Exception as e:
        print(f"Error al obtener el área: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener el área'}), 500

@area_api_bp.route('/', methods=['POST'])
def create_area():
    """Crear una nueva área"""
    try:
        data = request.get_json()
        if not data or 'nombre_area' not in data:
            return jsonify({'success': False, 'message': 'Nombre de área requerido'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("INSERT INTO area (nombre_area) VALUES (%s)", (data['nombre_area'],))
            connection.commit()
            
            new_area_id = cursor.lastrowid
            cursor.execute("SELECT id_area, nombre_area FROM area WHERE id_area = %s", (new_area_id,))
            new_area = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'area': new_area}), 201
    except Exception as e:
        print(f"Error al crear el área: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al crear el área'}), 500

@area_api_bp.route('/<int:id>', methods=['PUT'])
def update_area(id):
    """Actualizar un área existente"""
    try:
        data = request.get_json()
        if not data or 'nombre_area' not in data:
            return jsonify({'success': False, 'message': 'Nombre de área requerido'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("UPDATE area SET nombre_area = %s WHERE id_area = %s", 
                         (data['nombre_area'], id))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Área no encontrada'}), 404
                
            cursor.execute("SELECT id_area, nombre_area FROM area WHERE id_area = %s", (id,))
            updated_area = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'area': updated_area}), 200
    except Exception as e:
        print(f"Error al actualizar el área: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar el área'}), 500

@area_api_bp.route('/<int:id>', methods=['DELETE'])
def delete_area(id):
    """Eliminar un área"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM area WHERE id_area = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Área no encontrada'}), 404
                
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'message': 'Área eliminada correctamente'}), 200
    except Exception as e:
        print(f"Error al eliminar el área: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al eliminar el área'}), 500
    