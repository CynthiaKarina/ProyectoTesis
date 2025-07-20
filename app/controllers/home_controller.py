from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import current_user, login_required

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
@login_required  # ✅ USAR FLASK-LOGIN CORRECTAMENTE
def index():
    # ✅ VERIFICAR ACCESO ADMINISTRATIVO USANDO EL SISTEMA DE PERMISOS
    from app.utils.permissions import has_admin_access
    admin_access = has_admin_access()
    
    return render_template('home.html', usuario=current_user, admin_access=admin_access)

@home_bp.route('/pagina/<nombre>')
@login_required
def navegar_pagina(nombre):
    paginas_permitidas = {
        'productos': 'productos.html',
        'contacto': 'contacto.html',
        'acerca': 'acerca.html'
    }
    
    if nombre in paginas_permitidas:
        return render_template(paginas_permitidas[nombre], usuario=current_user)
    else:
        flash('Página no encontrada', 'error')
        return redirect(url_for('home.index'))

# Nueva ruta para ver la página de prueba con el diseño mejorado
@home_bp.route('/prueba-diseno')
def prueba_diseno():
    """Página de prueba para ver el nuevo sistema de diseño"""
    return render_template('ejemplo-pagina-mejorada.html', usuario=current_user)

@home_bp.route('/prueba-responsivo')
def prueba_responsivo():
    """Página de prueba para verificar la responsividad completa"""
    return render_template('prueba-responsivo.html')

@home_bp.route('/debug-template')
def debug_template():
    """Página de debug para verificar el template"""
    return render_template('debug_simple.html')


