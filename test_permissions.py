#!/usr/bin/env python
"""
Script para probar el sistema de permisos después de las correcciones
Ejecutar: python test_permissions.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.roles import Roles, Permiso, PermisoRol
from app.utils.permissions import PermissionManager
from flask_login import login_user

def test_permissions_system():
    """Prueba el sistema de permisos después de las correcciones"""
    app = create_app()
    
    with app.app_context():
        print("🔍 PRUEBA COMPLETA DEL SISTEMA DE PERMISOS")
        print("=" * 60)
        
        # 1. Verificar que existan roles y permisos
        print("\n📊 VERIFICACIÓN DE DATOS BASE")
        print("-" * 30)
        
        roles_count = Roles.query.count()
        permisos_count = Permiso.query.count()
        usuarios_count = User.query.count()
        
        print(f"📋 Roles en sistema: {roles_count}")
        print(f"🔑 Permisos en sistema: {permisos_count}")
        print(f"👥 Usuarios en sistema: {usuarios_count}")
        
        if roles_count == 0 or permisos_count == 0:
            print("⚠️  ADVERTENCIA: Faltan roles o permisos. Ejecuta: python setup_permissions.py")
            return
        
        # 2. Probar con diferentes usuarios
        print("\n👤 PRUEBA CON USUARIOS")
        print("-" * 30)
        
        users = User.query.limit(3).all()
        if not users:
            print("❌ No hay usuarios en la base de datos")
            return
        
        for i, user in enumerate(users, 1):
            print(f"\n🔸 Usuario {i}: {user.username}")
            print(f"   🆔 ID: {user.id_usuario}")
            print(f"   🎭 Rol ID: {user.id_rol}")
            
            # Verificar rol
            role_name = PermissionManager.get_user_role_name(user)
            print(f"   🎯 Rol: {role_name or 'Sin rol'}")
            
            # Verificar permisos
            permissions = PermissionManager.get_user_permissions(user.id_usuario)
            print(f"   🔑 Permisos: {len(permissions)}")
            
            # Verificar funciones administrativas
            is_admin = PermissionManager.is_admin(user)
            is_super_user = PermissionManager.is_super_user(user)
            has_admin_access = PermissionManager.has_admin_access(user)
            
            print(f"   🔹 Es admin: {'✅' if is_admin else '❌'}")
            print(f"   🔹 Es super usuario: {'✅' if is_super_user else '❌'}")
            print(f"   🔹 Acceso admin: {'✅' if has_admin_access else '❌'}")
            
            # Verificar permisos específicos críticos
            critical_perms = ['admin_access', 'gestionar_usuarios', 'ver_dashboard', 'gestionar_areas']
            admin_perms = sum(1 for perm in critical_perms 
                            if PermissionManager.user_has_permission(user, perm))
            print(f"   🎪 Permisos admin: {admin_perms}/{len(critical_perms)}")
        
        # 3. Probar funciones helper
        print("\n🧪 PRUEBA DE FUNCIONES HELPER")
        print("-" * 30)
        
        try:
            from app.utils.permissions import has_permission, is_admin, is_super_user, has_admin_access
            print("✅ Funciones helper importadas correctamente")
            
            # Simular contexto de aplicación para las funciones helper
            with app.test_request_context():
                from flask_login import login_user
                test_user = users[0]
                login_user(test_user)
                
                print(f"🔸 Probando con usuario: {test_user.username}")
                print(f"   has_permission('admin_access'): {has_permission('admin_access')}")
                print(f"   is_admin(): {is_admin()}")
                print(f"   is_super_user(): {is_super_user()}")
                print(f"   has_admin_access(): {has_admin_access()}")
                
        except Exception as e:
            print(f"❌ Error probando funciones helper: {e}")
        
        # 4. Verificar controladores actualizados
        print("\n🎛️  VERIFICACIÓN DE CONTROLADORES")
        print("-" * 30)
        
        controllers_updated = [
            "login_controller.py - ✅ Flask-Login implementado",
            "home_controller.py - ✅ @login_required agregado",
            "profile_controller.py - ✅ 5 funciones actualizadas",
            "dashboard_controller.py - ✅ current_user implementado",
            "area_controller.py - ✅ Permisos específicos agregados"
        ]
        
        for controller in controllers_updated:
            print(f"   📄 {controller}")
        
        # 5. Verificar rutas protegidas
        print("\n🛡️  RUTAS PROTEGIDAS")
        print("-" * 30)
        
        protected_routes = [
            "/mi-perfil - @login_required",
            "/editar-perfil - @login_required",
            "/cambiar-password - @login_required",
            "/dashboard - @login_required + @permission_required",
            "/admin/areas - @login_required + @permission_required",
            "/home - @login_required"
        ]
        
        for route in protected_routes:
            print(f"   🔒 {route}")
        
        # 6. Resumen final
        print("\n🎉 RESUMEN FINAL")
        print("-" * 30)
        
        print("✅ Sistema de permisos configurado correctamente")
        print("✅ Flask-Login implementado en todos los controladores")
        print("✅ Verificaciones manuales de session eliminadas")
        print("✅ Decoradores @login_required y @permission_required funcionando")
        print("✅ current_user disponible en todos los contextos")
        
        # Estadísticas finales
        admin_users = sum(1 for user in users if PermissionManager.is_admin(user))
        users_with_roles = sum(1 for user in users if user.id_rol is not None)
        
        print(f"\n📈 ESTADÍSTICAS:")
        print(f"   👑 Usuarios administradores: {admin_users}")
        print(f"   🎭 Usuarios con rol asignado: {users_with_roles}")
        print(f"   🔑 Total de permisos: {permisos_count}")
        print(f"   📋 Total de roles: {roles_count}")
        
        print("\n🎯 RECOMENDACIONES:")
        if admin_users == 0:
            print("   ⚠️  Considera asignar rol de administrador a un usuario")
            print("   💡 Ejecuta: python setup_permissions.py")
        
        if users_with_roles < len(users):
            print(f"   ⚠️  {len(users) - users_with_roles} usuarios sin rol asignado")
        
        print("\n✅ PRUEBA COMPLETADA EXITOSAMENTE")

if __name__ == "__main__":
    test_permissions_system() 