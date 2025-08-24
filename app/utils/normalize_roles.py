"""
Script de normalización de roles:
- Crea/actualiza los roles estándar usando setup_permissions
- Reasigna usuarios de roles antiguos a los roles nuevos equivalentes
- Elimina roles obsoletos sin usuarios

Ejecutar desde la raíz del proyecto:
  python -m app.utils.normalize_roles
"""

from app import db, create_app
from app.models.roles import Roles
from app.models.user import User
import argparse
import traceback
from sqlalchemy import text


# Mapeo de roles actuales en BD -> roles destino estándar
# Según indicación del usuario: aplicar SOLO el segundo punto
# (mantener "Usuario" como "Usuario Regular").
ROLE_MAPPING = {
    'Usuario': 'Usuario Regular',
}

# Lista final de roles que deben existir
TARGET_ROLES = [
    'Super Administrador',
    'Administrador',
    'Admin Institucional',
    'Gestor de Laboratorios',
    'Encargado Técnico',
    'Admin de Laboratorio',
    'Usuario Regular',
    'Estudiante',
    'Investigador',
    'Administrativo',
    'Empresa',
    'Colaborador',
    'Invitado',
]


def ensure_roles_and_permissions():
    """Crea permisos y roles estándar si no existen, y asigna permisos base."""
    from app.utils.setup_permissions import init_basic_permissions, init_basic_roles
    init_basic_permissions()
    init_basic_roles()


def normalize_roles(apply_changes: bool = False):
    ensure_roles_and_permissions()

    # Verificar conectividad a BD
    try:
        db.session.execute(text('SELECT 1'))
    except Exception as e:
        print('❌ Error conectando a la base de datos. Revisa variables de entorno y credenciales (DB_HOST/USER/PASSWORD/NAME/PORT).')
        traceback.print_exc()
        return

    # Construir índice por nombre
    all_roles = {r.nombre_rol: r for r in Roles.query.all()}

    # Asegurar que todos los roles objetivo existen
    for name in TARGET_ROLES:
        if name not in all_roles:
            r = Roles(nombre_rol=name, descripcion=f'Rol {name}')
            db.session.add(r)
            db.session.flush()
            all_roles[name] = r

    # Reasignar usuarios de roles mapeados a roles destino (solo preview si apply_changes=False)
    moved_counts = []
    for old_name, new_name in ROLE_MAPPING.items():
        old_role = all_roles.get(old_name)
        new_role = all_roles.get(new_name)
        if not old_role or not new_role:
            continue
        users = User.query.filter_by(id_rol=old_role.id_rol).all()
        if apply_changes:
            for u in users:
                u.id_rol = new_role.id_rol
        if users:
            moved_counts.append((old_name, new_name, len(users), old_role.id_rol, new_role.id_rol))

    # No eliminar roles (solicitado)
    to_delete = []

    if apply_changes:
        db.session.commit()

    # Reporte
    if not moved_counts:
        print('No se encontraron usuarios en roles a normalizar.')
    else:
        print(('Aplicación' if apply_changes else 'Vista previa') + ' de normalización de roles:')
        for old_name, new_name, n, old_id, new_id in moved_counts:
            print(f' - {n} usuario(s): {old_name} (id={old_id}) -> {new_name} (id={new_id})')
    if apply_changes:
        print('Cambios guardados.')


def main():
    parser = argparse.ArgumentParser(description='Normalizar roles de usuarios')
    parser.add_argument('--apply', action='store_true', help='Aplicar cambios (por defecto solo vista previa)')
    args = parser.parse_args()

    try:
        app = create_app()
    except Exception as e:
        print('❌ Error creando la app Flask. ¿Variables de entorno faltantes?')
        traceback.print_exc()
        return

    try:
        with app.app_context():
            normalize_roles(apply_changes=args.apply)
    except Exception:
        print('❌ Error ejecutando la normalización:')
        traceback.print_exc()


if __name__ == '__main__':
    main()


