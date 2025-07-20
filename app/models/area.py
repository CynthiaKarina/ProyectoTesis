from datetime import datetime
from app import db

class Area(db.Model):
    __tablename__ = 'area'
    
    id_area = db.Column(db.Integer, primary_key=True)
    nombre_area = db.Column(db.String(100), nullable=False)
    creado_por = db.Column(db.String(100))
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    modificado_por = db.Column(db.String(100))
    
    # Relación inversa con Usuario
    usuarios = db.relationship('User', back_populates='area', lazy=True)
        
    def __repr__(self):
        return f'<Area {self.nombre_area}>'
    
    def to_dict(self):
        return {
            'id_area': self.id_area,
            'nombre_area': self.nombre_area,
            'creado_por': self.creado_por,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultima_modificacion': self.ultima_modificacion.isoformat() if self.ultima_modificacion else None,
            'modificado_por': self.modificado_por
        }
