from flask import Blueprint, render_template, session, redirect, url_for, flash
from flask_login import login_required
from app import db
from app.utils.permissions import permission_required

admin_options_bp = Blueprint('admin_options', __name__)

@admin_options_bp.route('/admin/opciones')
@login_required
@permission_required('admin_access')
def admin_options():
    return render_template('admin_options.html')

@admin_options_bp.route('/admin/test')
@login_required
@permission_required('admin_access')
def test_navigation():
    """Ruta de prueba para verificar que la navegación funciona"""
    return "<h1>✅ La navegación funciona correctamente!</h1><p>Si puedes ver esto, significa que los menús desplegables están funcionando.</p>"

