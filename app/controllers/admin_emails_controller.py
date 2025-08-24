from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.models.monthly_report import SystemKV
from app.utils.permissions import is_super_user
from app.utils.email_service import send_email


admin_emails_bp = Blueprint('admin_emails', __name__)


TEMPLATE_DEFS = [
    {
        'key': 'email.activation',
        'name': 'Activación de cuenta',
        'placeholders': ['display_name', 'activation_url'],
        'default_subject': 'Activa tu cuenta - SIGRAL',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h2>¡Bienvenido(a) {{ display_name }}!</h2>'
            '<p>Para empezar a usar tu cuenta, por favor actívala haciendo clic en el siguiente botón:</p>'
            '<p><a href="{{ activation_url }}" style="background:#16a34a;color:white;padding:10px 16px;text-decoration:none;border-radius:6px;">Activar cuenta</a></p>'
            '<p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>'
            '<p style="word-break: break-all;">{{ activation_url }}</p>'
            '<p style="color:#666; font-size:12px;">Este enlace expira en 60 minutos.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.password_reset',
        'name': 'Restablecer contraseña',
        'placeholders': ['display_name', 'reset_url'],
        'default_subject': 'Restablece tu contraseña - SIGRAL',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h2>Hola {{ display_name }}</h2>'
            '<p>Recibimos una solicitud para restablecer tu contraseña.</p>'
            '<p>Haz clic en el siguiente botón para crear una nueva contraseña:</p>'
            '<p><a href="{{ reset_url }}" style="background:#2563eb;color:white;padding:10px 16px;text-decoration:none;border-radius:6px;">Restablecer contraseña</a></p>'
            '<p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>'
            '<p style="word-break: break-all;">{{ reset_url }}</p>'
            '<p style="color:#666; font-size:12px;">Este enlace expira en 60 minutos. Si no fuiste tú, ignora este correo.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.welcome',
        'name': 'Bienvenida',
        'placeholders': ['display_name'],
        'default_subject': 'Bienvenido(a) a SIGRAL',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h2>¡Hola {{ display_name }}!</h2>'
            '<p>Tu cuenta ha sido creada exitosamente.</p>'
            '<p>Puedes iniciar sesión cuando quieras desde el portal.</p>'
            '<p style="color:#666; font-size:12px;">Si tú no solicitaste esta cuenta, por favor ignora este correo.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.role_request',
        'name': 'Solicitud de rol (a Super Admins)',
        'placeholders': ['user_name','username','user_email','requested_roles','approval_links_html','extra_instituciones','fecha'],
        'default_subject': 'SIGRAL - Nueva solicitud de rol',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h3>Nueva solicitud de rol</h3>'
            '<p><strong>Usuario:</strong> {{ user_name }} | <strong>Usuario:</strong> {{ username }} | <strong>Email:</strong> {{ user_email }}</p>'
            '<p><strong>Solicitudes:</strong> {{ requested_roles }}</p>'
            '{{ extra_instituciones }}'
            '<div>{{ approval_links_html }}</div>'
            '<p style="color:#6b7280; font-size:12px;">Fecha: {{ fecha }}</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.role_request_result',
        'name': 'Resultado de solicitud de rol (al usuario)',
        'placeholders': ['display_name','role_name','status','lab_name','session_notice'],
        'default_subject': 'SIGRAL - Resultado de tu solicitud de rol',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h3>Resultado de tu solicitud de rol</h3>'
            '<p>Hola {{ display_name }},</p>'
            '<p>Tu solicitud para el rol <strong>{{ role_name }}</strong> ha sido <strong>{{ status }}</strong>.</p>'
            '{{ lab_name }}'
            '{{ session_notice }}'
            '<p style="color:#6b7280;font-size:12px">Este es un mensaje automático.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.inactivity_warning',
        'name': 'Aviso de inactividad',
        'placeholders': ['display_name','warn_days'],
        'default_subject': 'SIGRAL - Aviso de inactividad',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<p>Hola {{ display_name }},</p>'
            '<p>No hemos detectado actividad en tu cuenta recientemente. Si no inicias sesión en los próximos {{ warn_days }} días naturales, tu cuenta será eliminada por inactividad.</p>'
            '<p>Para conservar tu cuenta, inicia sesión en el sistema.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.inactivity_deleted',
        'name': 'Cuenta eliminada por inactividad',
        'placeholders': ['display_name','delete_days'],
        'default_subject': 'SIGRAL - Cuenta eliminada por inactividad',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<p>Hola {{ display_name }},</p>'
            '<p>Tu cuenta ha sido eliminada por inactividad superior a {{ delete_days }} días.</p>'
            '</div>'
        ),
    },
    {
        'key': 'email.institution_role_request',
        'name': 'Nueva solicitud en tu institución (Admin Institucional)',
        'placeholders': ['inst_admin_name','user_name','username','user_email','requested_roles','fecha'],
        'default_subject': 'SIGRAL - Nueva solicitud en tu institución',
        'default_html': (
            '<div style="font-family: Arial, sans-serif; line-height:1.6;">'
            '<h3>Nueva solicitud de usuario en tu institución</h3>'
            '<p>Hola {{ inst_admin_name }},</p>'
            '<p><strong>Usuario:</strong> {{ user_name }} ({{ username }}) - {{ user_email }}</p>'
            '<p><strong>Solicitudes:</strong> {{ requested_roles }}</p>'
            '<p style="color:#6b7280; font-size:12px;">Fecha: {{ fecha }}</p>'
            '</div>'
        ),
    },
]


def _get_kv(key: str, default_value: str) -> str:
    kv = SystemKV.query.get(key)
    return kv.value if kv and kv.value is not None else default_value


def _set_kv(key: str, value: str) -> None:
    kv = SystemKV.query.get(key)
    if not kv:
        kv = SystemKV(key=key, value=value)
        db.session.add(kv)
    else:
        kv.value = value


@admin_emails_bp.route('/admin/emails', methods=['GET'])
@login_required
def editar_emails():
    if not is_super_user():
        flash('Acceso restringido a Super Administradores.', 'error')
        return redirect(url_for('home.index'))
    items = []
    for t in TEMPLATE_DEFS:
        subj_key = f"{t['key']}.subject"
        html_key = f"{t['key']}.html"
        items.append({
            'key': t['key'],
            'name': t['name'],
            'placeholders': t['placeholders'],
            'subject': _get_kv(subj_key, t['default_subject']),
            'html': _get_kv(html_key, t['default_html']),
        })
    return render_template('admin_emails.html', items=items)


@admin_emails_bp.route('/admin/emails', methods=['POST'])
@login_required
def guardar_emails():
    if not is_super_user():
        flash('Acceso restringido a Super Administradores.', 'error')
        return redirect(url_for('home.index'))
    try:
        for t in TEMPLATE_DEFS:
            subj_field = f"{t['key']}__subject"
            html_field = f"{t['key']}__html"
            if subj_field in request.form:
                _set_kv(f"{t['key']}.subject", request.form.get(subj_field, t['default_subject']))
            if html_field in request.form:
                _set_kv(f"{t['key']}.html", request.form.get(html_field, t['default_html']))
        db.session.commit()
        flash('Plantillas de correo actualizadas.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al guardar: {e}', 'error')
    return redirect(url_for('admin_emails.editar_emails'))


def _find_template_def(key: str):
    for t in TEMPLATE_DEFS:
        if t['key'] == key:
            return t
    return None


@admin_emails_bp.route('/admin/emails/test-send', methods=['POST'])
@login_required
def test_send_email():
    if not is_super_user():
        flash('Acceso restringido a Super Administradores.', 'error')
        return redirect(url_for('home.index'))
    try:
        tmpl_key = request.form.get('tmpl_key', '').strip()
        to_email = request.form.get('test_to_email', '').strip()
        if not tmpl_key or not to_email:
            flash('Faltan datos para envío de prueba (plantilla o correo).', 'error')
            return redirect(url_for('admin_emails.editar_emails'))

        tdef = _find_template_def(tmpl_key)
        if not tdef:
            flash('Plantilla no reconocida.', 'error')
            return redirect(url_for('admin_emails.editar_emails'))

        # Cargar asunto/HTML actuales o sobrescritos
        subject = request.form.get('subject_override') or _get_kv(f"{tmpl_key}.subject", tdef['default_subject'])
        html = request.form.get('html_override') or _get_kv(f"{tmpl_key}.html", tdef['default_html'])

        # Reemplazar placeholders simples {{ name }} (incluye globales)
        missing = []
        global_phs = ['system_name','system_short','base_url']
        for ph in tdef.get('placeholders', []):
            val = (request.form.get(f'ph__{ph}', '') or '').strip()
            if not val:
                missing.append(ph)
            token = '{{ ' + ph + ' }}'
            subject = subject.replace(token, val)
            html = html.replace(token, val)
        # Globales opcionales
        from app.utils.email_service import _global_placeholders
        gvals = _global_placeholders()
        for gk, gv in gvals.items():
            token = '{{ ' + gk + ' }}'
            subject = subject.replace(token, str(gv))
            html = html.replace(token, str(gv))
        # Normalizar etiquetas HTML escapadas accidentales
        try:
            import html as _pyhtml
            html = _pyhtml.unescape(html)
        except Exception:
            pass

        if missing:
            flash('Faltan valores para: ' + ', '.join(missing), 'error')
            return redirect(url_for('admin_emails.editar_emails'))

        ok = send_email(subject, to_email, html)
        if ok:
            flash('Correo de prueba enviado.', 'success')
        else:
            flash('No se pudo enviar el correo de prueba. Revisa configuración SMTP.', 'error')
    except Exception as e:
        flash(f'Error al enviar prueba: {e}', 'error')
    return redirect(url_for('admin_emails.editar_emails'))


