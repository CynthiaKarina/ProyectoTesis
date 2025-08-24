from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models.user import User
from app import db
from sqlalchemy.orm import joinedload
from flask_login import login_user, logout_user, login_required
import os
from app.utils.email_service import generate_token, send_password_reset_email, confirm_token
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__)

def prepare_user_data_for_localstorage(user):
    """Prepara los datos del usuario para guardar en localStorage"""
    try:
        # Obtener información adicional del usuario
        role_name = None
        if user.id_rol and user.roles:
            role_name = user.roles.nombre_rol
        
        institucion_nombre = None
        if user.id_institucion and user.institucion:
            institucion_nombre = user.institucion.nombre_institucion
        
        area_nombre = None
        if user.id_area and user.area:
            area_nombre = user.area.nombre_area
        
        # Preparar datos del usuario
        user_data = {
            'id_usuario': user.id_usuario,
            'username': user.username,
            'email': user.email,
            'nombre': user.nombre or '',
            'apellido_paterno': user.apellido_paterno or '',
            'apellido_materno': user.apellido_materno or '',
            'nombre_completo': user.nombre_completo,
            'telefono': user.telefono or '',
            'ruta_imagen': user.get_imagen_url(),
            'id_rol': user.id_rol,
            'role_name': role_name,
            'id_institucion': user.id_institucion,
            'institucion_nombre': institucion_nombre,
            'id_area': user.id_area,
            'area_nombre': area_nombre,
            'activo': user.activo,
            'fecha_registro': user.fecha_registro.isoformat() if user.fecha_registro else None,
            'iniciales': user.iniciales
        }
        
        return user_data
        
    except Exception as e:
        current_app.logger.error(f"Error preparando datos del usuario para localStorage: {str(e)}")
        # Retornar datos mínimos en caso de error, pero incluyendo rol si está disponible
        try:
            role_name = user.roles.nombre_rol if user.id_rol and user.roles else None
        except:
            role_name = None
            
        return {
            'id_usuario': user.id_usuario,
            'username': user.username,
            'email': user.email,
            'nombre': user.nombre or '',
            'apellido_paterno': user.apellido_paterno or '',
            'apellido_materno': user.apellido_materno or '',
            'nombre_completo': user.nombre_completo,
            'telefono': user.telefono or '',
            'ruta_imagen': user.get_imagen_url() if hasattr(user, 'get_imagen_url') else '',
            'id_rol': user.id_rol,
            'role_name': role_name,
            'activo': user.activo,
            'iniciales': user.iniciales if hasattr(user, 'iniciales') else ''
        }

@auth_bp.route('/')
@auth_bp.route('/login')
def login():
    if 'username' in session:
        return redirect(url_for('home.index'))
    return render_template('login.html')

@auth_bp.route('/login', methods=['POST'])
def login_post():
    try:
        login_input = request.form.get('username')  # Puede ser username, email o teléfono
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        # Buscar usuario por username, email o teléfono (sin filtrar por contraseña)
        user = User.query.options(
            joinedload(User.roles),
            joinedload(User.institucion),
            joinedload(User.area)
        ).filter(
            db.or_(
                User.username == login_input,
                User.email == login_input,
                User.telefono == login_input
            )
        ).first()
        
        # Validar cuenta activa y contraseña (hash o texto plano durante transición)
        if user and user.activo and (
            (user.password and isinstance(user.password, str) and user.password == password) or
            (user.password and check_password_hash(user.password, password))
        ):
            # Si la sesión previa debe invalidarse por cambio de rol, podemos forzar re-login por fecha_cambio en cookies si fuera necesario.
            # ✅ REGISTRAR USUARIO EN FLASK-LOGIN (ESTO FALTABA!)
            login_user(user, remember=remember)
            
            # Guardar más información en la sesión
            session['username'] = user.username
            session['user_id'] = user.id_usuario
            session['nombre'] = user.nombre if user.nombre else user.username
            session['id_rol'] = user.id_rol  # Guardar el id del rol
            try:
                session['role_stamp'] = user.fecha_cambio.isoformat() if getattr(user, 'fecha_cambio', None) else ''
            except Exception:
                session['role_stamp'] = ''
            
            # Actualizar último acceso
            try:
                user.ultimo_acceso = datetime.utcnow()
                db.session.commit()
            except Exception:
                db.session.rollback()
            # Log de inicio de sesión
            try:
                from app.utils.audit import log_user_action
                log_user_action(user.id_usuario, 'login', extra=f'remember={remember}')
            except Exception:
                pass
            # Preparar datos del usuario para localStorage
            user_data = prepare_user_data_for_localstorage(user)
            
            # Configurar cookies si se seleccionó "recordar"
            if remember:
                # Nota: Las cookies se configurarán después de la redirección
                session['remember_user'] = True
            else:
                session['remember_user'] = False
            
            # Renderizar template temporal que guardará datos en localStorage
            return render_template('login_success.html', 
                                 user_data=user_data,
                                 redirect_url=url_for('home.index'))
        else:
            if user and not user.activo:
                flash('Tu cuenta aún no está activada. Revisa tu correo para activarla.', 'warning')
                return redirect(url_for('auth.login'))
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        flash(f'Error en el inicio de sesión: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        recovery_input = request.form.get('email')  # Puede ser email, teléfono o username
        
        # Buscar usuario por email, teléfono o username
        user = User.query.filter(
            db.or_(
                User.email == recovery_input,
                User.telefono == recovery_input,
                User.username == recovery_input
            )
        ).first()
        
        if user:
            # Generar token y enviar email
            token = generate_token(user.email)
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            try:
                send_password_reset_email(to_email=user.email, nombre=user.nombre, reset_url=reset_url)
                flash('Hemos enviado un enlace para restablecer tu contraseña a tu correo.', 'success')
            except Exception as _:
                flash('No se pudo enviar el correo de recuperación en este momento.', 'error')
        else:
            flash('Usuario, email o teléfono no encontrado', 'error')
            
        return redirect(url_for('auth.login'))
    return render_template('recover_password.html')


@auth_bp.route('/resend-activation', methods=['POST'])
def resend_activation():
    try:
        recovery_input = request.form.get('email')  # email, username o teléfono
        if not recovery_input:
            flash('Ingresa tu email, usuario o teléfono para reenviar activación.', 'warning')
            return redirect(url_for('auth.login'))

        # Buscar usuario
        user = User.query.filter(
            db.or_(
                User.email == recovery_input,
                User.username == recovery_input,
                User.telefono == recovery_input
            )
        ).first()

        if not user:
            flash('No se encontró un usuario con esos datos.', 'error')
            return redirect(url_for('auth.login'))

        if user.activo:
            flash('Tu cuenta ya está activada. Inicia sesión.', 'info')
            return redirect(url_for('auth.login'))

        # Generar token y enviar email
        token = generate_token(user.email)
        activation_url = url_for('auth.activate', token=token, _external=True)
        html = f"""
        <div style='font-family:Arial,sans-serif;line-height:1.6'>
          <h3>Activa tu cuenta</h3>
          <p>Hola {user.nombre or user.username}, usa el siguiente enlace para activar tu cuenta:</p>
          <p><a href='{activation_url}'>Activar cuenta</a></p>
          <p style='color:#6b7280;font-size:12px'>El enlace expira en 60 minutos.</p>
        </div>
        """
        # Reutilizar send_password_reset_email para canal SMTP o crear un envío genérico
        from app.utils.email_service import send_email
        ok = send_email(subject='SIGRAL - Reenvío de activación', to_email=user.email, html_body=html)
        if ok:
            flash('Te enviamos un nuevo enlace de activación a tu correo.', 'success')
        else:
            flash('No fue posible enviar el correo en este momento.', 'error')
    except Exception as e:
        flash(f'Error reenviando activación: {e}', 'error')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = confirm_token(token, expiration_seconds=3600)
    if not email:
        flash('El enlace de restablecimiento no es válido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not password or not confirm_password:
            flash('Debes ingresar y confirmar la nueva contraseña.', 'error')
            return render_template('reset_password.html')
        if password != confirm_password:
            flash('Las contraseñas no coinciden.', 'error')
            return render_template('reset_password.html')

        # Buscar usuario por email y actualizar contraseña
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('No se encontró el usuario asociado al enlace.', 'error')
            return redirect(url_for('auth.login'))

        # Almacenar hash; si el proyecto usa texto plano en login_post, conviene unificar a hash
        new_hashed = generate_password_hash(password)
        user.password = new_hashed
        db.session.commit()
        flash('Tu contraseña ha sido actualizada. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')


@auth_bp.route('/activate/<token>', methods=['GET'])
def activate(token):
    email = confirm_token(token, expiration_seconds=3600)
    if not email:
        flash('El enlace de activación no es válido o ha expirado.', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('No se encontró el usuario a activar.', 'error')
        return redirect(url_for('auth.login'))

    if user.activo:
        flash('Tu cuenta ya estaba activada. Ahora puedes iniciar sesión.', 'info')
        return redirect(url_for('auth.login'))

    user.activo = True
    db.session.commit()
    flash('Cuenta activada correctamente. Ya puedes iniciar sesión.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
@login_required
def logout():
    # ✅ CERRAR SESIÓN EN FLASK-LOGIN (ESTO FALTABA!)
    logout_user()
    
    # Limpiar sesión de Flask
    session.clear()
    
    # Usar template temporal para limpiar localStorage
    return render_template('logout_success.html',
                         redirect_url=url_for('auth.login'))

@auth_bp.route('/perfil')
def perfil():
    # Redirigir a la ruta correcta del perfil que maneja todas las variables necesarias
    return redirect(url_for('profile.ver_perfil'))

