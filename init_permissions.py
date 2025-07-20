from app import create_app
from app.utils.setup_permissions import setup_permissions_system, assign_super_admin_role

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        setup_permissions_system()
        
        # Preguntar si quiere asignar super admin
        print("\n" + "="*50)
        username = input("¿Quieres asignar el rol de Super Admin a un usuario? (nombre de usuario o Enter para omitir): ")
        if username.strip():
            assign_super_admin_role(username.strip())
        else:
            print("💡 Puedes asignar el rol de Super Admin más tarde ejecutando:")
            print("   python -c \"from app import create_app; from app.utils.setup_permissions import assign_super_admin_role; app = create_app(); app.app_context().push(); assign_super_admin_role('nombre_usuario')\"") 