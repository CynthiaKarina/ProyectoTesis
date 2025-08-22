from email.message import EmailMessage
import smtplib
import time
from typing import Optional
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired


def _get_serializer() -> URLSafeTimedSerializer:
    secret_key = current_app.config.get('SECRET_KEY')
    return URLSafeTimedSerializer(secret_key)


def generate_token(email: str) -> str:
    serializer = _get_serializer()
    salt = current_app.config.get('SECURITY_EMAIL_SALT', 'sigral-email-salt')
    return serializer.dumps(email, salt=salt)


def confirm_token(token: str, expiration_seconds: int = 3600) -> Optional[str]:
    serializer = _get_serializer()
    salt = current_app.config.get('SECURITY_EMAIL_SALT', 'sigral-email-salt')
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration_seconds)
        return email
    except (SignatureExpired, BadSignature):
        return None


def generate_approval_token(payload: dict) -> str:
    serializer = _get_serializer()
    salt = current_app.config.get('SECURITY_APPROVAL_SALT', 'sigral-approval-salt')
    return serializer.dumps(payload, salt=salt)


def confirm_approval_token(token: str, expiration_seconds: int = 172800) -> Optional[dict]:
    serializer = _get_serializer()
    salt = current_app.config.get('SECURITY_APPROVAL_SALT', 'sigral-approval-salt')
    try:
        data = serializer.loads(token, salt=salt, max_age=expiration_seconds)
        if isinstance(data, dict):
            return data
        return None
    except (SignatureExpired, BadSignature):
        return None


def send_email(subject: str, to_email: str, html_body: str, text_body: Optional[str] = None, max_attempts: int = 3, initial_backoff_seconds: float = 1.0) -> bool:
    mail_server = current_app.config.get('MAIL_SERVER')
    mail_port = current_app.config.get('MAIL_PORT', 587)
    mail_use_tls = current_app.config.get('MAIL_USE_TLS', True)
    mail_username = current_app.config.get('MAIL_USERNAME')
    mail_password = current_app.config.get('MAIL_PASSWORD')
    mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER', mail_username)

    if not (mail_server and mail_port and mail_username and mail_password and mail_sender):
        try:
            current_app.logger.error('Email no configurado correctamente. Faltan variables MAIL_*')
        except Exception:
            pass
        return False

    message = EmailMessage()
    message['Subject'] = subject
    message['From'] = mail_sender
    message['To'] = to_email
    message.set_content(text_body or 'Este mensaje requiere un cliente compatible con HTML.')
    message.add_alternative(html_body, subtype='html')

    backoff = max(0.5, float(initial_backoff_seconds or 1.0))
    attempts = max(1, int(max_attempts or 1))

    for attempt in range(1, attempts + 1):
        try:
            with smtplib.SMTP(mail_server, mail_port, timeout=15) as server:
                if mail_use_tls:
                    server.starttls()
                server.login(mail_username, mail_password)
                server.send_message(message)
            return True
        except Exception as e:
            try:
                current_app.logger.warning(f'Intento {attempt}/{attempts} fallido enviando email a {to_email}: {e}')
            except Exception:
                pass
            if attempt < attempts:
                try:
                    time.sleep(backoff)
                except Exception:
                    pass
                backoff *= 2
            else:
                try:
                    current_app.logger.error(f'Error definitivo enviando email a {to_email}: {e}')
                except Exception:
                    pass
                return False


def send_welcome_email(to_email: str, nombre: Optional[str] = None) -> bool:
    display_name = nombre or ''
    subject = 'Bienvenido(a) a SIGRAL'
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height:1.6;">
      <h2>¡Hola {display_name}!</h2>
      <p>Tu cuenta ha sido creada exitosamente.</p>
      <p>Puedes iniciar sesión cuando quieras desde el portal.</p>
      <p style="color:#666; font-size:12px;">Si tú no solicitaste esta cuenta, por favor ignora este correo.</p>
    </div>
    """
    text_body = f"Hola {display_name}, tu cuenta ha sido creada exitosamente."
    return send_email(subject, to_email, html_body, text_body)


def send_password_reset_email(to_email: str, nombre: Optional[str], reset_url: str) -> bool:
    display_name = nombre or ''
    subject = 'Restablece tu contraseña - SIGRAL'
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height:1.6;">
      <h2>Hola {display_name}</h2>
      <p>Recibimos una solicitud para restablecer tu contraseña.</p>
      <p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>
      <p><a href="{reset_url}" style="background:#2563eb;color:white;padding:10px 16px;text-decoration:none;border-radius:6px;">Restablecer contraseña</a></p>
      <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
      <p style="word-break: break-all;">{reset_url}</p>
      <p style="color:#666; font-size:12px;">Este enlace expira en 60 minutos. Si no fuiste tú, ignora este correo.</p>
    </div>
    """
    text_body = f"Hola {display_name}, para restablecer tu contraseña visita: {reset_url} (expira en 60 minutos)."
    return send_email(subject, to_email, html_body, text_body)


def send_activation_email(to_email: str, nombre: Optional[str], activation_url: str) -> bool:
    display_name = nombre or ''
    subject = 'Activa tu cuenta - SIGRAL'
    html_body = f"""
    <div style=\"font-family: Arial, sans-serif; line-height:1.6;\">
      <h2>¡Bienvenido(a) {display_name}!</h2>
      <p>Para empezar a usar tu cuenta, por favor actívala haciendo clic en el siguiente botón:</p>
      <p><a href=\"{activation_url}\" style=\"background:#16a34a;color:white;padding:10px 16px;text-decoration:none;border-radius:6px;\">Activar cuenta</a></p>
      <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
      <p style=\"word-break: break-all;\">{activation_url}</p>
      <p style=\"color:#666; font-size:12px;\">Este enlace expira en 60 minutos.</p>
    </div>
    """
    text_body = f"Hola {display_name}, activa tu cuenta aquí (expira en 60 minutos): {activation_url}"
    return send_email(subject, to_email, html_body, text_body)


