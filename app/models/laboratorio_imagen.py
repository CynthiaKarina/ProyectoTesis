from app import db
from datetime import datetime

class LaboratorioImagen(db.Model):
    __tablename__ = 'laboratorio_imagen'

    id_imagen = db.Column(db.BigInteger, primary_key=True)
    id_laboratorio = db.Column(db.BigInteger, db.ForeignKey('laboratorio.id_laboratorio', ondelete='CASCADE'))
    imagen_url = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)
    es_principal = db.Column(db.Boolean, default=False)

    # Relación con Laboratorio
    laboratorio = db.relationship('Laboratorio', backref=db.backref('imagenes', lazy=True, cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<LaboratorioImagen {self.id_imagen}>'

    def to_dict(self):
        return {
            'id_imagen': self.id_imagen,
            'id_laboratorio': self.id_laboratorio,
            'imagen_url': self.imagen_url,
            'fecha_subida': self.fecha_subida.isoformat() if self.fecha_subida else None,
            'es_principal': self.es_principal
        } 