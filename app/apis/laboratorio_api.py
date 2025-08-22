from flask import Blueprint, jsonify, request, render_template
from app.database.connection import get_db_connection
from flask_login import login_required
from app.models.laboratorio import Laboratorio
from app.models.laboratorio_imagen import LaboratorioImagen
import os
from werkzeug.utils import secure_filename
from flask import current_app

# Crear el Blueprint para el API de laboratorio
laboratorio_api_bp = Blueprint('laboratorio_api', __name__)

UPLOAD_FOLDER = 'app/static/uploads/laboratorios'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@laboratorio_api_bp.route('/api/laboratorios', methods=['GET'])
def get_laboratorios():
    """Obtener todos los laboratorios"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.*, a.nombre_area, i.nombre_institucion 
                FROM laboratorio l
                LEFT JOIN area a ON l.id_area = a.id_area
                LEFT JOIN institucion i ON l.id_institucion = i.id_institucion
                ORDER BY l.nombre_laboratorio
            """)
            laboratorios = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'laboratorios': laboratorios}), 200
    except Exception as e:
        print(f"Error al obtener laboratorios: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener laboratorios'}), 500

@laboratorio_api_bp.route('/api/laboratorios/by_institucion/<int:id_institucion>', methods=['GET'])
def get_laboratorios_by_institucion(id_institucion: int):
    """Obtener laboratorios asociados a una institución específica, opcionalmente filtrados por área."""
    try:
        id_area = request.args.get('id_area')

        connection = get_db_connection()
        if not connection:
            return jsonify({'success': False, 'message': 'Error de conexión a la base de datos'}), 500

        cursor = connection.cursor(dictionary=True)

        # Detectar el nombre real de la columna de institución en la tabla 'laboratorio'
        column_name = None
        try:
            cursor.execute("SHOW COLUMNS FROM laboratorio LIKE 'id_institucion'")
            has_id_institucion = cursor.fetchone() is not None
            cursor.execute("SHOW COLUMNS FROM laboratorio LIKE 'institucion_id'")
            has_institucion_id = cursor.fetchone() is not None
            if has_id_institucion:
                column_name = 'id_institucion'
            elif has_institucion_id:
                column_name = 'institucion_id'
            else:
                return jsonify({'success': False, 'message': 'No se encontró columna de institución en la tabla laboratorio'}), 500
        except Exception as e_detect:
            print(f"Error detectando columnas de institución en laboratorio: {e_detect}")
            return jsonify({'success': False, 'message': 'Error al preparar la consulta de laboratorios'}), 500

        # Construir consulta usando el nombre de columna detectado
        query = (
            f"""
            SELECT l.id_laboratorio, l.nombre_laboratorio
            FROM laboratorio l
            WHERE l.{column_name} = %s
            """
        )
        params = [id_institucion]

        if id_area:
            query += " AND l.id_area = %s"
            params.append(id_area)

        query += " ORDER BY l.nombre_laboratorio"

        cursor.execute(query, params)
        labs = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({'success': True, 'laboratorios': labs}), 200
    except Exception as e:
        print(f"Error al obtener laboratorios por institución: {e}")
        return jsonify({'success': False, 'message': f'Error al obtener laboratorios por institución: {str(e)}'}), 500

@laboratorio_api_bp.route('/api/laboratorios/<int:id>', methods=['GET'])
def get_laboratorio(id):
    """Obtener un laboratorio específico por ID"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.*, a.nombre_area, i.nombre_institucion 
                FROM laboratorio l
                LEFT JOIN area a ON l.id_area = a.id_area
                LEFT JOIN institucion i ON l.institucion_id = i.id_institucion
                WHERE l.id_laboratorio = %s
            """, (id,))
            laboratorio = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if laboratorio:
                return jsonify({'success': True, 'laboratorio': laboratorio}), 200
            return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
    except Exception as e:
        print(f"Error al obtener el laboratorio: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener el laboratorio'}), 500

@laboratorio_api_bp.route('/api/laboratorios', methods=['POST'])
def create_laboratorio():
    """Crear un nuevo laboratorio con sus imágenes"""
    try:
        # Obtener los datos del formulario
        nombre_laboratorio = request.form.get('nombre_laboratorio')
        descripcion = request.form.get('descripcion')
        id_area = request.form.get('id_area')
        institucion_id = request.form.get('institucion_id')
        capacidad = request.form.get('capacidad')
        status = request.form.get('status')
        
        # Validar campos requeridos
        if not all([nombre_laboratorio, descripcion, id_area, institucion_id, capacidad, status]):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Insertar el laboratorio
            cursor.execute("""
                INSERT INTO laboratorio (nombre_laboratorio, descripcion, id_area, institucion_id, capacidad, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                nombre_laboratorio,
                descripcion,
                id_area,
                institucion_id,
                capacidad,
                status
            ))
            
            # Obtener el ID del laboratorio creado
            new_laboratorio_id = cursor.lastrowid
            
            # Procesar las imágenes si se enviaron
            if 'imagenes' in request.files:
                imagenes = request.files.getlist('imagenes')
                
                # Crear el directorio si no existe
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                for i, imagen in enumerate(imagenes):
                    if imagen and allowed_file(imagen.filename):
                        # Generar nombre seguro para el archivo
                        filename = secure_filename(f"lab_{new_laboratorio_id}_{i}_{imagen.filename}")
                        filepath = os.path.join(UPLOAD_FOLDER, filename)
                        
                        # Guardar el archivo
                        imagen.save(filepath)
                        
                        # Insertar la imagen en la base de datos
                        imagen_url = f"/static/uploads/laboratorios/{filename}"
                        es_principal = i == 0  # La primera imagen será la principal
                        
                        cursor.execute("""
                            INSERT INTO laboratorio_imagen (id_laboratorio, imagen_url, es_principal)
                            VALUES (%s, %s, %s)
                        """, (new_laboratorio_id, imagen_url, es_principal))
            
            connection.commit()
            
            # Obtener el laboratorio creado con sus imágenes
            cursor.execute("""
                SELECT l.*, a.nombre_area, i.nombre_institucion 
                FROM laboratorio l
                LEFT JOIN area a ON l.id_area = a.id_area
                LEFT JOIN institucion i ON l.institucion_id = i.id_institucion
                WHERE l.id_laboratorio = %s
            """, (new_laboratorio_id,))
            new_laboratorio = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'laboratorio': new_laboratorio}), 201
            
    except Exception as e:
        print(f"Error al crear el laboratorio: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al crear el laboratorio'}), 500

@laboratorio_api_bp.route('/api/laboratorios/<int:id>', methods=['PUT'])
def update_laboratorio(id):
    """Actualizar un laboratorio existente"""
    try:
        data = request.get_json()
        required_fields = ['nombre_laboratorio', 'descripcion', 'id_area', 'institucion_id', 'capacidad', 'status']
        
        if not all(field in data for field in required_fields):
            return jsonify({'success': False, 'message': 'Todos los campos son requeridos'}), 400

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                UPDATE laboratorio 
                SET nombre_laboratorio = %s,
                    descripcion = %s,
                    id_area = %s,
                    institucion_id = %s,
                    capacidad = %s,
                    status = %s
                WHERE id_laboratorio = %s
            """, (
                data['nombre_laboratorio'],
                data['descripcion'],
                data['id_area'],
                data['institucion_id'],
                data['capacidad'],
                data['status'],
                id
            ))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
                
            cursor.execute("SELECT * FROM laboratorio WHERE id_laboratorio = %s", (id,))
            updated_laboratorio = cursor.fetchone()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'laboratorio': updated_laboratorio}), 200
    except Exception as e:
        print(f"Error al actualizar el laboratorio: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar el laboratorio'}), 500

@laboratorio_api_bp.route('/api/laboratorios/<int:id>', methods=['DELETE'])
def delete_laboratorio(id):
    """Eliminar un laboratorio"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM laboratorio WHERE id_laboratorio = %s", (id,))
            connection.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
                
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'message': 'Laboratorio eliminado correctamente'}), 200
    except Exception as e:
        print(f"Error al eliminar el laboratorio: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al eliminar el laboratorio'}), 500

@laboratorio_api_bp.route('/api/laboratorios/search', methods=['GET'])
def search_laboratorios():
    """Buscar laboratorios por criterios"""
    try:
        search_query = request.args.get('q', '')
        id_area = request.args.get('id_area', '')
        status = request.args.get('status', '')
        institucion_id = request.args.get('institucion_id', '')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            query = """
                SELECT l.*, a.nombre_area, i.nombre_institucion 
                FROM laboratorio l
                LEFT JOIN area a ON l.id_area = a.id_area
                LEFT JOIN institucion i ON l.institucion_id = i.id_institucion
                WHERE 1=1
            """
            params = []

            if search_query:
                query += " AND (l.nombre_laboratorio LIKE %s OR l.descripcion LIKE %s)"
                params.extend([f'%{search_query}%', f'%{search_query}%'])
            
            if id_area:
                query += " AND l.id_area = %s"
                params.append(id_area)
            
            if status:
                query += " AND l.status = %s"
                params.append(status)
            
            if institucion_id:
                query += " AND l.institucion_id = %s"
                params.append(institucion_id)

            cursor.execute(query, params)
            laboratorios = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'laboratorios': laboratorios}), 200
    except Exception as e:
        print(f"Error al buscar laboratorios: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al buscar laboratorios'}), 500

@laboratorio_api_bp.route('/laboratorio/detalles/<int:id>')
def get_laboratorio_detalles(id):
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT l.*, a.nombre_area, i.nombre_institucion 
                FROM laboratorio l
                LEFT JOIN area a ON l.id_area = a.id_area
                LEFT JOIN institucion i ON l.id_institucion = i.id_institucion
                WHERE l.id_laboratorio = %s
            """, (id,))
            laboratorio = cursor.fetchone()
            cursor.close()
            connection.close()
            
            if laboratorio:
                # Convertir el resultado a un diccionario si no lo es ya
                if not isinstance(laboratorio, dict):
                    laboratorio = dict(zip([col[0] for col in cursor.description], laboratorio))
                
                return render_template('laboratorio_detalles.html', laboratorio=laboratorio)
            
            return jsonify({'success': False, 'message': 'Laboratorio no encontrado'}), 404
            
    except Exception as e:
        print(f"Error al obtener el laboratorio: {str(e)}")
        return jsonify({'success': False, 'message': f'Error al obtener el laboratorio: {str(e)}'}), 500

@laboratorio_api_bp.route('/api/laboratorios/<int:id>/imagenes', methods=['GET'])
def get_laboratorio_imagenes(id):
    """Obtener todas las imágenes de un laboratorio"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM laboratorio_imagen 
                WHERE id_laboratorio = %s 
                ORDER BY es_principal DESC, fecha_subida DESC
            """, (id,))
            imagenes = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify({'success': True, 'imagenes': imagenes}), 200
    except Exception as e:
        print(f"Error al obtener las imágenes: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al obtener las imágenes'}), 500

@laboratorio_api_bp.route('/api/laboratorio/imagen/<int:id_imagen>', methods=['DELETE'])
@login_required
def delete_laboratorio_imagen(id_imagen):
    """Eliminar una imagen de laboratorio"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Obtener información de la imagen antes de eliminarla
            cursor.execute("SELECT * FROM laboratorio_imagen WHERE id_imagen = %s", (id_imagen,))
            imagen = cursor.fetchone()
            
            if not imagen:
                return jsonify({'success': False, 'message': 'Imagen no encontrada'}), 404
            
            # Eliminar la imagen
            cursor.execute("DELETE FROM laboratorio_imagen WHERE id_imagen = %s", (id_imagen,))
            
            # Si era la imagen principal, establecer otra como principal
            if imagen['es_principal']:
                cursor.execute("""
                    UPDATE laboratorio_imagen 
                    SET es_principal = TRUE 
                    WHERE id_laboratorio = %s 
                    ORDER BY fecha_subida DESC 
                    LIMIT 1
                """, (imagen['id_laboratorio'],))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Eliminar el archivo físico
            if imagen['imagen_url']:
                filepath = os.path.join(current_app.root_path, imagen['imagen_url'].lstrip('/'))
                if os.path.exists(filepath):
                    os.remove(filepath)
            
            return jsonify({'success': True, 'message': 'Imagen eliminada correctamente'}), 200
            
    except Exception as e:
        print(f"Error al eliminar la imagen: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al eliminar la imagen'}), 500

@laboratorio_api_bp.route('/api/laboratorio/imagen/<int:id_imagen>/principal', methods=['PUT'])
@login_required
def set_imagen_principal(id_imagen):
    """Establecer una imagen como principal"""
    try:
        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            
            # Obtener información de la imagen
            cursor.execute("SELECT * FROM laboratorio_imagen WHERE id_imagen = %s", (id_imagen,))
            imagen = cursor.fetchone()
            
            if not imagen:
                return jsonify({'success': False, 'message': 'Imagen no encontrada'}), 404
            
            # Quitar la imagen principal actual
            cursor.execute("""
                UPDATE laboratorio_imagen 
                SET es_principal = FALSE 
                WHERE id_laboratorio = %s
            """, (imagen['id_laboratorio'],))
            
            # Establecer la nueva imagen principal
            cursor.execute("""
                UPDATE laboratorio_imagen 
                SET es_principal = TRUE 
                WHERE id_imagen = %s
            """, (id_imagen,))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            return jsonify({'success': True, 'message': 'Imagen principal actualizada correctamente'}), 200
            
    except Exception as e:
        print(f"Error al actualizar la imagen principal: {str(e)}")
        return jsonify({'success': False, 'message': 'Error al actualizar la imagen principal'}), 500