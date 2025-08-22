from datetime import datetime, time
from app.models.solicitud import Solicitud
from app import db
from flask import Blueprint, request, redirect, url_for, flash, render_template
from flask_login import login_required, current_user
from app.models.laboratorio import Laboratorio
from app.models.institucion import Institucion
from app.utils.permissions import permission_required
from app.utils.notifications import notify_lab_admins_or_superadmins

solicitud_bp = Blueprint('solicitud', __name__, url_prefix='/solicitud')

@solicitud_bp.route('/solicitar/<int:id_laboratorio>', methods=['POST'])
@login_required
@permission_required('crear_solicitud')
def registrar_solicitud(id_laboratorio):
    try:
        data = request.form
        laboratorio = Laboratorio.query.get_or_404(id_laboratorio)
        
        # Validar datos requeridos
        campos_requeridos = ['id_institucion', 'id_tipo_solicitud', 'fecha', 'hora_inicio', 'hora_fin', 'razon', 'num_personas']
        for campo in campos_requeridos:
            if not data.get(campo):
                flash(f'El campo {campo.replace("_", " ").title()} es requerido', 'error')
                return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))
        
        # Validar que la fecha no sea en el pasado
        fecha_solicitud = datetime.strptime(data.get('fecha'), '%Y-%m-%d').date()
        if fecha_solicitud < datetime.now().date():
            flash('No puede seleccionar una fecha en el pasado', 'error')
            return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))
        
        # Validar horas
        hora_inicio = datetime.strptime(data.get('hora_inicio'), '%H:%M').time()
        hora_fin = datetime.strptime(data.get('hora_fin'), '%H:%M').time()
        if hora_inicio >= hora_fin:
            flash('La hora de inicio debe ser anterior a la hora de fin', 'error')
            return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))
        
        # Validar número de personas
        num_personas = int(data.get('num_personas'))
        if num_personas > laboratorio.capacidad:
            flash(f'El número de personas no puede exceder la capacidad del laboratorio ({laboratorio.capacidad})', 'error')
            return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))
        
        # Crear nueva solicitud
        nueva_solicitud = Solicitud(
            id_institucion=int(data.get('id_institucion')),
            id_estatus=1,  # 1 = Pendiente
            id_tipo_solicitud=int(data.get('id_tipo_solicitud')),
            id_insumo=int(data.get('id_insumo')) if data.get('id_insumo') else None,
            id_laboratorio=id_laboratorio,
            id_investigador=current_user.id if current_user.is_authenticated else None,
            razon=data.get('razon'),
            fecha_solicitud=fecha_solicitud,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            num_personas=num_personas,
            prioridad=data.get('prioridad', 'Normal'),
            # Campos de contacto (si no hay usuario autenticado)
            nombre_solicitante=data.get('nombre_solicitante') if not current_user.is_authenticated else None,
            email_solicitante=data.get('email_solicitante') if not current_user.is_authenticated else None,
            telefono_solicitante=data.get('telefono_solicitante') if not current_user.is_authenticated else None,
            fecha_creacion=datetime.now(),
            fecha_modificacion=datetime.now()
        )
        
        db.session.add(nueva_solicitud)
        db.session.commit()

        # Notificar a admin(es) de laboratorio, o a Super Admin si el lab no tiene admin
        try:
            notify_lab_admins_or_superadmins(
                lab_id=id_laboratorio,
                subject='Nueva solicitud de laboratorio',
                message=f'Se registró una solicitud para el laboratorio ID {id_laboratorio} el {fecha_solicitud}.'
            )
        except Exception:
            pass
        
        flash('Solicitud registrada correctamente. Recibirá una confirmación pronto.', 'success')
        return redirect(url_for('laboratorio_api.get_laboratorio_detalles', id=id_laboratorio))
        
    except ValueError as ve:
        db.session.rollback()
        flash('Error en el formato de los datos proporcionados', 'error')
        return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))
    except Exception as e:
        db.session.rollback()
        flash(f'Error al registrar la solicitud: {str(e)}', 'error')
        return redirect(url_for('laboratorio_api.solicitar_laboratorio', id_laboratorio=id_laboratorio))

@solicitud_bp.route('/mis-solicitudes')
@login_required
@permission_required('ver_solicitudes')
def mis_solicitudes():
    """Ver las solicitudes del usuario actual"""
    try:
        solicitudes = Solicitud.query.filter_by(id_investigador=current_user.id).order_by(Solicitud.fecha_creacion.desc()).all()
        return render_template('mis_solicitudes.html', solicitudes=solicitudes)
    except Exception as e:
        flash(f'Error al cargar las solicitudes: {str(e)}', 'error')
        return redirect(url_for('main.index'))

@solicitud_bp.route('/cancelar/<int:id_solicitud>')
@login_required
@permission_required('editar_solicitud')
def cancelar_solicitud(id_solicitud):
    """Cancelar una solicitud propia"""
    try:
        solicitud = Solicitud.query.get_or_404(id_solicitud)
        
        # Verificar que la solicitud pertenece al usuario actual
        if solicitud.id_investigador != current_user.id:
            flash('No tiene permisos para cancelar esta solicitud', 'error')
            return redirect(url_for('solicitud.mis_solicitudes'))
        
        # Solo se pueden cancelar solicitudes pendientes o en revisión
        if solicitud.id_estatus not in [1, 2]:  # 1=Pendiente, 2=En Revisión
            flash('Solo se pueden cancelar solicitudes pendientes o en revisión', 'error')
            return redirect(url_for('solicitud.mis_solicitudes'))
        
        solicitud.id_estatus = 5  # 5 = Cancelada
        solicitud.fecha_modificacion = datetime.now()
        
        db.session.commit()
        flash('Solicitud cancelada correctamente', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error al cancelar la solicitud: {str(e)}', 'error')
    
    return redirect(url_for('solicitud.mis_solicitudes'))