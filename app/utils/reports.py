from datetime import datetime, date
import os
from app import db
import secrets


def _period_from_date(d: date):
    return d.year, d.month


def _ensure_reports_folder():
    base = os.path.join(os.getcwd(), 'reports')
    if not os.path.exists(base):
        try:
            os.makedirs(base, exist_ok=True)
        except Exception:
            pass
    return base


def generate_user_month_report(user_id: int, period: date | None = None):
    """Genera XLSX con solicitudes del usuario para el mes; registra en MonthlyReport."""
    from openpyxl import Workbook
    from app.models.solicitud import Solicitud
    from app.models.monthly_report import MonthlyReport

    today = period or date.today()
    year, month = _period_from_date(today)

    # Consultar solicitudes del mes
    qs = (db.session.query(Solicitud)
          .filter(Solicitud.id_investigador==user_id,
                  Solicitud.fecha_creacion>=date(year, month, 1),
                  Solicitud.fecha_creacion<date(year + (1 if month==12 else 0), (month % 12) + 1, 1))
          .order_by(Solicitud.fecha_creacion.asc()))
    rows = qs.all()

    # Generar archivo
    wb = Workbook()
    ws = wb.active
    ws.title = 'Solicitudes'
    headers = ['ID', 'Fecha', 'Laboratorio', 'Razón', 'Estado']
    ws.append(headers)
    for s in rows:
        ws.append([
            s.id_solicitud,
            s.fecha_creacion.strftime('%Y-%m-%d') if s.fecha_creacion else '',
            s.laboratorio.nombre_laboratorio if s.laboratorio else '',
            s.razon or '',
            s.estado_nombre
        ])

    base = _ensure_reports_folder()
    # Nombre opaco no predecible
    token = secrets.token_hex(16)
    fname = f'rpt_{token}.xlsx'
    path = os.path.join(base, fname)
    try:
        wb.save(path)
    except Exception:
        return None

    # Registrar en BD
    try:
        rec = MonthlyReport(period_year=year, period_month=month, scope='user', user_id=user_id, file_path=path)
        db.session.add(rec)
        db.session.commit()
    except Exception:
        db.session.rollback()
    return path


def rotate_monthly_data_if_needed(today: date | None = None):
    """Si cambió de mes, archiva global y borra solicitudes de usuarios; conserva reportes del año.
    Debe llamarse en arranque o por cron diario.
    """
    from app.models.monthly_report import SystemKV, MonthlyReport
    from app.models.solicitud import Solicitud
    from openpyxl import Workbook

    now = today or date.today()
    year, month = _period_from_date(now)

    # Leer último período
    kv = SystemKV.query.get('last_rotate_period')
    last = kv.value if kv else None
    current_key = f'{year:04d}-{month:02d}'
    if last == current_key:
        return False  # ya rotado

    # Generar reporte global del mes anterior
    prev_year = year if month > 1 else year - 1
    prev_month = (month - 1) if month > 1 else 12

    start = date(prev_year, prev_month, 1)
    end = date(year, month, 1)
    qs = (db.session.query(Solicitud)
          .filter(Solicitud.fecha_creacion>=start, Solicitud.fecha_creacion<end))
    rows = qs.all()

    wb = Workbook()
    ws = wb.active
    ws.title = f'{prev_year}-{prev_month:02d}'
    ws.append(['ID', 'Usuario', 'Fecha', 'Laboratorio', 'Razón', 'Estado'])
    for s in rows:
        try:
            usuario = s.investigador_principal
            nombre = f"{usuario.nombre} {usuario.apellido_paterno}" if usuario else ''
        except Exception:
            nombre = ''
        ws.append([
            s.id_solicitud,
            nombre,
            s.fecha_creacion.strftime('%Y-%m-%d') if s.fecha_creacion else '',
            s.laboratorio.nombre_laboratorio if s.laboratorio else '',
            s.razon or '',
            s.estado_nombre
        ])

    base = _ensure_reports_folder()
    # Nombre opaco no predecible
    token = secrets.token_hex(16)
    gname = f'rpt_{token}.xlsx'
    gpath = os.path.join(base, gname)
    try:
        wb.save(gpath)
        rec = MonthlyReport(period_year=prev_year, period_month=prev_month, scope='global', file_path=gpath)
        db.session.add(rec)
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Borrar solicitudes de usuarios del período anterior
    try:
        qs.delete(synchronize_session=False)
        db.session.commit()
    except Exception:
        db.session.rollback()

    # Actualizar período rotado
    try:
        if not kv:
            kv = SystemKV(key='last_rotate_period', value=current_key)
            db.session.add(kv)
        else:
            kv.value = current_key
        db.session.commit()
    except Exception:
        db.session.rollback()
    return True


