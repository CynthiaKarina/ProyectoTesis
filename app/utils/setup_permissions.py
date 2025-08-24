#!/usr/bin/env python
"""
Script para inicializar el sistema de permisos
Ejecutar desde la raíz del proyecto: python -m app.utils.setup_permissions
"""

from app import db
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.user import User

def init_basic_permissions():
    """Inicializa los permisos básicos del sistema"""
    
    # Permisos básicos del sistema
    basic_permissions = [
        # Permisos de administración general
        {'nombre': 'admin_access', 'descripcion': 'Acceso al panel de administración', 'modelo': 'admin', 'leer': True, 'actualizar': True, 'crear': True, 'borrar': True},
        
        # Permisos de gestión de usuarios
        {'nombre': 'gestionar_usuarios', 'descripcion': 'Ver lista de usuarios', 'modelo': 'usuario', 'leer': True},
        {'nombre': 'crear_usuario', 'descripcion': 'Crear nuevos usuarios', 'modelo': 'usuario', 'crear': True},
        {'nombre': 'editar_usuario', 'descripcion': 'Editar información de usuarios', 'modelo': 'usuario', 'actualizar': True},
        {'nombre': 'eliminar_usuario', 'descripcion': 'Eliminar usuarios del sistema', 'modelo': 'usuario', 'borrar': True},
        
        # Permisos de gestión de roles
        {'nombre': 'gestionar_roles', 'descripcion': 'Ver lista de roles', 'modelo': 'rol', 'leer': True},
        {'nombre': 'crear_rol', 'descripcion': 'Crear nuevos roles', 'modelo': 'rol', 'crear': True},
        {'nombre': 'editar_rol', 'descripcion': 'Editar información de roles', 'modelo': 'rol', 'actualizar': True},
        {'nombre': 'eliminar_rol', 'descripcion': 'Eliminar roles del sistema', 'modelo': 'rol', 'borrar': True},
        
        # Permisos de gestión de permisos
        {'nombre': 'gestionar_permisos', 'descripcion': 'Ver lista de permisos', 'modelo': 'permiso', 'leer': True},
        {'nombre': 'crear_permiso', 'descripcion': 'Crear nuevos permisos', 'modelo': 'permiso', 'crear': True},
        {'nombre': 'editar_permiso', 'descripcion': 'Editar información de permisos', 'modelo': 'permiso', 'actualizar': True},
        {'nombre': 'eliminar_permiso', 'descripcion': 'Eliminar permisos del sistema', 'modelo': 'permiso', 'borrar': True},
        {'nombre': 'asignar_permisos', 'descripcion': 'Asignar permisos a roles', 'modelo': 'permiso', 'actualizar': True},
        
        # Permisos de gestión de laboratorios
        {'nombre': 'gestionar_laboratorios', 'descripcion': 'Ver lista de laboratorios'},
        {'nombre': 'crear_laboratorio', 'descripcion': 'Crear nuevos laboratorios'},
        {'nombre': 'editar_laboratorio', 'descripcion': 'Editar información de laboratorios'},
        {'nombre': 'eliminar_laboratorio', 'descripcion': 'Eliminar laboratorios del sistema'},
        
        # Permisos de gestión de áreas
        {'nombre': 'gestionar_areas', 'descripcion': 'Ver lista de áreas'},
        {'nombre': 'crear_area', 'descripcion': 'Crear nuevas áreas'},
        {'nombre': 'editar_area', 'descripcion': 'Editar información de áreas'},
        {'nombre': 'eliminar_area', 'descripcion': 'Eliminar áreas del sistema'},
        
        # Permisos de gestión de instituciones
        {'nombre': 'gestionar_instituciones', 'descripcion': 'Ver lista de instituciones'},
        {'nombre': 'crear_institucion', 'descripcion': 'Crear nuevas instituciones'},
        {'nombre': 'editar_institucion', 'descripcion': 'Editar información de instituciones'},
        {'nombre': 'eliminar_institucion', 'descripcion': 'Eliminar instituciones del sistema'},
        
        # Permisos de gestión de solicitudes
        {'nombre': 'ver_solicitudes', 'descripcion': 'Ver lista de solicitudes'},
        {'nombre': 'crear_solicitud', 'descripcion': 'Crear nuevas solicitudes'},
        {'nombre': 'editar_solicitud', 'descripcion': 'Editar información de solicitudes'},
        {'nombre': 'eliminar_solicitud', 'descripcion': 'Eliminar solicitudes'},
        {'nombre': 'aprobar_solicitud', 'descripcion': 'Aprobar solicitudes de laboratorio'},
        {'nombre': 'rechazar_solicitud', 'descripcion': 'Rechazar solicitudes de laboratorio'},
        {'nombre': 'ver_todas_solicitudes', 'descripcion': 'Ver solicitudes de todos los usuarios'},
        
        # Permisos de perfil
        {'nombre': 'ver_perfil', 'descripcion': 'Ver información del perfil propio'},
        {'nombre': 'editar_perfil', 'descripcion': 'Editar información del perfil propio'},
        {'nombre': 'cambiar_password', 'descripcion': 'Cambiar contraseña propia'},
        
        # Permisos de reportes
        {'nombre': 'ver_reportes', 'descripcion': 'Ver reportes del sistema', 'modelo': 'reporte', 'leer': True},
        {'nombre': 'generar_reportes', 'descripcion': 'Generar reportes personalizados', 'modelo': 'reporte', 'crear': True},

        # Permisos de proyectos
        {'nombre': 'gestionar_proyectos', 'descripcion': 'Ver y administrar proyectos', 'modelo': 'proyecto', 'leer': True, 'actualizar': True},
        {'nombre': 'crear_proyecto', 'descripcion': 'Crear nuevos proyectos', 'modelo': 'proyecto', 'crear': True},
        {'nombre': 'editar_proyecto', 'descripcion': 'Editar proyectos', 'modelo': 'proyecto', 'actualizar': True},
        {'nombre': 'eliminar_proyecto', 'descripcion': 'Eliminar proyectos', 'modelo': 'proyecto', 'borrar': True},
        
        # Permisos especiales
        {'nombre': 'ver_dashboard', 'descripcion': 'Acceso al dashboard principal'},
        {'nombre': 'acceso_total', 'descripcion': 'Acceso completo al sistema (super admin)'},
    ]
    
    print("Creando permisos básicos...")
    
    for perm_data in basic_permissions:
        # Verificar si el permiso ya existe
        existing_permission = Permiso.query.filter_by(nombre_permiso=perm_data['nombre']).first()
        if not existing_permission:
            new_permission = Permiso(
                nombre_permiso=perm_data['nombre'],
                descripcion=perm_data['descripcion'],
                modelo=perm_data.get('modelo', 'general'),
                leer=perm_data.get('leer', True),
                actualizar=perm_data.get('actualizar', True),
                crear=perm_data.get('crear', True),
                borrar=perm_data.get('borrar', True)
            )
            db.session.add(new_permission)
            print(f"✓ Creado permiso: {perm_data['nombre']}")
        else:
            print(f"- Permiso ya existe: {perm_data['nombre']}")
    
    try:
        db.session.commit()
        print("✅ Permisos básicos inicializados correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear permisos: {str(e)}")

def init_basic_roles():
    """Inicializa los roles básicos del sistema"""
    
    basic_roles = [
        {
            'nombre': 'Super Administrador',
            'descripcion': 'Acceso completo al sistema',
            'permisos': ['acceso_total']  # Este rol tendrá todos los permisos
        },
        {
            'nombre': 'Administrador',
            'descripcion': 'Administrador del sistema con permisos de gestión',
            'permisos': [
                'admin_access', 'gestionar_usuarios', 'crear_usuario', 'editar_usuario',
                'gestionar_roles', 'crear_rol', 'editar_rol',
                'gestionar_permisos', 'asignar_permisos',
                'gestionar_laboratorios', 'crear_laboratorio', 'editar_laboratorio',
                'gestionar_areas', 'crear_area', 'editar_area',
                'gestionar_instituciones', 'crear_institucion', 'editar_institucion',
                'ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud',
                'ver_reportes', 'generar_reportes',
                'gestionar_proyectos', 'crear_proyecto', 'editar_proyecto', 'eliminar_proyecto',
                'ver_dashboard'
            ]
        },
        {
            'nombre': 'Admin Institucional',
            'descripcion': 'Administrador a nivel de institución',
            'permisos': [
                'admin_access', 'gestionar_usuarios', 'crear_usuario', 'editar_usuario',
                'gestionar_laboratorios', 'crear_laboratorio', 'editar_laboratorio',
                'gestionar_instituciones', 'editar_institucion',
                'ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud',
                'ver_reportes',
                'gestionar_proyectos', 'crear_proyecto', 'editar_proyecto',
                'ver_dashboard'
            ]
        },
        {
            'nombre': 'Gestor de Laboratorios',
            'descripcion': 'Gestión de laboratorios y solicitudes',
            'permisos': [
                'gestionar_laboratorios', 'editar_laboratorio',
                'ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud',
                'ver_dashboard', 'ver_reportes'
            ]
        },
        {
            'nombre': 'Encargado Técnico',
            'descripcion': 'Responsable técnico de laboratorios',
            'permisos': [
                'gestionar_laboratorios', 'editar_laboratorio',
                'ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud',
                'ver_dashboard', 'ver_reportes'
            ]
        },
        {
            'nombre': 'Admin de Laboratorio',
            'descripcion': 'Administrador específico de laboratorios',
            'permisos': [
                'gestionar_laboratorios', 'editar_laboratorio',
                'ver_todas_solicitudes', 'aprobar_solicitud', 'rechazar_solicitud',
                'ver_dashboard', 'ver_reportes'
            ]
        },
        {
            'nombre': 'Usuario Regular',
            'descripcion': 'Usuario estándar del sistema',
            'permisos': [
                'ver_perfil', 'editar_perfil', 'cambiar_password',
                'crear_solicitud', 'editar_solicitud', 'ver_solicitudes',
                'ver_dashboard'
            ]
        },
        {
            'nombre': 'Estudiante',
            'descripcion': 'Usuario estudiante con permisos estándar',
            'permisos': [
                'ver_perfil', 'editar_perfil', 'cambiar_password',
                'crear_solicitud', 'editar_solicitud', 'ver_solicitudes',
                'ver_dashboard'
            ]
        },
        {
            'nombre': 'Investigador',
            'descripcion': 'Usuario investigador con gestión de solicitudes',
            'permisos': [
                'ver_perfil', 'editar_perfil', 'cambiar_password',
                'crear_solicitud', 'editar_solicitud', 'ver_solicitudes',
                'ver_reportes', 'crear_proyecto', 'ver_dashboard'
            ]
        },
        {
            'nombre': 'Administrativo',
            'descripcion': 'Personal administrativo con gestión operativa',
            'permisos': [
                'ver_solicitudes', 'editar_solicitud',
                'ver_reportes', 'ver_dashboard'
            ]
        },
        {
            'nombre': 'Empresa',
            'descripcion': 'Usuario externo (empresa) con acceso a solicitudes',
            'permisos': [
                'ver_perfil', 'ver_dashboard', 'crear_solicitud', 'ver_solicitudes'
            ]
        },
        {
            'nombre': 'Colaborador',
            'descripcion': 'Usuario colaborador externo',
            'permisos': [
                'ver_perfil', 'ver_dashboard', 'crear_solicitud', 'ver_solicitudes'
            ]
        },
        {
            'nombre': 'Invitado',
            'descripcion': 'Acceso básico de solo lectura',
            'permisos': [
                'ver_perfil', 'ver_dashboard'
            ]
        }
    ]
    
    print("Creando roles básicos...")
    
    for role_data in basic_roles:
        # Verificar si el rol ya existe
        existing_role = Roles.query.filter_by(nombre_rol=role_data['nombre']).first()
        if not existing_role:
            new_role = Roles(
                nombre_rol=role_data['nombre'],
                descripcion=role_data['descripcion']
            )
            db.session.add(new_role)
            db.session.flush()  # Para obtener el ID
            
            # Asignar permisos al rol
            for perm_name in role_data['permisos']:
                permission = Permiso.query.filter_by(nombre_permiso=perm_name).first()
                if permission:
                    perm_rol = PermisoRol(id_rol=new_role.id_rol, id_permiso=permission.id_permiso)
                    db.session.add(perm_rol)
            
            print(f"✓ Creado rol: {role_data['nombre']} con {len(role_data['permisos'])} permisos")
        else:
            print(f"- Rol ya existe: {role_data['nombre']}")
    
    try:
        db.session.commit()
        print("✅ Roles básicos inicializados correctamente")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al crear roles: {str(e)}")

def assign_super_admin_role(username):
    """Asigna el rol de Super Administrador a un usuario específico"""
    user = User.query.filter_by(username=username).first()
    if not user:
        print(f"❌ Usuario '{username}' no encontrado")
        return False
    
    super_admin_role = Roles.query.filter_by(nombre_rol='Super Administrador').first()
    if not super_admin_role:
        print("❌ Rol 'Super Administrador' no encontrado")
        return False
    
    user.id_rol = super_admin_role.id_rol
    db.session.commit()
    
    print(f"✅ Rol 'Super Administrador' asignado al usuario '{username}'")
    return True

def setup_permissions_system():
    """Configuración completa del sistema de permisos"""
    print("🚀 Inicializando sistema de permisos...")
    print("=" * 50)
    
    # Paso 1: Crear permisos básicos
    init_basic_permissions()
    print()
    
    # Paso 2: Crear roles básicos
    init_basic_roles()
    print()
    
    print("✅ Sistema de permisos inicializado correctamente")
    print("💡 Para asignar rol de Super Admin a un usuario, usa:")
    print("   assign_super_admin_role('nombre_usuario')")

if __name__ == '__main__':
    from app import create_app
    app = create_app()
    
    with app.app_context():
        setup_permissions_system()
        
        # Preguntar si quiere asignar super admin
        username = input("\n¿Quieres asignar el rol de Super Admin a un usuario? (nombre de usuario o Enter para omitir): ")
        if username.strip():
            assign_super_admin_role(username.strip()) 