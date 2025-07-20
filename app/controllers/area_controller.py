from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from app.models.area import Area
from app import db
from flask_login import login_required, current_user
from app.utils.permissions import permission_required

area_bp = Blueprint('area', __name__)

@area_bp.route('/admin/areas')
@login_required
@permission_required('gestionar_areas')
def admin_areas():
    # Obtener todas las áreas de la base de datos
    areas = Area.query.all()
    return render_template('admin_areas.html', areas=areas)

@area_bp.route('/admin/areas/agregar', methods=['POST'])
@login_required
@permission_required('crear_area')
def agregar_area():
    try:
        nombre_area = request.form.get('nombre_area')
        
        nueva_area = Area(nombre_area=nombre_area)
        db.session.add(nueva_area)
        db.session.commit()
        
        return jsonify({'mensaje': 'Área agregada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@area_bp.route('/admin/areas/editar/<int:id>', methods=['PUT'])
@login_required
@permission_required('editar_area')
def editar_area(id):
    try:
        area = Area.query.get_or_404(id)
        data = request.get_json()
        
        area.nombre_area = data.get('nombre_area', area.nombre_area)
        
        db.session.commit()
        return jsonify({'mensaje': 'Área actualizada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@area_bp.route('/admin/areas/eliminar/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_area')
def eliminar_area(id):
    try:
        area = Area.query.get_or_404(id)
        db.session.delete(area)
        db.session.commit()
        return jsonify({'mensaje': 'Área eliminada exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 