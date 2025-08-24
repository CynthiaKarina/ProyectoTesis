from datetime import datetime, timedelta
from app import db
import os


SPECIAL_ROLES = {
    'Super Administrador', 'Administrador', 'Admin Institucional',
    'Gestor de Laboratorios', 'Encargado Técnico', 'Admin de Laboratorio',
    'Investigador'
}


def _is_protected_role(user) -> bool:
    try:
        role_name = user.roles.nombre_rol if user.roles else None
        return role_name in SPECIAL_ROLES
    except Exception:
        return False


def _thresholds_from_env(default_warn=7, default_delete=30):
    try:
        wd = int(os.environ.get('INACTIVITY_WARN_DAYS', default_warn))
    except Exception:
        wd = default_warn
    try:
        dd = int(os.environ.get('INACTIVITY_DELETE_DAYS', default_delete))
    except Exception:
        dd = default_delete
    # proteger valores mínimos
    wd = max(1, wd)
    dd = max(wd + 1, dd)
    return wd, dd


def process_inactive_accounts(warn_days: int = 7, delete_after_days: int = 30):
    """Envía advertencias y elimina usuarios inactivos sin roles especiales.

    Regla:
    - Advertir por correo a quienes llevan >= (delete_after_days - warn_days) sin login.
    - Eliminar a quienes llevan >= delete_after_days sin login.
    """
    from app.models.user import User
    from app.utils.email_service import send_email
    from app.models.monthly_report import SystemKV

    now = datetime.utcnow()
    warn_since = now - timedelta(days=delete_after_days - warn_days)
    delete_since = now - timedelta(days=delete_after_days)

    warned = 0
    deleted = 0

    # Advertir
    try:
        to_warn = (db.session.query(User)
                   .filter(User.ultimo_acceso <= warn_since)
                   .filter(User.ultimo_acceso > delete_since)
                   .all())
        for u in to_warn:
            if _is_protected_role(u):
                continue
            if not getattr(u, 'email', None):
                continue
            try:
                subj = (SystemKV.query.get('email.inactivity_warning.subject') or SystemKV(key='email.inactivity_warning.subject', value='SIGRAL - Aviso de inactividad')).value
                html_tmpl = (SystemKV.query.get('email.inactivity_warning.html') or SystemKV(key='email.inactivity_warning.html', value='<div style="font-family: Arial, sans-serif; line-height:1.6;"><p>Hola {{ display_name }},</p><p>No hemos detectado actividad en tu cuenta recientemente. Si no inicias sesión en los próximos {{ warn_days }} días naturales, tu cuenta será eliminada por inactividad.</p><p>Para conservar tu cuenta, inicia sesión en el sistema.</p></div>')).value
                display_name = (getattr(u, 'nombre', None) or getattr(u, 'username', '') or '')
                html_body = (html_tmpl
                             .replace('{{ display_name }}', display_name)
                             .replace('{{ warn_days }}', str(warn_days)))
                send_email(subject=subj, to_email=u.email, html_body=html_body)
                warned += 1
            except Exception:
                continue
    except Exception:
        pass

    # Eliminar
    try:
        to_delete = (db.session.query(User)
                     .filter(User.ultimo_acceso <= delete_since)
                     .all())
        for u in to_delete:
            if _is_protected_role(u):
                continue
            try:
                if getattr(u, 'email', None):
                    subj = (SystemKV.query.get('email.inactivity_deleted.subject') or SystemKV(key='email.inactivity_deleted.subject', value='SIGRAL - Cuenta eliminada por inactividad')).value
                    html_tmpl = (SystemKV.query.get('email.inactivity_deleted.html') or SystemKV(key='email.inactivity_deleted.html', value='<div style="font-family: Arial, sans-serif; line-height:1.6;"><p>Hola {{ display_name }},</p><p>Tu cuenta ha sido eliminada por inactividad superior a {{ delete_days }} días.</p></div>')).value
                    display_name = (getattr(u, 'nombre', None) or getattr(u, 'username', '') or '')
                    html_body = (html_tmpl
                                 .replace('{{ display_name }}', display_name)
                                 .replace('{{ delete_days }}', str(delete_after_days)))
                    send_email(subject=subj, to_email=u.email, html_body=html_body)
            except Exception:
                pass
            try:
                db.session.delete(u)
                deleted += 1
            except Exception:
                continue
        db.session.commit()
    except Exception:
        db.session.rollback()

    return {'warned': warned, 'deleted': deleted}


def process_inactive_accounts_from_env():
    wd, dd = _thresholds_from_env()
    return process_inactive_accounts(warn_days=wd, delete_after_days=dd)


