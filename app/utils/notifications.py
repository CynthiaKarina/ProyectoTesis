from flask import current_app
from app import db
from app.utils.email_service import send_email


def get_super_admin_emails():
    try:
        from app.models.user import User
        from app.models.roles import Roles
        # Buscar usuarios cuyo rol sea 'Super Administrador' (o alias similares)
        aliases = ['Super Administrador', 'Super Admin', 'super_admin', 'superadministrador']
        super_roles = db.session.query(Roles.id_rol).filter(Roles.nombre_rol.in_(aliases)).all()
        role_ids = [r.id_rol for r in super_roles]
        if not role_ids:
            return []
        users = User.query.filter(User.id_rol.in_(role_ids)).all()
        return [u.email for u in users if getattr(u, 'email', None)]
    except Exception as e:
        try:
            current_app.logger.warning(f"No se pudieron obtener emails de Super Admin: {e}")
        except Exception:
            pass
        return []


def notify_super_admins(subject: str, message: str):
    """Envía una notificación básica a Super Admins.
    Si no hay sistema de email, se registra en el logger.
    """
    emails = []
    try:
        emails = get_super_admin_emails()
    except Exception:
        emails = []

    # Envío por email si hay destinatarios configurados
    if emails:
        html = f"""
        <div style='font-family:Arial,sans-serif;line-height:1.6'>
          <h3 style='margin:0 0 8px 0'>Notificación SIGRAL</h3>
          <p style='margin:0 0 12px 0'>{message}</p>
          <p style='color:#6b7280;font-size:12px'>Este es un mensaje automático. No respondas este correo.</p>
        </div>
        """
        for to in emails:
            try:
                send_email(subject=subject, to_email=to, html_body=html)
            except Exception as e:
                try:
                    current_app.logger.warning(f"Fallo enviando email a {to}: {e}")
                except Exception:
                    pass

    # Registrar en logger (fallback común)
    try:
        current_app.logger.info(f"[NOTIF SUPER ADMIN] {subject} | Destinatarios: {emails} | {message}")
    except Exception:
        print(f"[NOTIF SUPER ADMIN] {subject} -> {emails}: {message}")


def get_lab_admin_emails(lab_id: int):
    """Obtiene correos de administradores del laboratorio.
    Actualmente se usa el campo laboratorio.id_encargado como administrador.
    """
    try:
        from app.models.laboratorio import Laboratorio
        from app.models.user import User
        from app.models.laboratorio_admin import LaboratorioAdmin
        lab = Laboratorio.query.get(lab_id)
        emails = []
        # 1) admins múltiples vía tabla puente
        admins = LaboratorioAdmin.query.filter_by(id_laboratorio=lab_id).all()
        for adm in admins:
            u = User.query.get(adm.id_usuario)
            if u and getattr(u, 'email', None):
                emails.append(u.email)
        # 2) fallback: id_encargado
        if not emails and lab and lab.id_encargado:
            user = User.query.get(lab.id_encargado)
            if user and getattr(user, 'email', None):
                emails.append(user.email)
        return emails
    except Exception as e:
        try:
            current_app.logger.warning(f"No se pudieron obtener emails de admin de laboratorio {lab_id}: {e}")
        except Exception:
            pass
        return []


def notify_lab_admins_or_superadmins(lab_id: int, subject: str, message: str):
    """Notifica a admins del lab; si no hay, a Super Admins."""
    recipients = get_lab_admin_emails(lab_id)
    if not recipients:
        notify_super_admins(subject, f"[Sin admin de laboratorio {lab_id}] {message}")
        return
    try:
        current_app.logger.info(f"[NOTIF LAB ADMIN] {subject} | Lab {lab_id} | Destinatarios: {recipients} | {message}")
    except Exception:
        print(f"[NOTIF LAB ADMIN] {subject} -> {recipients}: {message}")


