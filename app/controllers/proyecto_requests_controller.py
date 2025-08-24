from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from datetime import datetime
from app.utils.permissions import permission_required, is_super_user, has_admin_access


proj_req_bp = Blueprint('proj_requests', __name__)


def _user_can_review_request(req):
    # Super Admin puede
    if is_super_user():
        return True
    # Admin Institucional puede
    if has_admin_access():
        return True
    # Investigador responsable del proyecto puede
    try:
        proyecto = req.proyecto
        if proyecto and proyecto.owner_id == getattr(current_user, 'id_usuario', None):
            return True
    except Exception:
        pass
    return False


@proj_req_bp.route('/admin/proyectos/solicitudes')
@login_required
@permission_required('ver_reportes')
def listar_solicitudes_proyecto():
    try:
        from app.models.proyecto_request import ProyectoRequest
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, int(request.args.get('per_page', 15)))
        status = (request.args.get('status') or '').strip()
        tipo = (request.args.get('tipo') or '').strip()

        q = db.session.query(ProyectoRequest).order_by(ProyectoRequest.created_at.desc())
        if status in ['pendiente', 'aprobado', 'rechazado']:
            q = q.filter(ProyectoRequest.estatus == status)
        if tipo in ['publicacion', 'actualizacion']:
            q = q.filter(ProyectoRequest.tipo == tipo)

        total = q.count()
        items = q.offset((page-1)*per_page).limit(per_page).all()
        # Filtrar por permisos efectivos
        items = [r for r in items if _user_can_review_request(r)]

        return render_template('admin_solicitudes_proyecto.html',
                               requests=items,
                               page=page,
                               per_page=per_page,
                               total=total,
                               total_pages=(total+per_page-1)//per_page,
                               status=status,
                               tipo=tipo)
    except Exception as e:
        flash(f'Error cargando solicitudes: {e}', 'error')
        return redirect(url_for('home.index'))


@proj_req_bp.route('/admin/proyectos/solicitudes/<int:req_id>/<action>', methods=['POST'])
@login_required
@permission_required('ver_reportes')
def resolver_solicitud_proyecto(req_id: int, action: str):
    if action not in ['aprobar', 'rechazar']:
        flash('Acción inválida.', 'error')
        return redirect(url_for('proj_requests.listar_solicitudes_proyecto'))
    try:
        from app.models.proyecto_request import ProyectoRequest
        from app.models.proyecto import Proyecto
        from app.utils.email_service import send_email

        req = db.session.query(ProyectoRequest).get(req_id)
        if not req:
            flash('Solicitud no encontrada.', 'error')
            return redirect(url_for('proj_requests.listar_solicitudes_proyecto'))
        if not _user_can_review_request(req):
            flash('No tienes permisos para resolver esta solicitud.', 'error')
            return redirect(url_for('proj_requests.listar_solicitudes_proyecto'))

        req.estatus = 'aprobado' if action == 'aprobar' else 'rechazado'
        req.reviewer_id = getattr(current_user, 'id_usuario', None)
        req.reviewed_at = datetime.utcnow()

        proyecto = db.session.query(Proyecto).get(req.id_proyecto)
        if proyecto and action == 'aprobar':
            proyecto.publico = True
            proyecto.requiere_aprobacion = False
            proyecto.aprobado_por = req.reviewer_id
            proyecto.aprobado_en = datetime.utcnow()

        db.session.commit()

        # Notificar solicitante
        try:
            from app.models.user import User
            u = db.session.query(User).get(req.id_solicitante)
            if u and u.email:
                estado_txt = 'aprobada' if req.estatus == 'aprobado' else 'rechazada'
                pname = proyecto.nombre_proyecto if proyecto else f'ID {req.id_proyecto}'
                html = f"""
                <div style='font-family:Arial,sans-serif;line-height:1.6'>
                  <h3>Solicitud de proyecto {estado_txt}</h3>
                  <p>Tu solicitud para publicar/actualizar el proyecto <strong>{pname}</strong> ha sido <strong>{estado_txt}</strong>.</p>
                  <p style='color:#6b7280;font-size:12px'>Este es un mensaje automático.</p>
                </div>
                """
                send_email(subject='SIGRAL - Solicitud de proyecto', to_email=u.email, html_body=html)
        except Exception:
            pass

        flash('Solicitud resuelta.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error resolviendo solicitud: {e}', 'error')
    return redirect(url_for('proj_requests.listar_solicitudes_proyecto'))


