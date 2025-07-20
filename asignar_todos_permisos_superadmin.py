#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para asignar todos los permisos al usuario con rol superAdmin+
"""

from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User
from app import create_app, db

def asignar_todos_permisos_superadmin():
    """Asigna todos los permisos al usuario con rol superAdmin+"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🚀 ASIGNANDO TODOS LOS PERMISOS AL SUPERADMIN+")
        print("="*60)
        
        # Verificar si existe el rol superAdmin+
        superadmin_rol = Roles.query.filter_by(nombre_rol="superAdmin+").first()
        
        if not superadmin_rol:
            print("❌ El rol 'superAdmin+' no existe. Creando rol...")
            
            # Crear el rol superAdmin+
            superadmin_rol = Roles(
                nombre_rol="superAdmin+",
                descripcion="Super Administrador con acceso total al sistema"
            )
            db.session.add(superadmin_rol)
            db.session.flush()  # Para obtener el ID sin hacer commit
            print(f"✅ Rol 'superAdmin+' creado con ID: {superadmin_rol.id_rol}")
        else:
            print(f"✅ Rol 'superAdmin+' encontrado (ID: {superadmin_rol.id_rol})")
        
        # Obtener todos los permisos disponibles
        todos_permisos = Permiso.query.all()
        print(f"📊 Total de permisos disponibles: {len(todos_permisos)}")
        
        # Limpiar permisos existentes del rol superAdmin+
        permisos_existentes = PermisoRol.query.filter_by(id_rol=superadmin_rol.id_rol).all()
        if permisos_existentes:
            print(f"🧹 Eliminando {len(permisos_existentes)} permisos existentes...")
            for permiso_rol in permisos_existentes:
                db.session.delete(permiso_rol)
        
        # Asignar todos los permisos al rol superAdmin+
        print("🔑 Asignando todos los permisos al rol superAdmin+...")
        permisos_asignados = 0
        
        for permiso in todos_permisos:
            # Verificar si el permiso ya está asignado
            existe = PermisoRol.query.filter_by(
                id_rol=superadmin_rol.id_rol, 
                id_permiso=permiso.id_permiso
            ).first()
            
            if not existe:
                nuevo_permiso_rol = PermisoRol(
                    id_rol=superadmin_rol.id_rol,
                    id_permiso=permiso.id_permiso
                )
                db.session.add(nuevo_permiso_rol)
                permisos_asignados += 1
                print(f"  ✅ {permiso.nombre_permiso}")
        
        # Confirmar cambios
        try:
            db.session.commit()
            print(f"\n🎉 ¡ÉXITO! Se asignaron {permisos_asignados} permisos al rol 'superAdmin+'")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios: {str(e)}")
            return False
        
        # Verificar usuarios con el rol superAdmin+
        usuarios_superadmin = User.query.filter_by(id_rol=superadmin_rol.id_rol).all()
        print(f"\n👥 Usuarios con rol 'superAdmin+': {len(usuarios_superadmin)}")
        
        if usuarios_superadmin:
            print("📋 Lista de usuarios con acceso total:")
            for usuario in usuarios_superadmin:
                print(f"  - {usuario.username} ({usuario.nombre_completo})")
        else:
            print("⚠️  No hay usuarios asignados al rol 'superAdmin+'")
            print("💡 Sugerencia: Asigna el rol 'superAdmin+' a un usuario usando:")
            print("   python asignar_usuarios_roles.py")
        
        # Mostrar resumen final
        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO")
        print("="*60)
        print(f"📊 Rol: {superadmin_rol.nombre_rol}")
        print(f"🔑 Permisos asignados: {len(todos_permisos)}")
        print(f"👥 Usuarios con este rol: {len(usuarios_superadmin)}")
        print("="*60)
        
        return True

def actualizar_super_administrador_existente():
    """Actualiza el rol 'Super Administrador' existente con todos los permisos"""
    app = create_app()
    
    with app.app_context():
        print("="*60)
        print("🔄 ACTUALIZANDO ROL 'SUPER ADMINISTRADOR' EXISTENTE")
        print("="*60)
        
        # Buscar el rol Super Administrador
        super_admin_rol = Roles.query.filter_by(nombre_rol="Super Administrador").first()
        
        if not super_admin_rol:
            print("❌ El rol 'Super Administrador' no existe")
            return False
        
        print(f"✅ Rol 'Super Administrador' encontrado (ID: {super_admin_rol.id_rol})")
        
        # Obtener todos los permisos disponibles
        todos_permisos = Permiso.query.all()
        print(f"📊 Total de permisos disponibles: {len(todos_permisos)}")
        
        # Limpiar permisos existentes
        permisos_existentes = PermisoRol.query.filter_by(id_rol=super_admin_rol.id_rol).all()
        if permisos_existentes:
            print(f"🧹 Eliminando {len(permisos_existentes)} permisos existentes...")
            for permiso_rol in permisos_existentes:
                db.session.delete(permiso_rol)
        
        # Asignar todos los permisos
        print("🔑 Asignando todos los permisos al rol 'Super Administrador'...")
        permisos_asignados = 0
        
        for permiso in todos_permisos:
            nuevo_permiso_rol = PermisoRol(
                id_rol=super_admin_rol.id_rol,
                id_permiso=permiso.id_permiso
            )
            db.session.add(nuevo_permiso_rol)
            permisos_asignados += 1
            print(f"  ✅ {permiso.nombre_permiso}")
        
        # Confirmar cambios
        try:
            db.session.commit()
            print(f"\n🎉 ¡ÉXITO! Se asignaron {permisos_asignados} permisos al rol 'Super Administrador'")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios: {str(e)}")
            return False
        
        # Mostrar usuarios afectados
        usuarios_super_admin = User.query.filter_by(id_rol=super_admin_rol.id_rol).all()
        print(f"\n👥 Usuarios con rol 'Super Administrador': {len(usuarios_super_admin)}")
        
        if usuarios_super_admin:
            print("📋 Usuarios que ahora tienen acceso total:")
            for usuario in usuarios_super_admin:
                print(f"  - {usuario.username} ({usuario.nombre_completo})")
        
        print("\n" + "="*60)
        print("✅ ACTUALIZACIÓN COMPLETADA")
        print("="*60)
        print(f"📊 Rol: {super_admin_rol.nombre_rol}")
        print(f"🔑 Permisos asignados: {len(todos_permisos)}")
        print(f"👥 Usuarios con este rol: {len(usuarios_super_admin)}")
        print("="*60)
        
        return True

def menu_principal():
    """Menú principal para elegir la acción"""
    print("="*60)
    print("🔧 CONFIGURACIÓN DE PERMISOS SUPER ADMINISTRADOR")
    print("="*60)
    print("\n¿Qué deseas hacer?")
    print("1. Crear rol 'superAdmin+' con todos los permisos")
    print("2. Actualizar rol 'Super Administrador' existente con todos los permisos")
    print("3. Cancelar")
    
    while True:
        try:
            opcion = input("\nSelecciona una opción (1-3): ").strip()
            
            if opcion == "1":
                return asignar_todos_permisos_superadmin()
            elif opcion == "2":
                return actualizar_super_administrador_existente()
            elif opcion == "3":
                print("❌ Operación cancelada")
                return False
            else:
                print("⚠️  Opción inválida. Por favor selecciona 1, 2 o 3.")
        except KeyboardInterrupt:
            print("\n❌ Operación cancelada por el usuario")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False

if __name__ == "__main__":
    menu_principal() 