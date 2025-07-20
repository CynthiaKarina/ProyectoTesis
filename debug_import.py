#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models.user import User
from app.models.roles import Roles

def debug_import_issue():
    app = create_app()
    
    with app.app_context():
        print("=== DEBUG BOTÓN IMPORTAR ===")
        
        # Buscar el usuario test
        usuario = User.query.filter_by(username='test').first()
        if not usuario:
            print("❌ Usuario 'test' no encontrado")
            # Buscar cualquier usuario activo
            usuario = User.query.filter_by(activo=True).first()
            if usuario:
                print(f"✅ Usando usuario alternativo: {usuario.username}")
            else:
                print("❌ No hay usuarios activos")
                return
        else:
            print(f"✅ Usuario encontrado: {usuario.username}")
        
        # Verificar rol
        if usuario.id_rol:
            rol = Roles.query.get(usuario.id_rol)
            print(f"✅ Rol: {rol.nombre_rol if rol else 'Sin rol'}")
            
            # Verificar permisos del rol
            if rol and hasattr(rol, 'permisos'):
                permisos = [p.nombre_permiso for p in rol.permisos]
                print(f"✅ Permisos del rol: {permisos}")
                
                # Verificar permisos específicos
                crear_usuario = 'crear_usuario' in permisos
                gestionar_usuarios = 'gestionar_usuarios' in permisos
                
                print(f"{'✅' if crear_usuario else '❌'} Permiso 'crear_usuario': {crear_usuario}")
                print(f"{'✅' if gestionar_usuarios else '❌'} Permiso 'gestionar_usuarios': {gestionar_usuarios}")
                
            else:
                print("❌ El rol no tiene permisos asignados")
        else:
            print("❌ Usuario sin rol")
        
        # Verificar rutas de importación
        print("\n=== VERIFICAR RUTAS ===")
        rutas_buscar = [
            '/admin/usuarios/importar',
            '/admin/usuarios/exportar', 
            '/admin/usuarios/plantilla'
        ]
        
        for ruta in rutas_buscar:
            encontrada = False
            for rule in app.url_map.iter_rules():
                if rule.rule == ruta:
                    print(f"✅ Ruta '{ruta}' encontrada")
                    encontrada = True
                    break
            
            if not encontrada:
                print(f"❌ Ruta '{ruta}' NO encontrada")
        
        print("\n=== VERIFICAR BLUEPRINT ===")
        # Verificar si el blueprint está registrado
        found_bp = False
        for bp_name, bp in app.blueprints.items():
            if bp_name == 'admin_users':
                print(f"✅ Blueprint 'admin_users' encontrado")
                found_bp = True
                break
        
        if not found_bp:
            print("❌ Blueprint 'admin_users' NO encontrado")

if __name__ == "__main__":
    debug_import_issue() 