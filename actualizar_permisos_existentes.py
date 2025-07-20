#!/usr/bin/env python
"""
Script para actualizar permisos de roles existentes
Ejecutar: python actualizar_permisos_existentes.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User

def actualizar_permisos_roles_existentes():
    """Actualiza los permisos de los roles existentes sin crear nuevos roles"""
    
    # Configuración mejorada para roles existentes
    configuracion_roles = {
        'Super Administrador': {
            'permisos': ['acceso_total']  # Este rol especial tiene todos los permisos
        },
        
        'Administrador': {
            'permisos': [
                # Administración general
                'admin_access', 'ver_dashboard',
                
                # Gestión de usuarios
                'gestionar_usuarios', 'crear_usuario', 'editar_usuario', 'eliminar_usuario',
                
                # Gestión de roles y permisos
                'gestionar_roles', 'crear_rol', 'editar_rol', 'eliminar_rol',
                'gestionar_permisos', 'crear_permiso', 'editar_permiso', 'eliminar_permiso', 'asignar_permisos',
                
                # Gestión de laboratorios
                'gestionar_laboratorios', 'crear_laboratorio', 'editar_laboratorio', 'eliminar_laboratorio',
                
                # Gestión de áreas
                'gestionar_areas', 'crear_area', 'editar_area', 'eliminar_area',
                
                # Gestión de instituciones
                'gestionar_instituciones', 'crear_institucion', 'editar_institucion', 'eliminar_institucion',
                
                # Gestión de solicitudes
                'ver_solicitudes', 'crear_solicitud', 'editar_solicitud', 'eliminar_solicitud',
                'aprobar_solicitud', 'rechazar_solicitud', 'ver_todas_solicitudes',
                
                # Perfil
                'ver_perfil', 'editar_perfil', 'cambiar_password',
                
                # Reportes
                'ver_reportes', 'generar_reportes'
            ]
        },
        
        'Gestor de Laboratorios': {
            'permisos': [
                'ver_dashboard',
                
                # Laboratorios (completo)
                'gestionar_laboratorios', 'crear_laboratorio', 'editar_laboratorio', 'eliminar_laboratorio',
                
                # Áreas (solo gestionar, para laboratorios)
                'gestionar_areas',
                
                # Solicitudes (completo)
                'ver_solicitudes', 'crear_solicitud', 'editar_solicitud', 'eliminar_solicitud',
                'aprobar_solicitud', 'rechazar_solicitud', 'ver_todas_solicitudes',
                
                # Perfil
                'ver_perfil', 'editar_perfil', 'cambiar_password',
                
                # Reportes
                'ver_reportes'
            ]
        },
        
        'Usuario Regular': {
            'permisos': [
                'ver_dashboard',
                
                # Solicitudes (básico)
                'crear_solicitud', 'editar_solicitud', 'ver_solicitudes',
                
                # Perfil
                'ver_perfil', 'editar_perfil', 'cambiar_password'
            ]
        },
        
        'Invitado': {
            'permisos': [
                'ver_dashboard',
                'ver_perfil'
            ]
        }
    }
    
    print("🔄 ACTUALIZANDO PERMISOS DE ROLES EXISTENTES")
    print("=" * 60)
    
    for nombre_rol, config in configuracion_roles.items():
        print(f"\n🎭 Actualizando rol: {nombre_rol}")
        
        # Buscar el rol existente
        role = Roles.query.filter_by(nombre_rol=nombre_rol).first()
        if not role:
            print(f"   ⚠️  Rol no encontrado: {nombre_rol} - Se omite")
            continue
        
        # Limpiar permisos existentes
        permisos_anteriores = PermisoRol.query.filter_by(id_rol=role.id_rol).count()
        PermisoRol.query.filter_by(id_rol=role.id_rol).delete()
        
        # Asignar nuevos permisos
        permisos_asignados = 0
        permisos_no_encontrados = []
        
        for nombre_permiso in config['permisos']:
            permiso = Permiso.query.filter_by(nombre_permiso=nombre_permiso).first()
            if permiso:
                perm_rol = PermisoRol(id_rol=role.id_rol, id_permiso=permiso.id_permiso)
                db.session.add(perm_rol)
                permisos_asignados += 1
            else:
                permisos_no_encontrados.append(nombre_permiso)
        
        print(f"   📊 Permisos anteriores: {permisos_anteriores}")
        print(f"   ✅ Permisos nuevos: {permisos_asignados}")
        print(f"   📈 Cambio: {permisos_asignados - permisos_anteriores:+d}")
        
        if permisos_no_encontrados:
            print(f"   ⚠️  Permisos no encontrados: {len(permisos_no_encontrados)}")
            for perm in permisos_no_encontrados:
                print(f"      - {perm}")
    
    return True

def mostrar_antes_y_despues():
    """Muestra un resumen antes y después de los cambios"""
    print("\n📊 RESUMEN DE CAMBIOS")
    print("=" * 60)
    
    roles = Roles.query.all()
    for role in roles:
        permisos_count = len(role.permisos_rol)
        print(f"🎭 {role.nombre_rol}: {permisos_count} permisos")
        
        # Mostrar algunos permisos como ejemplo
        if permisos_count > 0:
            permisos_nombres = [pr.permiso.nombre_permiso for pr in role.permisos_rol]
            for perm in permisos_nombres[:3]:
                print(f"   ✅ {perm}")
            if permisos_count > 3:
                print(f"   ... y {permisos_count - 3} más")
        else:
            print("   ⚠️  Sin permisos")

def verificar_permisos_criticos():
    """Verifica que los permisos críticos estén asignados"""
    print("\n🔍 VERIFICACIÓN DE PERMISOS CRÍTICOS")
    print("=" * 60)
    
    permisos_criticos = [
        'admin_access',
        'gestionar_usuarios',
        'gestionar_roles',
        'gestionar_laboratorios',
        'ver_dashboard',
        'crear_solicitud'
    ]
    
    for perm_name in permisos_criticos:
        permiso = Permiso.query.filter_by(nombre_permiso=perm_name).first()
        if not permiso:
            print(f"❌ Permiso crítico no existe: {perm_name}")
            continue
        
        roles_con_permiso = []
        for pr in permiso.permisos_rol:
            roles_con_permiso.append(pr.role.nombre_rol)
        
        if roles_con_permiso:
            print(f"✅ {perm_name}: {', '.join(roles_con_permiso)}")
        else:
            print(f"⚠️  {perm_name}: No asignado a ningún rol")

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        print("🚀 ACTUALIZADOR DE PERMISOS PARA ROLES EXISTENTES")
        print("=" * 60)
        
        # Mostrar estado actual
        print("\n📋 ESTADO ACTUAL:")
        mostrar_antes_y_despues()
        
        # Confirmar cambios
        print("\n💡 CAMBIOS PROPUESTOS:")
        print("   🎯 Administrador tendrá TODOS los permisos necesarios")
        print("   🧪 Gestor de Laboratorios tendrá permisos específicos mejorados")
        print("   👤 Usuario Regular tendrá permisos básicos optimizados")
        print("   👁️  Invitado tendrá acceso mínimo de lectura")
        
        respuesta = input("\n¿Deseas aplicar estos cambios? (s/n): ")
        
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            print("\n🔄 Aplicando cambios...")
            
            try:
                # Aplicar cambios
                if actualizar_permisos_roles_existentes():
                    db.session.commit()
                    print("\n✅ CAMBIOS APLICADOS EXITOSAMENTE")
                    
                    # Mostrar estado final
                    print("\n📋 ESTADO FINAL:")
                    mostrar_antes_y_despues()
                    
                    # Verificar permisos críticos
                    verificar_permisos_criticos()
                    
                    print("\n🎉 ACTUALIZACIÓN COMPLETADA")
                    print("=" * 60)
                    print("✅ Los roles existentes han sido actualizados")
                    print("✅ Los permisos están organizados correctamente")
                    print("✅ El sistema está listo para usar")
                    
                    print("\n💡 PRÓXIMOS PASOS:")
                    print("   1. Probar el sistema: python test_permissions.py")
                    print("   2. Asignar usuarios a roles apropiados")
                    print("   3. Verificar que las funcionalidades funcionen")
                    
                else:
                    print("\n❌ Error durante la actualización")
                    
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ ERROR: {str(e)}")
                print("Los cambios han sido revertidos")
        else:
            print("\n❌ Actualización cancelada")

if __name__ == "__main__":
    main() 