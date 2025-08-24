from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from flask_login import login_required
from app.utils.permissions import permission_required, is_super_user
from app import db
from datetime import datetime
import os


admin_reports_bp = Blueprint('admin_reports', __name__)


@admin_reports_bp.route('/admin/reportes-mensuales')
@login_required
@permission_required('ver_reportes')
def listar_reportes_mensuales():
    # Solo Super Admin
    if not is_super_user():
        flash('Acceso restringido: solo Super Administrador.', 'error')
        return redirect(url_for('home.index'))
    try:
        from app.models.monthly_report import MonthlyReport
        from app.models.user import User

        year = request.args.get('year', type=int) or datetime.utcnow().year
        scope = (request.args.get('scope') or '').strip()  # '' | global | user
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, int(request.args.get('per_page', 15)))

        q = db.session.query(MonthlyReport)
        q = q.filter(MonthlyReport.period_year == year)
        if scope in ['global', 'user']:
            q = q.filter(MonthlyReport.scope == scope)
        q = q.order_by(MonthlyReport.period_year.desc(), MonthlyReport.period_month.desc(), MonthlyReport.id.desc())

        # Paginación manual
        total = q.count()
        items = q.offset((page - 1) * per_page).limit(per_page).all()

        # Enriquecer con nombre de usuario para scope=user
        user_names = {}
        try:
            user_ids = [r.user_id for r in items if r.scope == 'user' and r.user_id]
            if user_ids:
                users = db.session.query(User).filter(User.id_usuario.in_(user_ids)).all()
                user_names = {u.id_usuario: f"{u.nombre} {u.apellido_paterno}".strip() for u in users}
        except Exception:
            user_names = {}

        return render_template(
            'admin_reports.html',
            reports=items,
            user_names=user_names,
            year=year,
            scope=scope,
            page=page,
            per_page=per_page,
            total=total,
            total_pages=(total + per_page - 1)//per_page,
            is_super=is_super_user()
        )
    except Exception as e:
        flash(f'Error cargando reportes: {e}', 'error')
        return redirect(url_for('home.index'))


@admin_reports_bp.route('/admin/reportes-mensuales/descargar/<int:report_id>')
@login_required
@permission_required('ver_reportes')
def descargar_reporte_mensual(report_id: int):
    # Solo Super Admin
    if not is_super_user():
        flash('Acceso restringido: solo Super Administrador.', 'error')
        return redirect(url_for('home.index'))
    try:
        from app.models.monthly_report import MonthlyReport
        rec = db.session.query(MonthlyReport).get(report_id)
        if not rec or not rec.file_path or not os.path.exists(rec.file_path):
            flash('Archivo no disponible', 'error')
            return redirect(url_for('admin_reports.listar_reportes_mensuales'))
        with open(rec.file_path, 'rb') as f:
            data = f.read()
        fname = os.path.basename(rec.file_path)
        resp = make_response(data)
        resp.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        resp.headers['Content-Disposition'] = f'attachment; filename={fname}'
        return resp
    except Exception as e:
        flash(f'Error descargando reporte: {e}', 'error')
        return redirect(url_for('admin_reports.listar_reportes_mensuales'))


@admin_reports_bp.route('/admin/reportes-mensuales/limpiar-anual', methods=['POST'])
@login_required
@permission_required('ver_reportes')
def limpiar_anual():
    # Solo Super Admin puede ejecutar limpieza
    if not is_super_user():
        flash('Solo Super Admin puede limpiar reportes anuales.', 'error')
        return redirect(url_for('admin_reports.listar_reportes_mensuales'))
    try:
        from app.models.monthly_report import MonthlyReport
        year = request.form.get('year', type=int) or datetime.utcnow().year
        rows = db.session.query(MonthlyReport).filter(MonthlyReport.period_year == year).all()
        removed = 0
        for r in rows:
            try:
                if r.file_path and os.path.exists(r.file_path):
                    os.remove(r.file_path)
            except Exception:
                pass
            try:
                db.session.delete(r)
                removed += 1
            except Exception:
                pass
        db.session.commit()
        flash(f'Reportes del año {year} eliminados ({removed}).', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error en limpieza anual: {e}', 'error')
    return redirect(url_for('admin_reports.listar_reportes_mensuales'))


