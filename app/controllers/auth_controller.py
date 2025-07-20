from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.models.user import User
from app import db
from datetime import datetime
from app.models.area import Area
from app.database.connection import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Aquí puedes autenticar con tu modelo
        if username == "admin" and password == "1234":
            flash('Login exitoso', 'success')
            return redirect(url_for('home.home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # Obtener las áreas de la base de datos
    areas = []
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM area")
            areas = cursor.fetchall()
            print("Áreas obtenidas:", areas)  # Para depuración
        except Exception as e:
            print(f"Error al obtener áreas: {str(e)}")
            flash('Error al cargar las áreas', 'error')
        finally:
            cursor.close()
            connection.close()

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
            id_area = request.form.get('id_area')  # Obtener el área seleccionada

            # Validaciones
            if not all([username, email, password, confirm_password, nombre, apellido_paterno, apellido_materno, id_institucion, telefono, id_area]):
                flash('Todos los campos son obligatorios', 'error')
                return render_template('register.html', areas=areas)

            # Verificar si el usuario ya existe
            if User.query.filter_by(username=username).first():
                flash('El nombre de usuario ya está en uso', 'error')
                return render_template('register.html', areas=areas)

            # Verificar si el email ya existe
            if User.query.filter_by(email=email).first():
                flash('El correo electrónico ya está registrado', 'error')
                return render_template('register.html', areas=areas)

            # Verificar que las contraseñas coincidan
            if password != confirm_password:
                flash('Las contraseñas no coinciden', 'error')
                return render_template('register.html', areas=areas)

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
                id_area=id_area,
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
            return render_template('register.html', areas=areas)

    # Si es GET, mostrar formulario
    return render_template('register.html', areas=areas)
