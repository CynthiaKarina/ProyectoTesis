from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models.laboratorio import Laboratorio
from app.models.area import Area
from app.models.institucion import Institucion
from app.models.tipo_laboratorio import Tipo_Laboratorio
from app.models.user import User
from app import db
from sqlalchemy import or_
from app.utils.permissions import permission_required, any_permission_required

laboratorio_bp = Blueprint('laboratorio', __name__, url_prefix='/laboratorio')

@laboratorio_bp.route('/')
def index():
    """Renderiza la página principal de laboratorios"""
    try:
        current_app.logger.info('Accediendo a la página de laboratorios')
        
        # Obtener parámetros de filtrado
        search_query = request.args.get('search', '')
        area_id = request.args.get('area', '')
        status = request.args.get('status', '')
        institution_id = request.args.get('institution', '')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        if per_page not in [12, 24, 36]:
            per_page = 12

        # Construir la consulta base
        query = Laboratorio.query
        current_app.logger.info(f'Query base creada: {query}')

        # Aplicar filtros
        if search_query:
            query = query.filter(
                or_(
                    Laboratorio.nombre_laboratorio.ilike(f'%{search_query}%'),
                    Laboratorio.descripcion.ilike(f'%{search_query}%')
                )
            )
        
        if area_id:
            query = query.filter(Laboratorio.id_area == area_id)
        
        if status:
            query = query.filter(Laboratorio.disponibilidad == status)
        
        if institution_id:
            query = query.filter(Laboratorio.id_institucion == institution_id)

        # Obtener datos para los filtros
        areas = Area.query.all()
        institutions = Institucion.query.all()
        current_app.logger.info(f'Áreas encontradas: {len(areas)}')
        current_app.logger.info(f'Instituciones encontradas: {len(institutions)}')

        # Paginar resultados
        laboratorios = query.paginate(page=page, per_page=per_page, error_out=False)
        current_app.logger.info(f'Laboratorios encontrados: {laboratorios.total}')

        return render_template('laboratorio.html',
                            laboratorios=laboratorios,
                            areas=areas,
                            institutions=institutions,
                            search_query=search_query,
                            selected_area=area_id,
                            selected_status=status,
                            selected_institution=institution_id,
                            per_page=per_page,
                            current_page=page)
    except Exception as e:
        current_app.logger.error(f'Error al cargar los laboratorios: {str(e)}')
        flash(f'Error al cargar los laboratorios: {str(e)}', 'error')
        return redirect(url_for('home.index'))

@laboratorio_bp.route('/detalle/<int:id>')
def detalle(id):
    """Renderiza la página de detalle de un laboratorio"""
    try:
        laboratorio = Laboratorio.query.get_or_404(id)
        return render_template('laboratorio_detalle.html', laboratorio=laboratorio)
    except Exception as e:
        current_app.logger.error(f'Error al cargar el detalle del laboratorio: {str(e)}')
        flash(f'Error al cargar el detalle del laboratorio: {str(e)}', 'error')
        return redirect(url_for('laboratorio.index'))

@laboratorio_bp.route('/api/laboratorios', methods=['GET'])
def get_laboratorios():
    """API para obtener la lista de laboratorios"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = Laboratorio.query
    
    if search:
        query = query.filter(Laboratorio.nombre_laboratorio.ilike(f'%{search}%'))
    
    laboratorios = query.paginate(page=page, per_page=per_page)
    
    return jsonify({
        'success': True,
        'data': [lab.to_dict() for lab in laboratorios.items],
        'total': laboratorios.total,
        'pages': laboratorios.pages,
        'current_page': laboratorios.page
    })

@laboratorio_bp.route('/api/laboratorios/<int:id>', methods=['GET'])
def get_laboratorio(id):
    """API para obtener un laboratorio específico"""
    laboratorio = Laboratorio.query.get_or_404(id)
    return jsonify({
        'success': True,
        'data': laboratorio.to_dict()
    })

@laboratorio_bp.route('/api/laboratorios', methods=['POST'])
@login_required
@permission_required('crear_laboratorio')
def create_laboratorio():
    """API para crear un nuevo laboratorio"""
    data = request.get_json()
    
    try:
        laboratorio = Laboratorio(
            nombre_laboratorio=data['nombre_laboratorio'],
            descripcion=data.get('descripcion'),
            disponibilidad=data.get('disponibilidad', True),
            id_institucion=data.get('id_institucion'),
            id_area=data.get('id_area'),
            id_tipo_laboratorio=data.get('id_tipo_laboratorio'),
            id_encargado=data.get('id_encargado')
        )
        
        db.session.add(laboratorio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Laboratorio creado exitosamente',
            'data': laboratorio.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@laboratorio_bp.route('/api/laboratorios/<int:id>', methods=['PUT'])
@login_required
@permission_required('editar_laboratorio')
def update_laboratorio(id):
    """API para actualizar un laboratorio existente"""
    laboratorio = Laboratorio.query.get_or_404(id)
    data = request.get_json()
    
    try:
        laboratorio.nombre_laboratorio = data.get('nombre_laboratorio', laboratorio.nombre_laboratorio)
        laboratorio.descripcion = data.get('descripcion', laboratorio.descripcion)
        laboratorio.disponibilidad = data.get('disponibilidad', laboratorio.disponibilidad)
        laboratorio.id_institucion = data.get('id_institucion', laboratorio.id_institucion)
        laboratorio.id_area = data.get('id_area', laboratorio.id_area)
        laboratorio.id_tipo_laboratorio = data.get('id_tipo_laboratorio', laboratorio.id_tipo_laboratorio)
        laboratorio.id_encargado = data.get('id_encargado', laboratorio.id_encargado)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Laboratorio actualizado exitosamente',
            'data': laboratorio.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@laboratorio_bp.route('/api/laboratorios/<int:id>', methods=['DELETE'])
@login_required
@permission_required('eliminar_laboratorio')
def delete_laboratorio(id):
    """API para eliminar un laboratorio"""
    laboratorio = Laboratorio.query.get_or_404(id)
    
    try:
        db.session.delete(laboratorio)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Laboratorio eliminado exitosamente'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400

@laboratorio_bp.route('/api/laboratorios/search', methods=['GET'])
def search_laboratorios():
    """API para búsqueda de laboratorios (autocompletado)"""
    query = request.args.get('query', '')
    
    if not query:
        return jsonify({
            'success': True,
            'data': []
        })
    
    laboratorios = Laboratorio.query.filter(
        Laboratorio.nombre_laboratorio.ilike(f'%{query}%')
    ).limit(10).all()
    
    return jsonify({
        'success': True,
        'data': [{
            'id': lab.id_laboratorio,
            'nombre': lab.nombre_laboratorio
        } for lab in laboratorios]
    })

@laboratorio_bp.route('/solicitar/<int:id_laboratorio>')
@login_required
@permission_required('crear_solicitud')
def solicitar(id_laboratorio):
    """Renderiza la página de solicitud de un laboratorio"""
    try:
        laboratorio = Laboratorio.query.get_or_404(id_laboratorio)
        return render_template('solicitar_laboratorio.html', laboratorio=laboratorio)
    except Exception as e:
        current_app.logger.error(f'Error al cargar la página de solicitud: {str(e)}')
        flash(f'Error al cargar la página de solicitud: {str(e)}', 'error')
        return redirect(url_for('laboratorio.index'))