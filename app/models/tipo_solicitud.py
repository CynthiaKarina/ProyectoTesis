from app import db

class Tipo_Solicitud(db.Model):
    __tablename__ = 'tipo_solicitud'

    id_tipo_solicitud = db.Column(db.BigInteger, primary_key=True)
    nombre_tipo_solicitud = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.Text)
    require_aprobacion = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return f'<TipoSolicitud {self.nombre_tipo_solicitud}>'

    def to_dict(self):
        return {
            'id_tipo_solicitud': self.id_tipo_solicitud,
            'nombre_tipo_solicitud': self.nombre_tipo_solicitud,
            'descripcion': self.descripcion,
            'require_aprobacion': self.require_aprobacion
        }
    
    @property
    def total_solicitudes(self):
        """Retorna el número total de solicitudes de este tipo"""
        return len(self.solicitudes) if hasattr(self, 'solicitudes') else 0
    
    @classmethod
    def get_all_active(cls):
        """Retorna todos los tipos de solicitud activos"""
        return cls.query.all()
    
    @classmethod
    def get_by_id(cls, tipo_id):
        """Obtiene un tipo de solicitud por su ID"""
        return cls.query.get(tipo_id) 