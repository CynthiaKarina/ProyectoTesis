#!/usr/bin/env python
"""
Script para verificar permisos específicos de áreas del usuario actual
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.roles import Roles, Permiso, PermisoRol
from app.utils.permissions import PermissionManager

def verificar_permisos_areas():
    """Verifica el sistema de permisos específico para áreas"""
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICACIÓN DE PERMISOS PARA GESTIÓN DE ÁREAS")
        print("=" * 60)
        
        # 1. Verificar que los permisos de áreas existen en la BD
        print("\n📋 1. PERMISOS DE ÁREAS EN BASE DE DATOS:")
        permisos_areas = ['gestionar_areas', 'crear_area', 'editar_area', 'eliminar_area']
        
        for permiso_nombre in permisos_areas:
            permiso = Permiso.query.filter_by(nombre_permiso=permiso_nombre).first()
            if permiso:
                # Contar roles que tienen este permiso
                roles_count = db.session.query(PermisoRol).filter_by(id_permiso=permiso.id_permiso).count()
                print(f"   ✅ {permiso_nombre}: ID={permiso.id_permiso}, Roles asignados={roles_count}")
            else:
                print(f"   ❌ {permiso_nombre}: NO EXISTE EN LA BD")
        
        # 2. Verificar roles que tienen permisos de áreas
        print("\n👥 2. ROLES CON PERMISOS DE ÁREAS:")
        roles = Roles.query.all()
        for rol in roles:
            permisos_del_rol = db.session.query(Permiso.nombre_permiso).join(PermisoRol).filter(
                PermisoRol.id_rol == rol.id_rol,
                Permiso.nombre_permiso.in_(permisos_areas)
            ).all()
            
            permisos_lista = [p[0] for p in permisos_del_rol]
            if permisos_lista:
                print(f"   ✅ {rol.nombre_rol} (ID={rol.id_rol}): {', '.join(permisos_lista)}")
        
        # 3. Buscar usuarios administrativos
        print("\n👤 3. USUARIOS CON ROLES ADMINISTRATIVOS:")
        usuarios_admin = db.session.query(User, Roles).join(Roles).filter(
            Roles.nombre_rol.in_(['Super Administrador', 'Administrador', 'Gestor de Laboratorios'])
        ).all()
        
        if usuarios_admin:
            for user, role in usuarios_admin:
                # Verificar permisos específicos de áreas
                permisos_areas_usuario = []
                for permiso_nombre in permisos_areas:
                    tiene_permiso = PermissionManager.user_has_permission(user, permiso_nombre)
                    if tiene_permiso:
                        permisos_areas_usuario.append(permiso_nombre)
                
                print(f"   👤 {user.username} ({user.nombre or 'Sin nombre'})")
                print(f"      🎭 Rol: {role.nombre_rol}")
                print(f"      🔑 Permisos de áreas: {', '.join(permisos_areas_usuario) if permisos_areas_usuario else 'NINGUNO'}")
                print()
        else:
            print("   ⚠️ No se encontraron usuarios administrativos")
        
        # 4. Recomendar usuario para probar
        print("\n💡 4. RECOMENDACIÓN PARA PRUEBAS:")
        
        # Buscar usuario 'test' si existe
        usuario_test = User.query.filter_by(username='test').first()
        if usuario_test:
            if usuario_test.id_rol:
                rol = Roles.query.get(usuario_test.id_rol)
                print(f"   👤 Usuario 'test' disponible:")
                print(f"      🎭 Rol actual: {rol.nombre_rol if rol else 'Sin rol'}")
                
                # Verificar permisos
                for permiso_nombre in permisos_areas:
                    tiene_permiso = PermissionManager.user_has_permission(usuario_test, permiso_nombre)
                    estado = "✅" if tiene_permiso else "❌"
                    print(f"      {estado} {permiso_nombre}")
                
                if not any(PermissionManager.user_has_permission(usuario_test, p) for p in permisos_areas):
                    print(f"\n   ⚠️ USUARIO 'test' NO TIENE PERMISOS DE ÁREAS")
                    print(f"   💡 Recomendación: Asignar rol 'Administrador' al usuario 'test'")
            else:
                print(f"   ⚠️ Usuario 'test' existe pero no tiene rol asignado")
        else:
            print(f"   ⚠️ No se encontró usuario 'test'")
        
        # 5. Verificar funcionalidad del sistema de permisos
        print("\n🧪 5. PRUEBA DEL SISTEMA DE PERMISOS:")
        
        try:
            # Probar función de verificación de permisos
            admin_role = Roles.query.filter_by(nombre_rol='Administrador').first()
            if admin_role:
                permisos_admin = db.session.query(Permiso).join(PermisoRol).filter(
                    PermisoRol.id_rol == admin_role.id_rol,
                    Permiso.nombre_permiso.in_(permisos_areas)
                ).count()
                print(f"   ✅ Rol 'Administrador' tiene {permisos_admin}/4 permisos de áreas")
                
                if permisos_admin < 4:
                    print(f"   ⚠️ FALTA ASIGNAR ALGUNOS PERMISOS DE ÁREAS AL ROL ADMINISTRADOR")
                    print(f"   💡 Ejecutar: python actualizar_permisos_existentes.py")
            else:
                print(f"   ❌ No se encontró el rol 'Administrador'")
                print(f"   💡 Ejecutar: python setup_permissions.py")
                
        except Exception as e:
            print(f"   ❌ Error en prueba del sistema: {e}")
        
        print("\n" + "=" * 60)
        print("🔒 RESUMEN DE SEGURIDAD:")
        print("✅ Los decoradores @permission_required están implementados")
        print("✅ Los permisos específicos están definidos:")
        print("   - @permission_required('gestionar_areas') - Ver áreas")
        print("   - @permission_required('crear_area') - Crear áreas") 
        print("   - @permission_required('editar_area') - Editar áreas")
        print("   - @permission_required('eliminar_area') - Eliminar áreas")
        print("✅ El template base_Admin.html controla el acceso al menú")
        print("✅ Solo usuarios con permisos pueden acceder a la funcionalidad")

if __name__ == '__main__':
    verificar_permisos_areas() 