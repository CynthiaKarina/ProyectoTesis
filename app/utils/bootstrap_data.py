from app import db
import os


def _get_or_create(model, defaults=None, **kwargs):
    obj = model.query.filter_by(**kwargs).first()
    if obj:
        return obj, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    obj = model(**params)
    db.session.add(obj)
    return obj, True


def ensure_core_data():
    """Crea datos esenciales si no existen. Idempotente."""
    # 1) Permisos y roles base
    try:
        from app.utils.setup_permissions import init_basic_permissions, init_basic_roles
        init_basic_permissions()
        init_basic_roles()
    except Exception:
        # No romper en caso de error, continuar con otras semillas
        pass

    # 2) Tipos de solicitud
    try:
        from app.models.tipo_solicitud import Tipo_Solicitud
        seeds = [
            ('Reserva de Laboratorio', 'Uso programado de laboratorio'),
            ('Préstamo de Equipo', 'Préstamo de insumos o equipo'),
            ('Mantenimiento', 'Solicitud de mantenimiento'),
        ]
        for nombre, desc in seeds:
            _get_or_create(Tipo_Solicitud, defaults={'descripcion': desc, 'require_aprobacion': True}, nombre_tipo_solicitud=nombre)
    except Exception:
        pass

    # 3) Tipos de laboratorio
    try:
        from app.models.tipo_laboratorio import Tipo_Laboratorio
        seeds = [
            ('Química', 'Laboratorio de Química'),
            ('Biología', 'Laboratorio de Biología'),
            ('Computación', 'Laboratorio de Cómputo'),
        ]
        for nombre, desc in seeds:
            _get_or_create(Tipo_Laboratorio, defaults={'descripcion': desc}, nombre_tipo_laboratorio=nombre)
    except Exception:
        pass

    # 3.1) Áreas frecuentes
    try:
        from app.models.area import Area
        area_seeds = [
            'Ingeniería', 'Ciencias de la Salud', 'Biotecnología',
            'Física', 'Química', 'Biología', 'Computación', 'Materiales'
        ]
        for nombre in area_seeds:
            _get_or_create(Area, defaults={'creado_por': 'Sistema', 'modificado_por': 'Sistema'}, nombre_area=nombre)
    except Exception:
        pass

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        # No propagar el error; se busca robustez en arranque
        pass

    # 4) Instituciones base en Tlaxcala (solo si no existen)
    try:
        from app.models.institucion import Institucion
        from app.models.tipo_institucion import Tipo_Institucion
        # Asegurar tipo "Universidad" existe
        tipo_uni, _ = _get_or_create(Tipo_Institucion, nombre_tipo_institucion='Universidad')
        tlax_insts = [
            'Universidad Politécnica de Tlaxcala',
            'Universidad Autónoma de Tlaxcala',
            'Universidad Tecnológica de Tlaxcala',
            'Instituto Tecnológico de Apizaco',
        ]
        for nombre in tlax_insts:
            _get_or_create(
                Institucion,
                defaults={
                    'estado': 'Tlaxcala',
                    'municipio': '',
                    'activo': True,
                    'id_tipo_institucion': getattr(tipo_uni, 'id_tipo_institucion', 1)
                },
                nombre_institucion=nombre
            )
        db.session.commit()
    except Exception:
        db.session.rollback()
        pass

    # 5) Usuario Super Admin (requiere variables de entorno)
    try:
        from app.models.user import User
        from app.models.roles import Roles
        from werkzeug.security import generate_password_hash

        sa_username = os.environ.get('SUPERADMIN_USERNAME')
        sa_email = os.environ.get('SUPERADMIN_EMAIL')
        sa_password = os.environ.get('SUPERADMIN_PASSWORD')
        sa_phone = os.environ.get('SUPERADMIN_PHONE', '0000000000')

        # Solo proceder si hay credenciales básicas
        if sa_username and sa_email and sa_password:
            exists = User.query.filter((User.username==sa_username) | (User.email==sa_email)).first()
            if not exists:
                role = Roles.query.filter_by(nombre_rol='Super Administrador').first()
                role_id = role.id_rol if role else None
                if not role_id:
                    # fallback: crear rol si no existiera
                    role = Roles(nombre_rol='Super Administrador', descripcion='Acceso total')
                    db.session.add(role)
                    db.session.flush()
                    role_id = role.id_rol

                hashed = generate_password_hash(sa_password)
                nuevo = User(
                    nombre='Super', apellido_paterno='Admin', apellido_materno='',
                    email=sa_email, username=sa_username, password=hashed,
                    telefono=sa_phone, id_institucion=None, matricula=None,
                    id_rol=role_id, id_area=None, activo=True
                )
                db.session.add(nuevo)
                db.session.commit()
    except Exception:
        db.session.rollback()
        pass

    # 6) Rotación mensual si aplica (archivado y borrado)
    try:
        from app.utils.reports import rotate_monthly_data_if_needed
        rotate_monthly_data_if_needed()
    except Exception:
        pass

    # 7) Proceso de inactividad (advertir/eliminar)
    try:
        from app.utils.inactivity import process_inactive_accounts
        process_inactive_accounts()
    except Exception:
        pass


