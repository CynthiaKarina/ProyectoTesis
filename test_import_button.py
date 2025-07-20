from flask import Flask
from app import create_app
from app.models.user import User
from app.models.roles import Roles
from app.utils.permissions import has_permission

def test_import_functionality():
    app = create_app()
    
    with app.app_context():
        # Verificar si el usuario tiene permisos
        print("=== VERIFICACIÓN DE PERMISOS PARA IMPORTAR ===")
        
        # Obtener usuario de prueba
        usuario_test = User.query.filter_by(username='test').first()
        if not usuario_test:
            print("❌ No se encontró usuario 'test'")
            return
        
        print(f"✅ Usuario encontrado: {usuario_test.username} (ID: {usuario_test.id_usuario})")
        
        # Verificar rol del usuario
        if usuario_test.id_rol:
            rol = Roles.query.get(usuario_test.id_rol)
            print(f"✅ Rol del usuario: {rol.nombre_rol if rol else 'Sin rol'}")
        else:
            print("❌ Usuario sin rol asignado")
        
        # Verificar permiso específico para crear usuario (necesario para importar)
        print("\n=== VERIFICACIÓN DE PERMISOS ===")
        try:
            # Simular contexto de sesión
            from flask import session
            with app.test_request_context():
                session['user_id'] = usuario_test.id_usuario
                
                # Importar la función de verificación
                from app.utils.permissions import has_permission
                
                permisos_necesarios = ['crear_usuario', 'gestionar_usuarios']
                for permiso in permisos_necesarios:
                    tiene_permiso = has_permission(permiso)
                    print(f"{'✅' if tiene_permiso else '❌'} Permiso '{permiso}': {tiene_permiso}")
        
        except Exception as e:
            print(f"❌ Error verificando permisos: {e}")
        
        print("\n=== VERIFICACIÓN DE RUTAS ===")
        # Verificar que las rutas estén registradas
        from app.controllers.admin_users_controller import admin_users_bp
        
        rutas_importar = [
            '/admin/usuarios/importar',
            '/admin/usuarios/plantilla',
            '/admin/usuarios/exportar'
        ]
        
        for ruta in rutas_importar:
            encontrada = False
            for rule in app.url_map.iter_rules():
                if rule.rule == ruta:
                    encontrada = True
                    print(f"✅ Ruta '{ruta}' registrada - Métodos: {list(rule.methods)}")
                    break
            
            if not encontrada:
                print(f"❌ Ruta '{ruta}' NO encontrada")

if __name__ == "__main__":
    test_import_functionality() 