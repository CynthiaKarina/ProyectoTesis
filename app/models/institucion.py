from app import db
from datetime import datetime

class Institucion(db.Model):
    __tablename__ = 'institucion'
    
    id_institucion = db.Column(db.Integer, primary_key=True)
    nombre_institucion = db.Column(db.String(100), nullable=False)
    calle = db.Column(db.String(200))
    colonia = db.Column(db.String(200))
    municipio = db.Column(db.String(200))
    estado = db.Column(db.String(200))
    codigo_postal = db.Column(db.String(20))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    id_tipo_institucion = db.Column(db.Integer, db.ForeignKey('tipo_institucion.id_tipo_institucion'), nullable=False)
    
    # Relaciones
    usuarios = db.relationship('User', back_populates='institucion', lazy=True)
    tipo_institucion = db.relationship('Tipo_Institucion', back_populates='instituciones', lazy=True)
    
    def __repr__(self):
        return f'<Institucion {self.nombre_institucion}>'
    
    def to_dict(self):
        return {
            'id_institucion': self.id_institucion,
            'nombre_institucion': self.nombre_institucion,
            'calle': self.calle,
            'colonia': self.colonia,
            'municipio': self.municipio,
            'estado': self.estado,
            'codigo_postal': self.codigo_postal,
            'telefono': self.telefono,
            'email': self.email,
            'id_tipo_institucion': self.id_tipo_institucion,
            'fecha_registro': self.fecha_registro.strftime('%Y-%m-%d %H:%M:%S') if self.fecha_registro else None,
            'activo': self.activo
        }