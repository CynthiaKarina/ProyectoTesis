from functools import wraps
from flask import current_app, request, redirect, url_for, flash, abort, session
from flask_login import current_user
from app import db
import logging

class PermissionManager:
    """Gestor central de permisos del sistema"""
    
    @staticmethod
    def get_user_permissions(user_id):
        """Obtiene todos los permisos de un usuario (rol principal + roles adicionales)"""
        try:
            from app.models.user import User
            from app.models.roles import Permiso, PermisoRol
            
            user = User.query.get(user_id)
            if not user:
                return []
            
            # Verificar si el usuario tiene los atributos necesarios
            if not hasattr(user, 'id_rol'):
                return []
            
            permissions = set()
            
            # Permisos del rol principal
            if user.id_rol:
                permisos_rol_principal = db.session.query(Permiso).join(PermisoRol).filter(
                    PermisoRol.id_rol == user.id_rol
                ).all()
                permissions.update([p.nombre_permiso for p in permisos_rol_principal])
            
            return list(permissions)
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error obteniendo permisos del usuario {user_id}: {str(e)}")
            return []
    
    @staticmethod
    def user_has_permission(user, permission_name):
        """Verifica si un usuario tiene un permiso específico"""
        if not user or not user.is_authenticated:
            return False
        
        # Verificar si el usuario tiene los atributos necesarios
        if not hasattr(user, 'id_rol') or not hasattr(user, 'id_usuario'):
            return False
        
        try:
            from app.models.roles import Permiso, PermisoRol
            
            # Verificar en rol principal
            if user.id_rol:
                permission_exists = db.session.query(PermisoRol).join(Permiso).filter(
                    PermisoRol.id_rol == user.id_rol,
                    Permiso.nombre_permiso == permission_name
                ).first()
                
                if permission_exists:
                    return True
            
            return False
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error verificando permiso {permission_name}: {str(e)}")
            return False
    
    @staticmethod
    def user_has_any_permission(user, permissions_list):
        """Verifica si un usuario tiene cualquiera de los permisos de la lista"""
        if not user or not user.is_authenticated:
            return False
        
        for permission in permissions_list:
            if PermissionManager.user_has_permission(user, permission):
                return True
        return False
    
    @staticmethod
    def user_has_all_permissions(user, permissions_list):
        """Verifica si un usuario tiene todos los permisos de la lista"""
        if not user or not user.is_authenticated:
            return False
        
        for permission in permissions_list:
            if not PermissionManager.user_has_permission(user, permission):
                return False
        return True
    
    @staticmethod
    def get_user_role_name(user):
        """Obtiene el nombre del rol principal del usuario"""
        if not user or not user.is_authenticated:
            return None
        
        # Verificar si el usuario tiene los atributos necesarios
        if not hasattr(user, 'id_rol') or not hasattr(user, 'id_usuario'):
            return None
        
        if not user.id_rol:
            return None
        
        try:
            from app.models.roles import Roles
            
            role = Roles.query.get(user.id_rol)
            return role.nombre_rol if role else None
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error obteniendo nombre del rol: {str(e)}")
            return None
    
    @staticmethod
    def is_admin(user):
        """Verifica si un usuario es administrador"""
        role_name = PermissionManager.get_user_role_name(user)
        if not role_name:
            return False
        return role_name.lower() in ['admin', 'administrador', 'super_admin', 'super administrador']
    
    @staticmethod
    def is_super_user(user):
        """Verifica si un usuario es super usuario/super administrador"""
        if not user or not user.is_authenticated:
            return False
        
        # Verificar si tiene el permiso especial de acceso total
        if PermissionManager.user_has_permission(user, 'acceso_total'):
            return True
        
        # Verificar si su rol es Super Administrador
        role_name = PermissionManager.get_user_role_name(user)
        if role_name:
            return role_name.lower() in ['super administrador', 'super_admin', 'superadministrador']
        
        return False
    
    @staticmethod
    def has_admin_access(user):
        """Verifica si un usuario tiene acceso al panel de administración"""
        if not user or not user.is_authenticated:
            return False
        
        # Super usuarios tienen acceso automático
        if PermissionManager.is_super_user(user):
            return True
        
        # Verificar permiso específico de admin_access
        if PermissionManager.user_has_permission(user, 'admin_access'):
            return True
        
        # Verificar si es administrador por rol
        if PermissionManager.is_admin(user):
            return True
        
        return False
    
    @staticmethod
    def get_all_permissions():
        """Obtiene todos los permisos disponibles en el sistema"""
        try:
            from app.models.roles import Permiso
            return Permiso.query.all()
        except Exception as e:
            if hasattr(current_app, 'logger'):
                current_app.logger.error(f"Error obteniendo todos los permisos: {str(e)}")
            return []

# Decoradores para control de acceso
def permission_required(permission_name):
    """Decorador para requerir un permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not PermissionManager.user_has_permission(current_user, permission_name):
                flash('No tienes permisos suficientes para acceder a esta página.', 'error')
                return redirect(url_for('home.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def any_permission_required(permissions_list):
    """Decorador para requerir cualquiera de los permisos de la lista"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            if not PermissionManager.user_has_any_permission(current_user, permissions_list):
                flash('No tienes permisos suficientes para acceder a esta página.', 'error')
                return redirect(url_for('home.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not PermissionManager.is_admin(current_user):
            flash('Se requieren permisos de administrador para acceder a esta página.', 'error')
            return redirect(url_for('home.index'))
        
        return f(*args, **kwargs)
    return decorated_function

def role_required(role_name):
    """Decorador para requerir un rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            user_role = PermissionManager.get_user_role_name(current_user)
            if not user_role or user_role.lower() != role_name.lower():
                flash(f'Se requiere el rol "{role_name}" para acceder a esta página.', 'error')
                return redirect(url_for('home.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Funciones helper para templates
def has_permission(permission_name):
    """Función helper para usar en templates"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        return PermissionManager.user_has_permission(current_user, permission_name)
    except Exception:
        return False

def has_any_permission(permissions_list):
    """Función helper para usar en templates"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        return PermissionManager.user_has_any_permission(current_user, permissions_list)
    except Exception:
        return False

def has_all_permissions(permissions_list):
    """Función helper para usar en templates"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        return PermissionManager.user_has_all_permissions(current_user, permissions_list)
    except Exception:
        return False

def is_admin():
    """Función helper para verificar si el usuario actual es admin"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        return PermissionManager.is_admin(current_user)
    except Exception:
        return False

def get_user_role():
    """Función helper para obtener el rol del usuario actual"""
    try:
        if not current_user or not current_user.is_authenticated:
            return None
        return PermissionManager.get_user_role_name(current_user)
    except Exception:
        return None

def is_super_user():
    """Función helper para verificar si el usuario actual es super usuario"""
    try:
        if not current_user or not current_user.is_authenticated:
            return False
        return PermissionManager.is_super_user(current_user)
    except Exception:
        return False

def has_admin_access():
    """Función helper para verificar si el usuario actual tiene acceso al panel de administración"""
    try:
        # Verificar si tenemos contexto de aplicación Flask
        try:
            from flask import has_app_context
            if not has_app_context():
                return False
        except (ImportError, RuntimeError):
            # Si no podemos verificar el contexto, asumimos que no lo hay
            return False
        
        # Verificar si hay usuario actual
        if not current_user:
            return False
            
        # Verificar si el usuario está autenticado
        try:
            if not current_user.is_authenticated:
                return False
        except AttributeError:
            # Si current_user no tiene is_authenticated, no está autenticado
            return False
        
        # Usar lógica simple en lugar de PermissionManager para evitar errores de importación
        # Verificar permisos básicos directamente
        return (
            has_permission('admin_access') or 
            is_admin() or 
            is_super_user()
        )
    except Exception as e:
        # Log del error si es posible, pero no fallar
        try:
            if hasattr(current_app, 'logger'):
                current_app.logger.warning(f"Error en has_admin_access: {e}")
        except:
            pass
        return False

def get_user_permissions():
    """Función helper para obtener todos los permisos del usuario actual"""
    try:
        if not current_user or not current_user.is_authenticated:
            return []
        return PermissionManager.get_user_permissions(current_user.id_usuario)
    except Exception:
        return []

def handle_permission_error(required_permission=None, required_role=None):
    """Maneja errores de permisos de forma centralizada"""
    if not current_user or not current_user.is_authenticated:
        flash('Debes iniciar sesión para acceder a esta página.', 'warning')
        return redirect(url_for('auth.login'))
    
    if required_permission:
        message = f'No tienes el permiso "{required_permission}" requerido para esta acción.'
    elif required_role:
        message = f'Se requiere el rol "{required_role}" para esta acción.'
    else:
        message = 'No tienes permisos suficientes para realizar esta acción.'
    
    flash(message, 'error')
    
    try:
        user_id = getattr(current_user, 'id_usuario', 'desconocido')
        current_app.logger.warning(
            f"Acceso denegado - Usuario: {user_id}, "
            f"Ruta: {request.path}, "
            f"Permiso requerido: {required_permission}, "
            f"Rol requerido: {required_role}"
        )
    except Exception:
        current_app.logger.warning(
            f"Acceso denegado - Ruta: {request.path}, "
            f"Permiso requerido: {required_permission}, "
            f"Rol requerido: {required_role}"
        )
    
    return redirect(url_for('home.index')) 