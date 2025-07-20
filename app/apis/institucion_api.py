from flask import Blueprint, jsonify, request, send_file
from app.database.connection import get_db_connection
import csv
import io
from datetime import datetime

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

@institucion_bp.route('/download', methods=['GET'])
def download_catalogo():
    """Descargar el catálogo de instituciones en formato CSV"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT i.*, t.nombre_tipo_institucion 
                FROM institucion i
                LEFT JOIN tipo_institucion t ON i.id_tipo_institucion = t.id_tipo_institucion
                ORDER BY i.nombre_institucion
            """)
            instituciones = cursor.fetchall()
            cursor.close()
            connection.close()

            # Crear un archivo CSV en memoria
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Escribir encabezados
            writer.writerow([
                'ID', 'Nombre', 'Tipo', 'Calle', 'Colonia', 'Municipio', 
                'Estado', 'Código Postal', 'Teléfono', 'Email', 'Fecha Registro'
            ])
            
            # Escribir datos
            for inst in instituciones:
                writer.writerow([
                    inst['id_institucion'],
                    inst['nombre_institucion'],
                    inst['nombre_tipo_institucion'],
                    inst['calle'] or '',
                    inst['colonia'] or '',
                    inst['municipio'] or '',
                    inst['estado'] or '',
                    inst['codigo_postal'] or '',
                    inst['telefono'] or '',
                    inst['email'] or '',
                    inst['fecha_registro'].strftime('%Y-%m-%d %H:%M:%S') if inst['fecha_registro'] else ''
                ])
            
            # Preparar el archivo para descarga
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode('utf-8')),
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'catalogo_instituciones_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
    except Exception as e:
        print(f"Error al generar el catálogo: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al generar el catálogo'}), 500