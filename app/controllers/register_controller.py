from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.database.connection import get_db_connection
from datetime import datetime
import re
from werkzeug.security import generate_password_hash
from app.models.institucion import Institucion

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
        id_rol = 2
        
        # Validar que todos los campos requeridos estén presentes
        campos_requeridos = {
            'username': 'Matrícula',
            'email': 'Email',
            'password': 'Contraseña',
            'confirm_password': 'Confirmación de contraseña',
            'nombre': 'Nombre',
            'apellido_paterno': 'Apellido paterno',
            'apellido_materno': 'Apellido materno',
            'id_institucion': 'Institución',
            'telefono': 'Teléfono',
            'id_area': 'Área'
        }
        
        campos_faltantes = []
        for campo, nombre in campos_requeridos.items():
            if not locals()[campo]:
                campos_faltantes.append(nombre)
        
        if campos_faltantes:
            flash(f'Los siguientes campos son obligatorios: {", ".join(campos_faltantes)}', 'error')
            return render_template('register.html')
        
        # Validar que las contraseñas coincidan
        if password != confirm_password:
            flash('Las contraseñas no coinciden', 'error')
            return render_template('register.html')
        
        # Validar formato de matrícula
        if not validar_matricula(username):
            flash('El formato de la matrícula no es válido', 'error')
            return render_template('register.html')
        
        # Validar formato de teléfono
        if not telefono.isdigit() or len(telefono) != 10:
            flash('El teléfono debe contener 10 dígitos numéricos', 'error')
            return render_template('register.html')
        
        # Validar que la institución exista
        if not Institucion.query.get(id_institucion):
            flash('La institución seleccionada no es válida', 'error')
            return render_template('register.html')
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Verificar username
            cursor.execute("SELECT IDUsuario FROM usuario WHERE username = %s", (username,))
            if cursor.fetchone() is not None:
                flash('El nombre de usuario ya está registrado', 'error')
                return render_template('register.html')
            
            # Verificar email
            cursor.execute("SELECT IDUsuario FROM usuario WHERE email = %s", (email,))
            if cursor.fetchone() is not None:
                flash('El email ya está registrado', 'error')
                return render_template('register.html')
            
            # Hash de la contraseña
            hashed_password = generate_password_hash(password)
            
            # Insertar nuevo usuario
            sql = """
            INSERT INTO usuario (username, email, password, nombre, apellido_paterno, apellido_materno,
            id_institucion, telefono, id_area, fecha_registro)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (username, email, hashed_password, nombre, apellido_paterno, apellido_materno,
                    id_institucion, telefono, id_area, datetime.now())
            
            cursor.execute(sql, valores)
            conn.commit()
            
            flash('Registro exitoso. Por favor inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"Error en el registro: {e}")
            flash('Error en el registro. Por favor intenta nuevamente.', 'error')
            return render_template('register.html')
            
        finally:
            cursor.close()
            conn.close()
    
    return render_template('register.html')