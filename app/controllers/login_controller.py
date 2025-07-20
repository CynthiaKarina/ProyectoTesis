from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app, make_response
from werkzeug.utils import secure_filename
from datetime import datetime
from app.models.user import User
from app import db
from sqlalchemy.orm import joinedload
from flask_login import login_user, logout_user, login_required
import os

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
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.options(
            joinedload(User.roles),
            joinedload(User.institucion),
            joinedload(User.area)
        ).filter_by(username=username, password=password).first()
        
        if user:
            # ✅ REGISTRAR USUARIO EN FLASK-LOGIN (ESTO FALTABA!)
            login_user(user, remember=remember)
            
            # Guardar más información en la sesión
            session['username'] = user.username
            session['user_id'] = user.id_usuario
            session['nombre'] = user.nombre if user.nombre else user.username
            session['id_rol'] = user.id_rol  # Guardar el id del rol
            
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
            flash('Usuario o contraseña incorrectos', 'error')
            return redirect(url_for('auth.login'))
            
    except Exception as e:
        flash(f'Error en el inicio de sesión: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Aquí iría la lógica de recuperación de contraseña
            flash('Se han enviado instrucciones a tu correo', 'success')
        else:
            flash('Email no encontrado', 'error')
            
        return redirect(url_for('auth.login'))
    return render_template('recover_password.html')

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

@auth_bp.route('/editar-perfil', methods=['GET', 'POST'])
def editar_perfil():
    # Redirigir a la ruta correcta del perfil que maneja todas las variables necesarias
    return redirect(url_for('profile.editar_perfil'))

@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
def cambiar_password():
    # Redirigir a la ruta correcta del perfil que maneja todas las variables necesarias
    return redirect(url_for('profile.cambiar_password'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
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

            # Validaciones
            if not all([username, email, password, confirm_password, nombre, apellido_paterno, apellido_materno]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('register.html')

            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está en uso', 'error')
                return render_template('register.html')

            # Verificar si el email ya existe
            if User.query.filter_by(email=email).first():
                flash('El correo electrónico ya está registrado', 'error')
                return render_template('register.html')

            # Verificar que las contraseñas coincidan
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('register.html')

            # Crear nuevo usuario
            new_user = User(
                username=username,
                email=email,
                password=password,
                nombre=nombre,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno,
                id_institucion=id_institucion,
                telefono=telefono,
                fecha_registro=datetime.now()
            )

            # Guardar en la base de datos
            db.session.add(new_user)
            db.session.commit()

            # Mensaje de éxito
            flash('¡Registro exitoso! Por favor inicia sesión', 'success')
            return redirect(url_for('auth.login'))

        except Exception as e:
            db.session.rollback()
            flash('Error al registrar usuario. Por favor intente nuevamente.', 'error')
            return render_template('register.html')

    # Si es GET, mostrar formulario
    return render_template('register.html')
