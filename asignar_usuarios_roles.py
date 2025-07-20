#!/usr/bin/env python
"""
Script para asignar usuarios a roles específicos
Ejecutar: python asignar_usuarios_roles.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.roles import Roles
from app.models.user import User

def mostrar_usuarios_y_roles():
    """Muestra todos los usuarios y roles disponibles"""
    print("👥 USUARIOS DISPONIBLES:")
    print("-" * 40)
    
    usuarios = User.query.all()
    if not usuarios:
        print("   ⚠️  No hay usuarios en el sistema")
        return [], []
    
    for i, user in enumerate(usuarios, 1):
        rol_actual = user.roles.nombre_rol if user.roles else "Sin rol"
        print(f"   {i}. {user.username} ({user.nombre_completo})")
        print(f"      📧 {user.email}")
        print(f"      🎭 Rol actual: {rol_actual}")
        print(f"      🔹 Activo: {'Sí' if user.activo else 'No'}")
        print()
    
    print("🎭 ROLES DISPONIBLES:")
    print("-" * 40)
    
    roles = Roles.query.all()
    if not roles:
        print("   ⚠️  No hay roles en el sistema")
        return usuarios, []
    
    for i, role in enumerate(roles, 1):
        usuarios_con_rol = User.query.filter_by(id_rol=role.id_rol).count()
        permisos_count = len(role.permisos_rol)
        print(f"   {i}. {role.nombre_rol}")
        print(f"      📝 {role.descripcion}")
        print(f"      👥 {usuarios_con_rol} usuarios asignados")
        print(f"      🔑 {permisos_count} permisos")
        print()
    
    return usuarios, roles

def asignar_usuario_a_rol(usuarios, roles):
    """Permite asignar un usuario a un rol específico"""
    print("🔄 ASIGNAR USUARIO A ROL")
    print("-" * 40)
    
    try:
        # Seleccionar usuario
        print("Selecciona un usuario:")
        for i, user in enumerate(usuarios, 1):
            print(f"   {i}. {user.username} ({user.nombre_completo})")
        
        user_choice = input("\nIngresa el número del usuario: ")
        user_index = int(user_choice) - 1
        
        if user_index < 0 or user_index >= len(usuarios):
            print("❌ Número de usuario inválido")
            return False
        
        selected_user = usuarios[user_index]
        
        # Seleccionar rol
        print(f"\nSelecciona un rol para {selected_user.username}:")
        for i, role in enumerate(roles, 1):
            print(f"   {i}. {role.nombre_rol}")
        
        role_choice = input("\nIngresa el número del rol: ")
        role_index = int(role_choice) - 1
        
        if role_index < 0 or role_index >= len(roles):
            print("❌ Número de rol inválido")
            return False
        
        selected_role = roles[role_index]
        
        # Confirmar asignación
        rol_anterior = selected_user.roles.nombre_rol if selected_user.roles else "Sin rol"
        print(f"\n📋 CONFIRMACIÓN:")
        print(f"   👤 Usuario: {selected_user.username} ({selected_user.nombre_completo})")
        print(f"   🎭 Rol anterior: {rol_anterior}")
        print(f"   🎯 Rol nuevo: {selected_role.nombre_rol}")
        
        confirm = input("\n¿Confirmas la asignación? (s/n): ")
        
        if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            # Realizar la asignación
            selected_user.id_rol = selected_role.id_rol
            db.session.commit()
            
            print(f"\n✅ Usuario {selected_user.username} asignado al rol {selected_role.nombre_rol}")
            return True
        else:
            print("❌ Asignación cancelada")
            return False
            
    except ValueError:
        print("❌ Entrada inválida. Por favor ingresa un número.")
        return False
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la asignación: {str(e)}")
        return False

def asignaciones_recomendadas():
    """Muestra asignaciones recomendadas basadas en análisis"""
    print("💡 ASIGNACIONES RECOMENDADAS")
    print("-" * 50)
    
    usuarios = User.query.all()
    
    # Buscar usuarios que podrían ser administradores
    posibles_admins = []
    for user in usuarios:
        # Criterios para ser administrador
        if (user.username.lower() in ['admin', 'administrador', 'root', 'superuser'] or
            'admin' in user.email.lower() or
            user.username.lower().startswith('admin')):
            posibles_admins.append(user)
    
    if posibles_admins:
        print("🛡️  CANDIDATOS PARA ADMINISTRADOR:")
        for user in posibles_admins:
            rol_actual = user.roles.nombre_rol if user.roles else "Sin rol"
            print(f"   • {user.username} ({user.email}) - Rol actual: {rol_actual}")
    
    # Buscar usuarios sin rol
    usuarios_sin_rol = User.query.filter_by(id_rol=None).all()
    if usuarios_sin_rol:
        print(f"\n⚠️  USUARIOS SIN ROL ASIGNADO ({len(usuarios_sin_rol)}):")
        for user in usuarios_sin_rol:
            print(f"   • {user.username} ({user.email})")
        print("   💡 Recomendación: Asignar rol 'Usuario Regular' por defecto")
    
    # Análisis por dominio de email
    dominios_institucionales = {}
    for user in usuarios:
        if user.email:
            dominio = user.email.split('@')[1] if '@' in user.email else 'desconocido'
            if dominio not in dominios_institucionales:
                dominios_institucionales[dominio] = []
            dominios_institucionales[dominio].append(user)
    
    if len(dominios_institucionales) > 1:
        print(f"\n🏢 ANÁLISIS POR DOMINIO DE EMAIL:")
        for dominio, users in dominios_institucionales.items():
            print(f"   📧 {dominio}: {len(users)} usuarios")
            if len(users) >= 5:  # Dominio con muchos usuarios
                print(f"      💡 Considerar crear rol específico para {dominio}")

def asignar_roles_masivos():
    """Permite asignar un rol a múltiples usuarios"""
    print("🎯 ASIGNACIÓN MASIVA DE ROLES")
    print("-" * 50)
    
    try:
        # Mostrar usuarios sin rol
        usuarios_sin_rol = User.query.filter_by(id_rol=None).all()
        if not usuarios_sin_rol:
            print("✅ Todos los usuarios ya tienen roles asignados")
            return
        
        print(f"📋 Usuarios sin rol ({len(usuarios_sin_rol)}):")
        for user in usuarios_sin_rol:
            print(f"   • {user.username} ({user.email})")
        
        # Seleccionar rol para asignar
        roles = Roles.query.all()
        print(f"\n🎭 Selecciona un rol para asignar a todos:")
        for i, role in enumerate(roles, 1):
            print(f"   {i}. {role.nombre_rol}")
        
        role_choice = input("\nIngresa el número del rol: ")
        role_index = int(role_choice) - 1
        
        if role_index < 0 or role_index >= len(roles):
            print("❌ Número de rol inválido")
            return
        
        selected_role = roles[role_index]
        
        # Confirmar asignación masiva
        print(f"\n📋 CONFIRMACIÓN:")
        print(f"   🎯 Rol: {selected_role.nombre_rol}")
        print(f"   👥 Usuarios afectados: {len(usuarios_sin_rol)}")
        
        confirm = input("\n¿Confirmas la asignación masiva? (s/n): ")
        
        if confirm.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            # Realizar asignación masiva
            for user in usuarios_sin_rol:
                user.id_rol = selected_role.id_rol
            
            db.session.commit()
            print(f"\n✅ {len(usuarios_sin_rol)} usuarios asignados al rol {selected_role.nombre_rol}")
        else:
            print("❌ Asignación cancelada")
            
    except ValueError:
        print("❌ Entrada inválida. Por favor ingresa un número.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error durante la asignación masiva: {str(e)}")

def resumen_asignaciones():
    """Muestra un resumen de las asignaciones actuales"""
    print("📊 RESUMEN DE ASIGNACIONES")
    print("-" * 50)
    
    roles = Roles.query.all()
    total_usuarios = User.query.count()
    
    for role in roles:
        usuarios_rol = User.query.filter_by(id_rol=role.id_rol).all()
        count = len(usuarios_rol)
        percentage = (count / total_usuarios * 100) if total_usuarios > 0 else 0
        
        print(f"🎭 {role.nombre_rol}: {count} usuarios ({percentage:.1f}%)")
        
        if count > 0:
            for user in usuarios_rol:
                status = "✅ Activo" if user.activo else "❌ Inactivo"
                print(f"   • {user.username} ({user.email}) - {status}")
        print()
    
    # Usuarios sin rol
    usuarios_sin_rol = User.query.filter_by(id_rol=None).count()
    if usuarios_sin_rol > 0:
        percentage = (usuarios_sin_rol / total_usuarios * 100) if total_usuarios > 0 else 0
        print(f"⚠️  Sin rol asignado: {usuarios_sin_rol} usuarios ({percentage:.1f}%)")

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        print("🚀 ASIGNADOR DE USUARIOS A ROLES")
        print("=" * 60)
        
        while True:
            print("\n📋 MENÚ DE OPCIONES:")
            print("1. 👥 Mostrar usuarios y roles")
            print("2. 🔄 Asignar usuario individual a rol")
            print("3. 🎯 Asignación masiva de roles")
            print("4. 💡 Ver asignaciones recomendadas")
            print("5. 📊 Resumen de asignaciones")
            print("6. 🚪 Salir")
            
            choice = input("\nSelecciona una opción: ")
            
            if choice == '1':
                usuarios, roles = mostrar_usuarios_y_roles()
                
            elif choice == '2':
                usuarios, roles = mostrar_usuarios_y_roles()
                if usuarios and roles:
                    asignar_usuario_a_rol(usuarios, roles)
                
            elif choice == '3':
                asignar_roles_masivos()
                
            elif choice == '4':
                asignaciones_recomendadas()
                
            elif choice == '5':
                resumen_asignaciones()
                
            elif choice == '6':
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción inválida. Por favor selecciona 1-6.")
            
            input("\nPresiona Enter para continuar...")

if __name__ == "__main__":
    main() 