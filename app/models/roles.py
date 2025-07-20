from app import db
from sqlalchemy import BigInteger

class Roles(db.Model):
    __tablename__ = 'roles'
    
    id_rol = db.Column(db.BigInteger, primary_key=True)
    nombre_rol = db.Column(db.String(35), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    
    # Relación inversa con Usuario
    usuarios = db.relationship('User', back_populates='roles', lazy=True)
    permisos_rol = db.relationship('PermisoRol', back_populates='rol', lazy=True)
    
    def __repr__(self):
        return f'<Roles {self.nombre_rol}>'
    
    def to_dict(self):
        return {
            'id_rol': self.id_rol,
            'nombre_rol': self.nombre_rol
        }

class Permiso(db.Model):
    __tablename__ = 'permisos'
    id_permiso = db.Column(db.BigInteger, primary_key=True)
    nombre_permiso = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    modelo = db.Column(db.String(50), nullable=False)
    leer = db.Column(db.Boolean, default=False)
    actualizar = db.Column(db.Boolean, default=False)
    crear = db.Column(db.Boolean, default=False)
    borrar = db.Column(db.Boolean, default=False)
    permisos_rol = db.relationship('PermisoRol', back_populates='permiso', lazy=True)

class PermisoRol(db.Model):
    __tablename__ = 'permisos_rol'
    id_permiso_rol = db.Column(db.BigInteger, primary_key=True)
    id_permiso = db.Column(db.BigInteger, db.ForeignKey('permisos.id_permiso'))
    id_rol = db.Column(db.BigInteger, db.ForeignKey('roles.id_rol'))
    rol = db.relationship('Roles', back_populates='permisos_rol')
    permiso = db.relationship('Permiso', back_populates='permisos_rol')

