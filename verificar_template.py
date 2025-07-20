#!/usr/bin/env python
"""
Script para verificar que el template home.html funciona correctamente
"""

from app import create_app
from app.models.user import User

def verificar_template():
    """Verifica que el template home.html funciona correctamente"""
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICANDO TEMPLATE HOME.HTML")
        print("=" * 40)
        
        # Buscar usuario test
        user = User.query.filter_by(username='test').first()
        if not user:
            print("❌ Usuario 'test' no encontrado")
            return False
        
        print(f"👤 Usuario: {user.username}")
        print(f"🆔 ID Usuario: {user.id_usuario}")
        print(f"🎭 Rol ID: {user.id_rol}")
        
        # Verificar si tiene el atributo nombre en el rol
        try:
            if hasattr(user, 'id_rol') and user.id_rol:
                print(f"🔍 Tipo de id_rol: {type(user.id_rol)}")
                print(f"🔍 Valor de id_rol: {user.id_rol}")
                
                # Intentar acceder al nombre del rol
                if hasattr(user.id_rol, 'nombre'):
                    print(f"✅ Nombre del rol: {user.id_rol.nombre}")
                else:
                    print("⚠️ id_rol no tiene atributo 'nombre'")
                    
                    # Buscar el rol por ID
                    from app.models.roles import Roles
                    rol = Roles.query.get(user.id_rol)
                    if rol:
                        print(f"✅ Rol encontrado: {rol.nombre_rol}")
                    else:
                        print("❌ Rol no encontrado en base de datos")
        except Exception as e:
            print(f"❌ Error accediendo al rol: {e}")
        
        print("\n🎯 CONCLUSIÓN:")
        print("Para verificar que el template funciona:")
        print("1. Inicia el servidor: python run.py")
        print("2. Ve a: http://localhost:5000/home")
        print("3. Logueate con 'test'")
        print("4. Verifica si ves el panel de administración")
        
        return True

if __name__ == '__main__':
    verificar_template() 