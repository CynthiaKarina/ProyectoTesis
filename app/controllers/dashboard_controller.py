from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.user import User
from app.utils.permissions import permission_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
@permission_required('ver_dashboard')
def index():
    try:
        # current_user está disponible automáticamente por @login_required
        user = current_user
        return render_template('dashboard.html', user=user)
    except Exception as e:
        flash('Error al cargar el dashboard', 'error')
        return redirect(url_for('home.index')) 