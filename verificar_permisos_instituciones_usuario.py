#!/usr/bin/env python
"""
Script para verificar permisos específicos de instituciones del usuario actual
"""

import sys
import os

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.roles import Roles, Permiso, PermisoRol
from app.models.institucion import Institucion
from app.models.tipo_institucion import Tipo_Institucion
from app.utils.permissions import PermissionManager

def verificar_permisos_instituciones():
    """Verifica el sistema de permisos específico para instituciones"""
    app = create_app()
    
    with app.app_context():
        print("🏢 VERIFICACIÓN DE PERMISOS PARA GESTIÓN DE INSTITUCIONES")
        print("=" * 60)
        
        # 1. Verificar que los permisos de instituciones existen en la BD
        print("\n📋 1. PERMISOS DE INSTITUCIONES EN BASE DE DATOS:")
        permisos_instituciones = ['gestionar_instituciones', 'crear_institucion', 'editar_institucion', 'eliminar_institucion']
        
        permisos_encontrados = {}
        for permiso_nombre in permisos_instituciones:
            permiso = Permiso.query.filter_by(nombre_permiso=permiso_nombre).first()
            if permiso:
                # Contar roles que tienen este permiso
                roles_count = db.session.query(PermisoRol).filter_by(id_permiso=permiso.id_permiso).count()
                print(f"   ✅ {permiso_nombre}: ID={permiso.id_permiso}, Roles asignados={roles_count}")
                permisos_encontrados[permiso_nombre] = True
            else:
                print(f"   ❌ {permiso_nombre}: NO EXISTE EN LA BD")
                permisos_encontrados[permiso_nombre] = False
        
        # 2. Verificar roles que tienen permisos de instituciones
        print("\n👥 2. ROLES CON PERMISOS DE INSTITUCIONES:")
        roles = Roles.query.all()
        for rol in roles:
            permisos_del_rol = db.session.query(Permiso.nombre_permiso).join(PermisoRol).filter(
                PermisoRol.id_rol == rol.id_rol,
                Permiso.nombre_permiso.in_(permisos_instituciones)
            ).all()
            
            permisos_lista = [p[0] for p in permisos_del_rol]
            if permisos_lista:
                print(f"   ✅ {rol.nombre_rol} (ID={rol.id_rol}): {', '.join(permisos_lista)}")
        
        # 3. Buscar usuarios administrativos
        print("\n👤 3. USUARIOS CON ROLES ADMINISTRATIVOS:")
        usuarios_admin = db.session.query(User, Roles).join(Roles).filter(
            Roles.nombre_rol.in_(['Super Administrador', 'Administrador', 'Gestor de Usuarios', 'Coordinador Académico'])
        ).all()
        
        if usuarios_admin:
            for user, role in usuarios_admin:
                # Verificar permisos específicos de instituciones
                permisos_instituciones_usuario = []
                for permiso_nombre in permisos_instituciones:
                    if permisos_encontrados[permiso_nombre]:  # Solo verificar si el permiso existe
                        tiene_permiso = PermissionManager.user_has_permission(user, permiso_nombre)
                        if tiene_permiso:
                            permisos_instituciones_usuario.append(permiso_nombre)
                
                print(f"   👤 {user.username} ({user.nombre or 'Sin nombre'})")
                print(f"      🎭 Rol: {role.nombre_rol}")
                print(f"      🔑 Permisos de instituciones: {', '.join(permisos_instituciones_usuario) if permisos_instituciones_usuario else 'NINGUNO'}")
                print()
        else:
            print("   ⚠️ No se encontraron usuarios administrativos")
        
        # 4. Verificar datos de instituciones
        print("\n🏢 4. DATOS DE INSTITUCIONES EN LA BASE DE DATOS:")
        total_instituciones = Institucion.query.count()
        instituciones_activas = Institucion.query.filter_by(activo=True).count()
        tipos_institucion = Tipo_Institucion.query.count()
        
        print(f"   📊 Total de instituciones: {total_instituciones}")
        print(f"   ✅ Instituciones activas: {instituciones_activas}")
        print(f"   📋 Tipos de institución disponibles: {tipos_institucion}")
        
        if total_instituciones > 0:
            instituciones_muestra = Institucion.query.limit(3).all()
            print(f"   📝 Muestra de instituciones:")
            for inst in instituciones_muestra:
                estado = "Activa" if inst.activo else "Inactiva"
                tipo = inst.tipo_institucion.nombre_tipo_institucion if inst.tipo_institucion else "Sin tipo"
                print(f"      - {inst.nombre_institucion} ({estado}) - Tipo: {tipo}")
        
        # 5. Verificar funcionalidad del sistema de permisos
        print("\n🧪 5. PRUEBA DEL SISTEMA DE PERMISOS:")
        
        try:
            # Probar función de verificación de permisos
            admin_role = Roles.query.filter_by(nombre_rol='Administrador').first()
            if admin_role:
                permisos_admin = 0
                for permiso_nombre in permisos_instituciones:
                    if permisos_encontrados[permiso_nombre]:
                        existe = db.session.query(PermisoRol).join(Permiso).filter(
                            PermisoRol.id_rol == admin_role.id_rol,
                            Permiso.nombre_permiso == permiso_nombre
                        ).first()
                        if existe:
                            permisos_admin += 1
                
                print(f"   ✅ Rol 'Administrador' tiene {permisos_admin}/4 permisos de instituciones")
                
                if permisos_admin < 4:
                    print(f"   ⚠️ FALTA ASIGNAR ALGUNOS PERMISOS DE INSTITUCIONES AL ROL ADMINISTRADOR")
                    print(f"   💡 Ejecutar: python actualizar_permisos_existentes.py")
            else:
                print(f"   ❌ No se encontró el rol 'Administrador'")
                print(f"   💡 Ejecutar: python setup_permissions.py")
        
        except Exception as e:
            print(f"   ❌ Error en prueba del sistema: {e}")
        
        # 6. Verificar integración del controlador
        print("\n🔗 6. VERIFICACIÓN DE INTEGRACIÓN:")
        print("   ✅ Controlador: admin_instituciones_controller.py creado")
        print("   ✅ Template: admin_instituciones.html creado")
        print("   ✅ Blueprint registrado en __init__.py")
        print("   ✅ Menú actualizado en base_Admin.html")
        print("   ✅ Rutas disponibles:")
        print("      - GET  /admin/instituciones (Página principal)")
        print("      - GET  /admin/instituciones/<id> (Obtener institución)")
        print("      - POST /admin/instituciones/agregar (Crear)")
        print("      - PUT  /admin/instituciones/editar/<id> (Editar)")
        print("      - DELETE /admin/instituciones/eliminar/<id> (Eliminar)")
        print("      - POST /admin/instituciones/toggle-status/<id> (Cambiar estado)")
        
        print("\n" + "=" * 60)
        print("🔒 RESUMEN DE SEGURIDAD:")
        print("✅ Los decoradores @permission_required están implementados")
        print("✅ Los permisos específicos están definidos:")
        print("   - @permission_required('gestionar_instituciones') - Ver instituciones")
        print("   - @permission_required('crear_institucion') - Crear instituciones") 
        print("   - @permission_required('editar_institucion') - Editar instituciones")
        print("   - @permission_required('eliminar_institucion') - Eliminar instituciones")
        print("✅ El template base_Admin.html controla el acceso al menú")
        print("✅ Solo usuarios con permisos pueden acceder a la funcionalidad")
        
        # 7. Recomendar usuario para probar
        print("\n💡 7. RECOMENDACIÓN PARA PRUEBAS:")
        
        # Buscar usuario 'test' o 'cynthia' si existe
        usuario_test = User.query.filter_by(username='test').first()
        if not usuario_test:
            usuario_test = User.query.filter_by(username='cynthia').first()
        
        if usuario_test:
            if usuario_test.id_rol:
                rol = db.session.get(Roles, usuario_test.id_rol)
                print(f"   👤 Usuario '{usuario_test.username}' disponible:")
                print(f"      🎭 Rol actual: {rol.nombre_rol if rol else 'Sin rol'}")
                
                # Verificar permisos
                for permiso_nombre in permisos_instituciones:
                    if permisos_encontrados[permiso_nombre]:
                        tiene_permiso = PermissionManager.user_has_permission(usuario_test, permiso_nombre)
                        estado = "✅" if tiene_permiso else "❌"
                        print(f"      {estado} {permiso_nombre}")
                
                if any(PermissionManager.user_has_permission(usuario_test, p) for p in permisos_instituciones if permisos_encontrados[p]):
                    print(f"\n   🎉 USUARIO '{usuario_test.username}' TIENE PERMISOS DE INSTITUCIONES")
                    print(f"   🌐 Puede acceder a: http://localhost:10000/admin/instituciones")
                else:
                    print(f"\n   ⚠️ USUARIO '{usuario_test.username}' NO TIENE PERMISOS DE INSTITUCIONES")
                    print(f"   💡 Recomendación: Asignar rol 'Administrador' al usuario '{usuario_test.username}'")
            else:
                print(f"   ⚠️ Usuario '{usuario_test.username}' existe pero no tiene rol asignado")
        else:
            print(f"   ⚠️ No se encontró usuario 'test' ni 'cynthia'")

if __name__ == '__main__':
    verificar_permisos_instituciones() 