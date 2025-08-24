from datetime import datetime, time
from app.models.solicitud import Solicitud
from app import db
from flask import Blueprint, request, redirect, url_for, flash, render_template, make_response
from flask_login import login_required, current_user
from app.models.laboratorio import Laboratorio
from app.models.institucion import Institucion
from app.utils.permissions import permission_required, has_admin_access
from app.utils.notifications import notify_lab_admins_or_superadmins
from sqlalchemy import or_
import io
import csv
from openpyxl import Workbook

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
    """Ver las solicitudes del usuario actual con filtros y exportación"""
    try:
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, int(request.args.get('per_page', 15)))
        status_raw = (request.args.get('status') or '').strip()
        desde_raw = (request.args.get('desde') or '').strip()
        hasta_raw = (request.args.get('hasta') or '').strip()
        q_text = (request.args.get('q') or '').strip()

        query = Solicitud.query.filter_by(id_investigador=current_user.id)
        if status_raw:
            try:
                query = query.filter(Solicitud.id_estatus == int(status_raw))
            except ValueError:
                pass
        if desde_raw:
            try:
                query = query.filter(Solicitud.fecha_creacion >= datetime.strptime(desde_raw, '%Y-%m-%d'))
            except ValueError:
                pass
        if hasta_raw:
            try:
                hasta_dt = datetime.strptime(hasta_raw, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                query = query.filter(Solicitud.fecha_creacion <= hasta_dt)
            except ValueError:
                pass
        if q_text:
            query = (query.join(Laboratorio, Laboratorio.id_laboratorio == Solicitud.id_laboratorio, isouter=True)
                          .filter(or_(Solicitud.razon.ilike(f'%{q_text}%'),
                                      Laboratorio.nombre_laboratorio.ilike(f'%{q_text}%'))))

        query = query.order_by(Solicitud.fecha_creacion.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        status_options = [
            {'id': 1, 'label': 'Pendiente'},
            {'id': 2, 'label': 'En Revisión'},
            {'id': 3, 'label': 'Aprobada'},
            {'id': 4, 'label': 'Rechazada'},
            {'id': 5, 'label': 'Cancelada'},
            {'id': 6, 'label': 'Completada'},
        ]

        # Marcar notificaciones vistas
        try:
            from app.models.role_request import RoleRequest
            latest_resp = (db.session.query(RoleRequest)
                           .filter(RoleRequest.id_usuario==current_user.id,
                                   RoleRequest.status.in_(['aprobado','rechazado']))
                           .order_by(RoleRequest.reviewed_at.desc().nullslast(), RoleRequest.created_at.desc())
                           .first())
            if latest_resp:
                from flask import session as flask_session
                flask_session['seen_role_response_id'] = latest_resp.id_request
        except Exception:
            pass

        return render_template('mis_solicitudes.html',
                               solicitudes=pagination.items,
                               pagination=pagination,
                               status_options=status_options,
                               current_filters={'status': status_raw, 'desde': desde_raw, 'hasta': hasta_raw, 'q': q_text, 'per_page': per_page})
    except Exception as e:
        flash(f'Error al cargar las solicitudes: {str(e)}', 'error')
        return redirect(url_for('home.index'))


@solicitud_bp.route('/mis-solicitudes/export/xlsx')
@login_required
@permission_required('ver_solicitudes')
def mis_solicitudes_export_xlsx():
    """Exporta las solicitudes del mes actual del usuario a XLSX y las entrega como descarga."""
    try:
        from app.utils.reports import generate_user_month_report
        path = generate_user_month_report(current_user.id)
        if not path:
            return make_response('No se pudo generar el reporte', 500)
        with open(path, 'rb') as f:
            data = f.read()
        resp = make_response(data)
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        resp.headers['Content-Disposition'] = 'attachment; filename=mis_solicitudes_mes.xlsx'
        return resp
    except Exception as e:
        return make_response(f'Error: {e}', 500)

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


@solicitud_bp.route('/institucion')
@login_required
@permission_required('ver_todas_solicitudes')
def solicitudes_institucion():
    """Listado paginado de solicitudes de la institución del admin, con filtros."""
    try:
        inst_id = getattr(current_user, 'id_institucion', None)
        if not inst_id:
            flash('No se encontró la institución asociada a tu usuario.', 'warning')
            return redirect(url_for('home.index'))

        # Parámetros de filtro
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, int(request.args.get('per_page', 15)))
        status_raw = (request.args.get('status') or '').strip()
        q_text = (request.args.get('q') or '').strip()
        desde_raw = (request.args.get('desde') or '').strip()
        hasta_raw = (request.args.get('hasta') or '').strip()

        query = Solicitud.query.filter(Solicitud.id_institucion == inst_id)

        # Filtro por estatus
        if status_raw:
            try:
                status_val = int(status_raw)
                query = query.filter(Solicitud.id_estatus == status_val)
            except ValueError:
                pass

        # Filtro por fechas
        if desde_raw:
            try:
                desde_dt = datetime.strptime(desde_raw, '%Y-%m-%d')
                query = query.filter(Solicitud.fecha_creacion >= desde_dt)
            except ValueError:
                pass
        if hasta_raw:
            try:
                hasta_dt = datetime.strptime(hasta_raw, '%Y-%m-%d')
                # incluir fin del día
                hasta_dt = hasta_dt.replace(hour=23, minute=59, second=59)
                query = query.filter(Solicitud.fecha_creacion <= hasta_dt)
            except ValueError:
                pass

        # Búsqueda por texto: razón o nombre de laboratorio
        if q_text:
            query = (query.join(Laboratorio, Laboratorio.id_laboratorio == Solicitud.id_laboratorio, isouter=True)
                          .filter(or_(Solicitud.razon.ilike(f'%{q_text}%'),
                                      Laboratorio.nombre_laboratorio.ilike(f'%{q_text}%'))))

        query = query.order_by(Solicitud.fecha_creacion.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # Opciones de estatus para filtros
        status_options = [
            {'id': 1, 'label': 'Pendiente'},
            {'id': 2, 'label': 'En Revisión'},
            {'id': 3, 'label': 'Aprobada'},
            {'id': 4, 'label': 'Rechazada'},
            {'id': 5, 'label': 'Cancelada'},
            {'id': 6, 'label': 'Completada'},
        ]

        return render_template(
            'admin_solicitudes_institucion.html',
            solicitudes=pagination.items,
            pagination=pagination,
            status_options=status_options,
            current_filters={
                'status': status_raw,
                'q': q_text,
                'desde': desde_raw,
                'hasta': hasta_raw,
                'per_page': per_page
            }
        )
    except Exception as e:
        flash(f'Error al cargar solicitudes de la institución: {str(e)}', 'error')
        return redirect(url_for('home.index'))


def _build_solicitudes_inst_query(current_user, request):
    inst_id = getattr(current_user, 'id_institucion', None)
    if not inst_id:
        return None, {}
    status_raw = (request.args.get('status') or '').strip()
    q_text = (request.args.get('q') or '').strip()
    desde_raw = (request.args.get('desde') or '').strip()
    hasta_raw = (request.args.get('hasta') or '').strip()

    query = Solicitud.query.filter(Solicitud.id_institucion == inst_id)
    if status_raw:
        try:
            status_val = int(status_raw)
            query = query.filter(Solicitud.id_estatus == status_val)
        except ValueError:
            pass
    if desde_raw:
        try:
            desde_dt = datetime.strptime(desde_raw, '%Y-%m-%d')
            query = query.filter(Solicitud.fecha_creacion >= desde_dt)
        except ValueError:
            pass
    if hasta_raw:
        try:
            hasta_dt = datetime.strptime(hasta_raw, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
            query = query.filter(Solicitud.fecha_creacion <= hasta_dt)
        except ValueError:
            pass
    if q_text:
        query = (query.join(Laboratorio, Laboratorio.id_laboratorio == Solicitud.id_laboratorio, isouter=True)
                      .filter(or_(Solicitud.razon.ilike(f'%{q_text}%'),
                                  Laboratorio.nombre_laboratorio.ilike(f'%{q_text}%'))))
    query = query.order_by(Solicitud.fecha_creacion.desc())
    return query, {
        'status': status_raw,
        'q': q_text,
        'desde': desde_raw,
        'hasta': hasta_raw,
    }


@solicitud_bp.route('/institucion/export/csv')
@login_required
@permission_required('ver_todas_solicitudes')
def export_institucion_csv():
    # Solo Administradores
    if not has_admin_access():
        flash('Solo administradores pueden exportar.', 'error')
        return redirect(url_for('home.index'))
    query, _filters = _build_solicitudes_inst_query(current_user, request)
    if query is None:
        flash('No se encontró la institución asociada a tu usuario.', 'warning')
        return redirect(url_for('home.index'))
    rows = query.limit(5000).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Fecha', 'Laboratorio', 'Área', 'Razón', 'Estado', 'Institución', 'Tipo Solicitud', 'Prioridad', 'Investigador', 'ID Investigador', 'Email Contacto', 'Teléfono Contacto'])
    for s in rows:
        inv = getattr(s, 'investigador_principal', None)
        writer.writerow([
            s.id_solicitud,
            s.fecha_creacion.strftime('%Y-%m-%d') if s.fecha_creacion else '',
            s.laboratorio.nombre_laboratorio if s.laboratorio else '',
            (s.laboratorio.area.nombre_area if s.laboratorio and getattr(s.laboratorio, 'area', None) else ''),
            (s.razon or '').replace('\n', ' ').replace('\r', ' '),
            s.estado_nombre,
            s.institucion.nombre_institucion if s.institucion else '',
            s.tipo_solicitud.nombre_tipo_solicitud if s.tipo_solicitud else '',
            s.prioridad or '',
            s.nombre_completo_solicitante,
            getattr(inv, 'id_usuario', ''),
            s.email_contacto or '',
            s.telefono_contacto or '',
        ])
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'text/csv; charset=utf-8'
    resp.headers['Content-Disposition'] = 'attachment; filename=solicitudes_institucion.csv'
    return resp


@solicitud_bp.route('/institucion/export/xlsx')
@login_required
@permission_required('ver_todas_solicitudes')
def export_institucion_xlsx():
    # Solo Administradores
    if not has_admin_access():
        flash('Solo administradores pueden exportar.', 'error')
        return redirect(url_for('home.index'))
    query, _filters = _build_solicitudes_inst_query(current_user, request)
    if query is None:
        flash('No se encontró la institución asociada a tu usuario.', 'warning')
        return redirect(url_for('home.index'))
    rows = query.limit(10000).all()
    wb = Workbook()
    ws = wb.active
    ws.title = 'Solicitudes'
    headers = ['ID', 'Fecha', 'Laboratorio', 'Área', 'Razón', 'Estado', 'Institución', 'Tipo Solicitud', 'Prioridad', 'Investigador', 'ID Investigador', 'Email Contacto', 'Teléfono Contacto']
    ws.append(headers)
    for s in rows:
        inv = getattr(s, 'investigador_principal', None)
        ws.append([
            s.id_solicitud,
            s.fecha_creacion.strftime('%Y-%m-%d') if s.fecha_creacion else '',
            s.laboratorio.nombre_laboratorio if s.laboratorio else '',
            (s.laboratorio.area.nombre_area if s.laboratorio and getattr(s.laboratorio, 'area', None) else ''),
            s.razon or '',
            s.estado_nombre,
            s.institucion.nombre_institucion if s.institucion else '',
            s.tipo_solicitud.nombre_tipo_solicitud if s.tipo_solicitud else '',
            s.prioridad or '',
            s.nombre_completo_solicitante,
            getattr(inv, 'id_usuario', ''),
            s.email_contacto or '',
            s.telefono_contacto or '',
        ])
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    resp = make_response(output.getvalue())
    resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    resp.headers['Content-Disposition'] = 'attachment; filename=solicitudes_institucion.xlsx'
    return resp