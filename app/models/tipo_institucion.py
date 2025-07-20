from app import db

class Tipo_Institucion(db.Model):
    __tablename__ = 'tipo_institucion'
    
    id_tipo_institucion = db.Column(db.Integer, primary_key=True)
    nombre_tipo_institucion = db.Column(db.String(100), nullable=False)
    
    # Relación con Instituciones
    instituciones = db.relationship('Institucion', back_populates='tipo_institucion', lazy=True)
    
    def __repr__(self):
        return f'<Tipo_Institucion {self.nombre_tipo_institucion}>'
    
    def to_dict(self):
        return {
            'id_tipo_institucion': self.id_tipo_institucion,
            'nombre_tipo_institucion': self.nombre_tipo_institucion,
            'descripcion': self.descripcion
        }
