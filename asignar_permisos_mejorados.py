#!/usr/bin/env python
"""
Script para asignar permisos mejorados a los roles existentes
Ejecutar: python asignar_permisos_mejorados.py
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User

def analizar_situacion_actual():
    """Analiza la situación actual de roles y permisos"""
    print("📊 ANÁLISIS DE LA SITUACIÓN ACTUAL")
    print("=" * 60)
    
    # Obtener datos actuales
    roles = Roles.query.all()
    permisos = Permiso.query.all()
    
    print(f"📋 Roles existentes: {len(roles)}")
    print(f"🔑 Permisos existentes: {len(permisos)}")
    
    # Mostrar roles y sus permisos actuales
    for role in roles:
        permisos_rol = [pr.permiso.nombre_permiso for pr in role.permisos_rol]
        print(f"\n🎭 {role.nombre_rol}: {len(permisos_rol)} permisos")
        if permisos_rol:
            for perm in permisos_rol[:3]:  # Mostrar solo los primeros 3
                print(f"   - {perm}")
            if len(permisos_rol) > 3:
                print(f"   ... y {len(permisos_rol) - 3} más")
        else:
            print("   ⚠️  Sin permisos asignados")
    
    # Identificar permisos no asignados
    permisos_asignados = set()
    for role in roles:
        for pr in role.permisos_rol:
            permisos_asignados.add(pr.permiso.nombre_permiso)
    
    permisos_no_asignados = [p.nombre_permiso for p in permisos if p.nombre_permiso not in permisos_asignados]
    
    if permisos_no_asignados:
        print(f"\n⚠️  PERMISOS NO ASIGNADOS A NINGÚN ROL ({len(permisos_no_asignados)}):")
        for perm in permisos_no_asignados:
            print(f"   - {perm}")

def obtener_permisos_por_controlador():
    """Obtiene los permisos agrupados por funcionalidad"""
    return {
        # Administración general
        'admin_general': [
            'admin_access',
            'acceso_total',
            'ver_dashboard'
        ],
        
        # Gestión de usuarios
        'usuarios': [
            'gestionar_usuarios',
            'crear_usuario',
            'editar_usuario',
            'eliminar_usuario'
        ],
        
        # Gestión de roles y permisos
        'roles_permisos': [
            'gestionar_roles',
            'crear_rol',
            'editar_rol',
            'eliminar_rol',
            'gestionar_permisos',
            'crear_permiso',
            'editar_permiso',
            'eliminar_permiso',
            'asignar_permisos'
        ],
        
        # Gestión de laboratorios
        'laboratorios': [
            'gestionar_laboratorios',
            'crear_laboratorio',
            'editar_laboratorio',
            'eliminar_laboratorio'
        ],
        
        # Gestión de áreas
        'areas': [
            'gestionar_areas',
            'crear_area',
            'editar_area',
            'eliminar_area'
        ],
        
        # Gestión de instituciones
        'instituciones': [
            'gestionar_instituciones',
            'crear_institucion',
            'editar_institucion',
            'eliminar_institucion'
        ],
        
        # Gestión de solicitudes
        'solicitudes': [
            'ver_solicitudes',
            'crear_solicitud',
            'editar_solicitud',
            'eliminar_solicitud',
            'aprobar_solicitud',
            'rechazar_solicitud',
            'ver_todas_solicitudes'
        ],
        
        # Gestión de perfil
        'perfil': [
            'ver_perfil',
            'editar_perfil',
            'cambiar_password'
        ],
        
        # Reportes
        'reportes': [
            'ver_reportes',
            'generar_reportes'
        ]
    }

def configurar_permisos_mejorados():
    """Configura una asignación mejorada de permisos por rol"""
    
    permisos_por_controlador = obtener_permisos_por_controlador()
    
    # Configuración mejorada por rol
    configuracion_roles = {
        'Super Administrador': {
            'descripcion': 'Acceso completo y total al sistema',
            'permisos': ['acceso_total']  # Este rol especial tiene todos los permisos automáticamente
        },
        
        'Administrador': {
            'descripcion': 'Administrador del sistema con permisos completos de gestión',
            'permisos': (
                permisos_por_controlador['admin_general'] +
                permisos_por_controlador['usuarios'] +
                permisos_por_controlador['roles_permisos'] +
                permisos_por_controlador['laboratorios'] +
                permisos_por_controlador['areas'] +
                permisos_por_controlador['instituciones'] +
                permisos_por_controlador['solicitudes'] +
                permisos_por_controlador['perfil'] +
                permisos_por_controlador['reportes']
            )
        },
        
        'Gestor de Laboratorios': {
            'descripcion': 'Gestión completa de laboratorios y solicitudes relacionadas',
            'permisos': (
                ['ver_dashboard'] +
                permisos_por_controlador['laboratorios'] +
                ['gestionar_areas'] +  # Necesario para gestionar áreas de laboratorios
                permisos_por_controlador['solicitudes'] +
                permisos_por_controlador['perfil'] +
                ['ver_reportes']
            )
        },
        
        'Gestor de Usuarios': {
            'descripcion': 'Gestión de usuarios e instituciones (nuevo rol)',
            'permisos': (
                ['ver_dashboard'] +
                permisos_por_controlador['usuarios'] +
                permisos_por_controlador['instituciones'] +
                ['gestionar_areas'] +  # Para asignar áreas a usuarios
                permisos_por_controlador['perfil'] +
                ['ver_reportes']
            )
        },
        
        'Coordinador Académico': {
            'descripcion': 'Gestión de áreas, instituciones y supervisión de solicitudes (nuevo rol)',
            'permisos': (
                ['ver_dashboard'] +
                permisos_por_controlador['areas'] +
                permisos_por_controlador['instituciones'] +
                ['ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud'] +
                permisos_por_controlador['perfil'] +
                ['ver_reportes']
            )
        },
        
        'Usuario Regular': {
            'descripcion': 'Usuario estándar con permisos básicos de uso',
            'permisos': (
                ['ver_dashboard'] +
                ['crear_solicitud', 'editar_solicitud', 'ver_solicitudes'] +
                permisos_por_controlador['perfil']
            )
        },
        
        'Usuario Invitado': {
            'descripcion': 'Acceso básico de solo lectura',
            'permisos': [
                'ver_dashboard',
                'ver_perfil'
            ]
        }
    }
    
    return configuracion_roles

def aplicar_permisos_mejorados():
    """Aplica la configuración mejorada de permisos"""
    print("\n🔄 APLICANDO CONFIGURACIÓN MEJORADA DE PERMISOS")
    print("=" * 60)
    
    configuracion_roles = configurar_permisos_mejorados()
    
    for nombre_rol, config in configuracion_roles.items():
        print(f"\n🎭 Configurando rol: {nombre_rol}")
        
        # Buscar o crear el rol
        role = Roles.query.filter_by(nombre_rol=nombre_rol).first()
        if not role:
            if nombre_rol in ['Gestor de Usuarios', 'Coordinador Académico']:
                print(f"   ➕ Creando nuevo rol: {nombre_rol}")
                role = Roles(
                    nombre_rol=nombre_rol,
                    descripcion=config['descripcion']
                )
                db.session.add(role)
                db.session.flush()  # Para obtener el ID
            else:
                print(f"   ⚠️  Rol no encontrado: {nombre_rol}")
                continue
        else:
            # Actualizar descripción si es necesario
            if role.descripcion != config['descripcion']:
                role.descripcion = config['descripcion']
                print(f"   📝 Descripción actualizada")
        
        # Limpiar permisos existentes
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
        
        print(f"   ✅ Permisos asignados: {permisos_asignados}")
        
        if permisos_no_encontrados:
            print(f"   ⚠️  Permisos no encontrados: {len(permisos_no_encontrados)}")
            for perm in permisos_no_encontrados:
                print(f"      - {perm}")
    
    try:
        db.session.commit()
        print("\n✅ CONFIGURACIÓN APLICADA EXITOSAMENTE")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ ERROR AL APLICAR CONFIGURACIÓN: {str(e)}")

def mostrar_resumen_final():
    """Muestra el resumen final de la configuración"""
    print("\n📋 RESUMEN FINAL DE LA CONFIGURACIÓN")
    print("=" * 60)
    
    roles = Roles.query.all()
    
    for role in roles:
        permisos_rol = [pr.permiso.nombre_permiso for pr in role.permisos_rol]
        print(f"\n🎭 {role.nombre_rol}")
        print(f"   📝 {role.descripcion}")
        print(f"   🔑 Permisos: {len(permisos_rol)}")
        
        # Agrupar permisos por categoría
        categorias = {
            'Administración': [p for p in permisos_rol if 'admin' in p.lower() or p == 'acceso_total'],
            'Usuarios': [p for p in permisos_rol if 'usuario' in p.lower()],
            'Roles/Permisos': [p for p in permisos_rol if 'rol' in p.lower() or 'permiso' in p.lower()],
            'Laboratorios': [p for p in permisos_rol if 'laboratorio' in p.lower()],
            'Áreas': [p for p in permisos_rol if 'area' in p.lower()],
            'Instituciones': [p for p in permisos_rol if 'institucion' in p.lower()],
            'Solicitudes': [p for p in permisos_rol if 'solicitud' in p.lower()],
            'Perfil': [p for p in permisos_rol if 'perfil' in p.lower() or 'password' in p.lower()],
            'Reportes': [p for p in permisos_rol if 'reporte' in p.lower()],
            'Dashboard': [p for p in permisos_rol if 'dashboard' in p.lower()]
        }
        
        for categoria, permisos in categorias.items():
            if permisos:
                print(f"      {categoria}: {len(permisos)} permisos")

def main():
    """Función principal"""
    app = create_app()
    
    with app.app_context():
        print("🚀 CONFIGURADOR DE PERMISOS MEJORADOS")
        print("=" * 60)
        
        # Paso 1: Analizar situación actual
        analizar_situacion_actual()
        
        # Paso 2: Mostrar propuesta
        print("\n💡 PROPUESTA DE MEJORA")
        print("=" * 60)
        print("✨ Se creará una configuración mejorada que incluye:")
        print("   🎯 Roles más específicos y organizados")
        print("   🔐 Permisos asignados según funcionalidad real")
        print("   📚 Nuevos roles especializados")
        print("   ⚡ Mejor distribución de responsabilidades")
        
        # Confirmar aplicación
        respuesta = input("\n¿Deseas aplicar la configuración mejorada? (s/n): ")
        if respuesta.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            # Paso 3: Aplicar configuración
            aplicar_permisos_mejorados()
            
            # Paso 4: Mostrar resumen final
            mostrar_resumen_final()
            
            print("\n🎉 CONFIGURACIÓN COMPLETADA")
            print("=" * 60)
            print("✅ Los roles han sido configurados con permisos mejorados")
            print("✅ Se han creado nuevos roles especializados")
            print("✅ Los permisos están organizados por funcionalidad")
            print("\n💡 PRÓXIMOS PASOS:")
            print("   1. Asignar usuarios a los roles apropiados")
            print("   2. Probar el sistema con diferentes usuarios")
            print("   3. Ejecutar: python test_permissions.py")
        else:
            print("\n❌ Configuración cancelada")

if __name__ == "__main__":
    main() 