from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.connection import get_db_connection
from app import db
from datetime import datetime
import re
from werkzeug.security import generate_password_hash
from app.models.institucion import Institucion
from app.utils.email_service import generate_token, send_activation_email

# Modificar el nombre del Blueprint
register_bp = Blueprint('register', __name__)

def validar_email(email):
    """Validar formato de email"""
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None

def validar_telefono(telefono):
    """Validar formato de teléfono (10 dígitos)"""
    patron = r'^\d{10}$'
    return re.match(patron, telefono) is not None

def validar_matricula(matricula):
    """Validar formato de matrícula"""
    patron = r'^[A-Z0-9]{8,10}$'
    return re.match(patron, matricula) is not None

def validar_password(password):
    """Validar formato de contraseña según los requisitos específicos"""
    if not password:
        return False, "La contraseña es requerida"
    
    # Longitud: 8-64 caracteres
    if len(password) < 8 or len(password) > 12:
        return False, "La contraseña debe tener entre 8 y 12 caracteres"
    
    # Al menos una letra mayúscula
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    # Al menos una letra minúscula
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    # Al menos un carácter especial
    caracteres_especiales = r'[.,*+$&#!@#$%^&*()_=+~`<>;:"|]'
    if not re.search(caracteres_especiales, password):
        return False, "La contraseña debe contener al menos uno de estos caracteres especiales: .,*+$&#!@#$%^&*()_=+~`<>;:"
    
    return True, "Contraseña válida"


@register_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        nombre = request.form.get('nombre')
        apellido_paterno = request.form.get('apellido_paterno')
        apellido_materno = request.form.get('apellido_materno')
        id_institucion = request.form.get('id_institucion')
        telefono = request.form.get('telefono')
        id_area = request.form.get('id_area')
        matricula = request.form.get('matricula')
        user_type = request.form.get('user_type')  # nuevo campo
        wants_admin_inst = request.form.get('wants_admin_inst') == 'on'
        wants_lab_admin = request.form.get('wants_lab_admin') == 'on'
        lab_id = request.form.get('lab_id')
        # múltiples instituciones (solo investigador)
        id_instituciones_multi = request.form.getlist('id_instituciones')
        id_rol = 2
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = {
            'username': 'Usuario',
            'email': 'Email',
            'password': 'Contraseña',
            'confirm_password': 'Confirmación de contraseña',
            'nombre': 'Nombre',
            'apellido_paterno': 'Apellido paterno',
            'apellido_materno': 'Apellido materno',
            'telefono': 'Teléfono',
            # matrícula se valida condicionalmente más abajo
        }
        
        # Campos opcionales
        campos_opcionales = {
            'id_area': 'Área',
            'id_institucion': 'Institución'
        }
        
        campos_faltantes = []
        for campo, etiqueta in campos_requeridos.items():
            if not locals().get(campo):
                campos_faltantes.append(etiqueta)
        
        if campos_faltantes:
            flash(f'Los siguientes campos son obligatorios: {", ".join(campos_faltantes)}', 'error')
            return render_template('register.html')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        # Validar formato de contraseña
        password_valida, mensaje_password = validar_password(password)
        if not password_valida:
            flash(mensaje_password, 'error')
            return render_template('register.html')
        
        # Validar matrícula solo si es estudiante
        if user_type == 'estudiante':
            if not validar_matricula(matricula):
                flash('El formato de la matrícula no es válido', 'error')
                return render_template('register.html')
        else:
            matricula = None
        
        # Validar formato de teléfono
        if not telefono.isdigit() or len(telefono) != 10:
            flash('El teléfono debe contener 10 dígitos numéricos', 'error')
            return render_template('register.html')
        
        # Validar que la institución exista (solo si se proporciona)
        try:
            if id_institucion and id_institucion.strip() and not Institucion.query.get(id_institucion):
                flash('La institución seleccionada no es válida', 'error')
                return render_template('register.html')
        except Exception as inst_error:
            print(f"Error al validar institución: {inst_error}")
            # Continuar sin validar institución si hay problemas con SQLAlchemy
        
        try:
            conn = get_db_connection()
            if not conn:
                flash('Error de conexión a la base de datos', 'error')
                return render_template('register.html')
            cursor = conn.cursor()
            
            # Verificar username
            cursor.execute("SELECT id_usuario FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone() is not None:
                flash('El nombre de usuario ya está registrado', 'error')
                return render_template('register.html')
            
            # Verificar email
            cursor.execute("SELECT id_usuario FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone() is not None:
                flash('El email ya está registrado', 'error')
                return render_template('register.html')
                
            # Verificar matrícula solo si aplica
            if matricula:
                cursor.execute("SELECT id_usuario FROM usuario WHERE matricula = %s", (matricula,))
                if cursor.fetchone() is not None:
                    flash('La matrícula ya está registrada', 'error')
                    return render_template('register.html')
                
            # Verificar teléfono
            cursor.execute("SELECT id_usuario FROM usuario WHERE telefono = %s", (telefono,))
            if cursor.fetchone() is not None:
                flash('El teléfono ya está registrado', 'error')
                return render_template('register.html')
            
            # Hash de la contraseña
            hashed_password = generate_password_hash(password)
            
            # Validar tipos de datos antes de la inserción
            try:
                id_institucion = int(id_institucion) if id_institucion and id_institucion.strip() else None
                id_area = int(id_area) if id_area and id_area.strip() else None
                id_rol = int(id_rol)
            except (ValueError, TypeError) as ve:
                flash(f'Error en los datos numéricos: {ve}', 'error')
                return render_template('register.html')
            
            print(f"Datos a insertar: nombre={nombre}, email={email}, username={username}, telefono={telefono}")
            print(f"IDs: institucion={id_institucion}, area={id_area}, rol={id_rol}")
            
            # Determinar rol base y campos adicionales según tipo
            # 2 = Usuario Regular por defecto; mapear "Usuario" -> Usuario Regular
            id_rol = 2
            if user_type in ['docente', 'investigador', 'estudiante', 'normal', 'usuario']:
                id_rol = 2

            # Si es investigador, exigir área
            if user_type == 'investigador' and not id_area:
                flash('Para registrarte como investigador debes seleccionar un área', 'error')
                return render_template('register.html')

            # Insertar nuevo usuario (marcar como inactivo hasta activar por correo)
            sql = """
            INSERT INTO usuario (
                nombre, apellido_paterno, apellido_materno, email, username, password,
                telefono, id_institucion, matricula, id_rol, id_area, activo, fecha_registro
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            from datetime import datetime
            fecha_actual = datetime.now()
            valores = (
                nombre, apellido_paterno, apellido_materno, email, username, hashed_password,
                telefono, id_institucion, matricula, id_rol, id_area, 0, fecha_actual
            )
            
            print(f"SQL: {sql}")
            print(f"Valores: {valores}")
            
            cursor.execute(sql, valores)
            conn.commit()
            # Log de creación de cuenta
            try:
                from app.utils.audit import log_user_action
                # Obtener ID del insert
                cursor.execute("SELECT LAST_INSERT_ID()")
                _uid = cursor.fetchone()[0]
                log_user_action(_uid, 'crear_cuenta', extra=f'username={username}; email={email}')
            except Exception:
                pass

            # Obtener id del usuario insertado para tablas puente/solicitudes
            try:
                from app.models.role_request import RoleRequest
                from app.utils.notifications import notify_super_admins
                # Obtener id del usuario insertado
                cursor.execute("SELECT LAST_INSERT_ID()")
                new_user_id = cursor.fetchone()[0]
                # Insertar instituciones múltiples si aplica
                try:
                    if user_type == 'investigador' and id_instituciones_multi:
                        for inst_id in id_instituciones_multi:
                            try:
                                cursor.execute(
                                    "INSERT IGNORE INTO usuario_institucion (id_usuario, id_institucion) VALUES (%s, %s)",
                                    (new_user_id, int(inst_id))
                                )
                            except Exception:
                                continue
                        conn.commit()
                except Exception:
                    pass
                requests = []
                # Solicitudes por checkboxes explícitos
                if wants_admin_inst:
                    requests.append(('administrativo', None))
                if wants_lab_admin:
                    requests.append(('admin_laboratorio', int(lab_id) if lab_id and lab_id.strip() else None))

                # Solicitudes implícitas por tipo de usuario seleccionado
                if user_type == 'administrativo' and ('administrativo', None) not in requests:
                    requests.append(('administrativo', None))
                if user_type == 'admin_laboratorio':
                    requested_lab = int(lab_id) if lab_id and lab_id.strip() else None
                    if ('admin_laboratorio', requested_lab) not in requests:
                        requests.append(('admin_laboratorio', requested_lab))
                if user_type == 'investigador' and ('investigador', None) not in requests:
                    # Para investigador no se asigna rol inmediato; requiere aprobación
                    requests.append(('investigador', None))

                # Mantener SIEMPRE como usuario simple hasta aprobación
                try:
                    id_rol = 2
                except Exception:
                    id_rol = 2

                request_records = []
                for (req_role, lab) in requests:
                    rr = RoleRequest(id_usuario=new_user_id, requested_role=req_role, id_laboratorio=lab)
                    db.session.add(rr)
                    request_records.append(rr)
                if request_records:
                    db.session.commit()  # rr.id_request poblado
                    # Notificar a Super Admins
                    try:
                        detalles = []
                        for (req_role, lab) in requests:
                            if req_role == 'admin_laboratorio':
                                detalles.append(f"{req_role} (lab_id={lab if lab else 'sin seleccionar'})")
                            else:
                                detalles.append(req_role)
                        # Email detallado a super admins
                        resumen_usuario = f"Nombre: {nombre} {apellido_paterno} {apellido_materno} | Username: {username} | Email: {email}"
                        # Enlaces de aprobación por token para el primer rol solicitado (y uno por cada rol)
                        try:
                            from app.utils.email_service import generate_approval_token
                            enlaces = []
                            # enlazar por id_request real
                            for rr in request_records:
                                payload_ok = {'request_id': rr.id_request, 'action': 'aprobar'}
                                payload_no = {'request_id': rr.id_request, 'action': 'rechazar'}
                                token_ok = generate_approval_token(payload_ok)
                                token_no = generate_approval_token(payload_no)
                                url_ok = url_for('admin_roles.approve_with_token', token=token_ok, _external=True)
                                url_no = url_for('admin_roles.approve_with_token', token=token_no, _external=True)
                                etiqueta = rr.requested_role
                                if rr.requested_role == 'admin_laboratorio' and rr.id_laboratorio:
                                    etiqueta += f" (lab_id={rr.id_laboratorio})"
                                enlaces.append(f"<li>{etiqueta}: <a href='{url_ok}'>Aprobar</a> | <a href='{url_no}'>Rechazar</a></li>")
                            enlaces_html = '<ul>' + ''.join(enlaces) + '</ul>'
                        except Exception:
                            enlaces_html = ''

                        # Construir listado de instituciones adicionales
                        institutos_html = ''
                        try:
                            if user_type == 'investigador' and id_instituciones_multi:
                                cursor.execute(
                                    "SELECT nombre_institucion FROM institucion WHERE id_institucion IN (" + ",".join(["%s"]*len(id_instituciones_multi)) + ")",
                                    tuple(int(x) for x in id_instituciones_multi)
                                )
                                nombres = [row[0] if isinstance(row, tuple) else row['nombre_institucion'] for row in cursor.fetchall()]
                                if nombres:
                                    institutos_html = '<br/><strong>Instituciones adicionales:</strong> ' + ', '.join(nombres)
                        except Exception:
                            pass

                        # Usar plantilla configurable
                        try:
                            from app.models.monthly_report import SystemKV
                            subj = (SystemKV.query.get('email.role_request.subject') or SystemKV(key='email.role_request.subject', value='SIGRAL - Nueva solicitud de rol')).value
                            html_tmpl = (SystemKV.query.get('email.role_request.html') or SystemKV(key='email.role_request.html', value='<div style="font-family: Arial, sans-serif; line-height:1.6;"><h3>Nueva solicitud de rol</h3><p><strong>Usuario:</strong> {{ user_name }} | <strong>Usuario:</strong> {{ username }} | <strong>Email:</strong> {{ user_email }}</p><p><strong>Solicitudes:</strong> {{ requested_roles }}</p>{{ extra_instituciones }}<div>{{ approval_links_html }}</div><p style="color:#6b7280; font-size:12px;">Fecha: {{ fecha }}</p></div>')).value
                            html_msg = (html_tmpl
                                .replace('{{ user_name }}', f"{nombre} {apellido_paterno} {apellido_materno}")
                                .replace('{{ username }}', username)
                                .replace('{{ user_email }}', email)
                                .replace('{{ requested_roles }}', ', '.join(detalles))
                                .replace('{{ extra_instituciones }}', institutos_html)
                                .replace('{{ approval_links_html }}', enlaces_html)
                                .replace('{{ fecha }}', fecha_actual.strftime('%Y-%m-%d %H:%M:%S'))
                            )
                            from app.utils.notifications import get_super_admin_emails
                            recipients = get_super_admin_emails()
                            for to in recipients:
                                try:
                                    from app.utils.email_service import send_email
                                    send_email(subject=subj, to_email=to, html_body=html_msg)
                                except Exception:
                                    continue
                        except Exception:
                            # Fallback al mecanismo anterior
                            mensaje = (
                                f"Se registró una nueva solicitud de rol.<br/>"
                                f"<strong>Usuario:</strong> {resumen_usuario}<br/>"
                                f"<strong>Solicitudes:</strong> {', '.join(detalles)}<br/>"
                                f"{institutos_html}"
                                f"{enlaces_html}"
                                f"<strong>Fecha:</strong> {fecha_actual.strftime('%Y-%m-%d %H:%M:%S')}"
                            )
                            notify_super_admins(
                                subject='SIGRAL - Nueva solicitud de rol',
                                message=mensaje
                            )
                        # Notificar Admin Institucional si aplica
                        try:
                            if id_institucion:
                                from app.models.user import User
                                from app.models.roles import Roles
                                aliases = ['Admin Institucional']
                                rid = db.session.query(Roles.id_rol).filter(Roles.nombre_rol.in_(aliases)).first()
                                if rid:
                                    admins_inst = User.query.filter(User.id_institucion==id_institucion, User.id_rol==rid.id_rol).all()
                                    for adm in admins_inst:
                                        try:
                                            from app.models.monthly_report import SystemKV
                                            subj2 = (SystemKV.query.get('email.institution_role_request.subject') or SystemKV(key='email.institution_role_request.subject', value='SIGRAL - Nueva solicitud en tu institución')).value
                                            html2 = (SystemKV.query.get('email.institution_role_request.html') or SystemKV(key='email.institution_role_request.html', value='<div style="font-family: Arial, sans-serif; line-height:1.6;"><h3>Nueva solicitud de usuario en tu institución</h3><p>Hola {{ inst_admin_name }},</p><p><strong>Usuario:</strong> {{ user_name }} ({{ username }}) - {{ user_email }}</p><p><strong>Solicitudes:</strong> {{ requested_roles }}</p><p style="color:#6b7280; font-size:12px;">Fecha: {{ fecha }}</p></div>')).value
                                            html2 = (html2
                                                     .replace('{{ inst_admin_name }}', getattr(adm, 'nombre', '') or 'Administrador')
                                                     .replace('{{ user_name }}', f"{nombre} {apellido_paterno} {apellido_materno}")
                                                     .replace('{{ username }}', username)
                                                     .replace('{{ user_email }}', email)
                                                     .replace('{{ requested_roles }}', ', '.join(detalles))
                                                     .replace('{{ fecha }}', fecha_actual.strftime('%Y-%m-%d %H:%M:%S')))
                                            from app.utils.email_service import send_email
                                            send_email(subject=subj2, to_email=adm.email, html_body=html2)
                                        except Exception:
                                            continue
                        except Exception:
                            pass
                    except Exception:
                        pass
            except Exception as _:
                pass
            
            # Enviar correo de activación (best-effort)
            try:
                token = generate_token(email)
                activation_url = url_for('auth.activate', token=token, _external=True)
                send_activation_email(to_email=email, nombre=nombre, activation_url=activation_url)
            except Exception:
                pass

            flash('Registro exitoso. Revisa tu correo para activar tu cuenta. Si solicitaste roles avanzados, serán revisados por un Super Admin.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"Error en el registro: {e}")
            print(f"Tipo de error: {type(e)}")
            import traceback
            traceback.print_exc()
            flash(f'Error en el registro: {str(e)}', 'error')
            return render_template('register.html')
            
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn:
                conn.close()
    
    return render_template('register.html')