from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user
from config import Config
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from flask_migrate import Migrate
from flask_cors import CORS

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    from app.models.user import User
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Habilitar CORS para APIs (ajusta origins según tu dominio frontend)
    try:
        CORS(app, resources={r"/api/*": {"origins": "*"}})
    except Exception:
        pass
    
    # Asegurarse de que hay una clave secreta
    if not app.secret_key:
        app.secret_key = 'tu_clave_secreta_aqui'
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    with app.app_context():
        # Importar modelos
        from app.models.area import Area
        from app.models.user import User
        from app.models.institucion import Institucion
        from app.models.tipo_institucion import Tipo_Institucion
        from app.models.roles import Roles
        from app.models.laboratorio import Laboratorio
        from app.models.solicitud import Solicitud
        from app.models.tipo_solicitud import Tipo_Solicitud
        from app.models.tipo_laboratorio import Tipo_Laboratorio
        from app.models.proyecto import Proyecto
        from app.models.proyecto_usuario import ProyectoUsuario
        from app.models.proyecto_audit import ProyectoAudit
        from app.models.monthly_report import SystemKV, MonthlyReport
        from app.models.proyecto_request import ProyectoRequest
        # Crear todas las tablas
        db.create_all()
        # Semillas idempotentes de datos esenciales
        try:
            from app.utils.bootstrap_data import ensure_core_data
            ensure_core_data()
        except Exception:
            pass
        
    from app.controllers.login_controller import auth_bp
    from app.controllers.home_controller import home_bp
    from app.controllers.dashboard_controller import dashboard_bp
    from app.controllers.profile_controller import profile_bp
    from app.controllers.register_controller import register_bp
    from app.controllers.institucion_controller import institucion_bp
    from app.controllers.area_controller import area_bp
    from app.controllers.laboratorio_controller import laboratorio_bp
    from app.controllers.solicitud_controller import solicitud_bp
    
    from app.controllers.admin_areas_controller import admin_areas_bp
    from app.controllers.admin_users_controller import admin_users_bp
    from app.controllers.admin_options_controller import admin_options_bp
    from app.controllers.admin_roles_controller import admin_roles_bp
    from app.controllers.admin_permisos_controller import admin_permisos_bp
    from app.controllers.admin_laboratorios_controller import admin_laboratorios_bp
    from app.controllers.admin_instituciones_controller import admin_instituciones_bp
    from app.controllers.admin_proyectos_controller import admin_proyectos_bp
    from app.controllers.admin_reports_controller import admin_reports_bp
    from app.controllers.proyecto_requests_controller import proj_req_bp
    from app.controllers.admin_emails_controller import admin_emails_bp

    #API
    from app.apis.user_api import user_api_bp
    from app.apis.area_api import area_api_bp
    from app.apis.laboratorio_api import laboratorio_api_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(home_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(register_bp)
    app.register_blueprint(area_api_bp)
    app.register_blueprint(area_bp)
    app.register_blueprint(institucion_bp)
    app.register_blueprint(user_api_bp)
    app.register_blueprint(laboratorio_bp)
    app.register_blueprint(laboratorio_api_bp)
    app.register_blueprint(admin_options_bp)
    app.register_blueprint(solicitud_bp)
    app.register_blueprint(admin_users_bp)
    app.register_blueprint(admin_areas_bp)
    app.register_blueprint(admin_roles_bp)
    app.register_blueprint(admin_permisos_bp)
    app.register_blueprint(admin_laboratorios_bp)
    app.register_blueprint(admin_instituciones_bp)
    app.register_blueprint(admin_proyectos_bp)
    app.register_blueprint(admin_reports_bp)
    app.register_blueprint(proj_req_bp)
    app.register_blueprint(admin_emails_bp)

    @app.context_processor
    def utility_processor():
        def get_user_display_name():
            if 'nombre' in session and session['nombre']:
                return f"{session['nombre']} {session.get('apellido_paterno', '')} {session.get('apellido_materno', '')}"
            return session.get('nombre_usuario', '')
        return dict(user_display_name=get_user_display_name)
    
    # Registrar funciones de permisos en el contexto de templates
    @app.context_processor
    def inject_permission_functions():
        from app.utils.permissions import (
            has_permission, has_any_permission, has_all_permissions,
            is_admin, get_user_role, is_super_user, has_admin_access, get_user_permissions
        )
        return {
            'has_permission': has_permission,
            'has_any_permission': has_any_permission,
            'has_all_permissions': has_all_permissions,
            'is_admin': is_admin,
            'get_user_role': get_user_role,
            'is_super_user': is_super_user,
            'has_admin_access': has_admin_access,
            'get_user_permissions': get_user_permissions
        }

    # Middleware simple para invalidar sesiones si cambió el rol
    @app.before_request
    def enforce_role_change_invalidation():
        try:
            from flask_login import current_user
            if not current_user or not current_user.is_authenticated:
                return
            # Comparar sello guardado en sesión con fecha_cambio actual
            sess_stamp = session.get('role_stamp', '')
            try:
                current_stamp = current_user.fecha_cambio.isoformat() if getattr(current_user, 'fecha_cambio', None) else ''
            except Exception:
                current_stamp = ''
            if sess_stamp != current_stamp:
                # Invalidar sesión
                from flask_login import logout_user
                logout_user()
                session.clear()
                from flask import redirect, url_for, flash
                flash('Tu rol fue actualizado. Por seguridad, inicia sesión nuevamente.', 'info')
                return redirect(url_for('auth.login'))
        except Exception:
            return
    
    # Configurar logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Inicio de la aplicación')
    
    return app