from flask import Blueprint, render_template, request, jsonify
from app.models.area import Area
from app import db
from flask_login import current_user, login_required
from datetime import datetime
from app.utils.permissions import permission_required

admin_areas_bp = Blueprint('admin_areas', __name__)

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
        nombre_area = request.form.get('nombre_area') or request.json.get('nombre_area')
        usuario = current_user.nombre if current_user.is_authenticated else 'Desconocido'
        ahora = datetime.now()
        nueva_area = Area(
            nombre_area=nombre_area,
            creado_por=usuario,
            modificado_por=usuario,
            fecha_creacion=ahora,
            ultima_modificacion=ahora
        )
        db.session.add(nueva_area)
        db.session.commit()
        return jsonify({'mensaje': 'Área agregada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_areas_bp.route('/admin/areas/editar/<int:id>', methods=['PUT'])
@login_required
@permission_required('editar_area')
def editar_area(id):
    try:
        area = Area.query.get_or_404(id)
        data = request.get_json()
        area.nombre_area = data.get('nombre_area')
        area.modificado_por = current_user.nombre if current_user.is_authenticated else 'Desconocido'
        area.ultima_modificacion = datetime.now()
        db.session.commit()
        return jsonify({'mensaje': 'Área actualizada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@admin_areas_bp.route('/admin/areas/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_area')
def eliminar_area(id):
    try:
        area = Area.query.get_or_404(id)
        db.session.delete(area)
        db.session.commit()
        return jsonify({'mensaje': 'Área eliminada exitosamente'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 