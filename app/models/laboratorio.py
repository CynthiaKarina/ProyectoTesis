from app import db
from datetime import datetime
from app.models.tipo_laboratorio import Tipo_Laboratorio
from app.models.institucion import Institucion
from app.models.area import Area
from app.models.user import User

class Laboratorio(db.Model):
    __tablename__ = 'laboratorio'

    id_laboratorio = db.Column(db.BigInteger, primary_key=True)
    nombre_laboratorio = db.Column(db.String(100), nullable=False)
    disponibilidad = db.Column(db.String(100), default='Activo')
    descripcion = db.Column(db.Text)
    imagen_url = db.Column(db.String(255))
    
    # Nuevos campos agregados
    capacidad = db.Column(db.Integer, default=20)
    horario = db.Column(db.String(100))
    ubicacion = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    email_contacto = db.Column(db.String(100))
    superficie_m2 = db.Column(db.Numeric(8, 2))
    equipamiento = db.Column(db.Text)
    normas_uso = db.Column(db.Text)
    requiere_capacitacion = db.Column(db.Boolean, default=False)
    
    id_institucion = db.Column(db.BigInteger, db.ForeignKey('institucion.id_institucion', ondelete='SET NULL'))
    institucion = db.relationship('Institucion', backref=db.backref('laboratorios', lazy=True))
    
    id_area = db.Column(db.BigInteger, db.ForeignKey('area.id_area', ondelete='SET NULL'))
    area = db.relationship('Area', backref=db.backref('laboratorios', lazy=True))
    
    id_tipo_laboratorio = db.Column(db.BigInteger, db.ForeignKey('tipo_laboratorio.id_tipo_laboratorio', ondelete='SET NULL'))
    tipo_laboratorio = db.relationship('Tipo_Laboratorio', backref=db.backref('laboratorios', lazy=True))
    
    id_encargado = db.Column(db.BigInteger, db.ForeignKey('usuario.id_usuario', ondelete='SET NULL'))
    encargado = db.relationship('User',
                              primaryjoin="Laboratorio.id_encargado == User.id_usuario",
                              backref=db.backref('laboratorios_encargados', lazy=True))
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Laboratorio {self.nombre_laboratorio}>'

    @property
    def estado_disponibilidad(self):
        """Retorna el estado de disponibilidad con formato legible"""
        estados = {
            'Activo': 'Disponible',
            'Inactivo': 'No Disponible',
            'Mantenimiento': 'En Mantenimiento',
            'Reservado': 'Reservado'
        }
        return estados.get(self.disponibilidad, self.disponibilidad)
    
    @property
    def color_disponibilidad(self):
        """Retorna el color asociado al estado de disponibilidad"""
        colores = {
            'Activo': '#28a745',      # Verde
            'Inactivo': '#dc3545',    # Rojo
            'Mantenimiento': '#ffc107', # Amarillo
            'Reservado': '#17a2b8'    # Azul
        }
        return colores.get(self.disponibilidad, '#6c757d')
    
    @property
    def equipamiento_lista(self):
        """Retorna el equipamiento como lista"""
        if self.equipamiento:
            return [item.strip() for item in self.equipamiento.split(',') if item.strip()]
        return []
    
    @property
    def horario_formateado(self):
        """Retorna el horario formateado o un mensaje por defecto"""
        return self.horario or 'Consultar disponibilidad'
    
    @property
    def ubicacion_completa(self):
        """Retorna la ubicación completa incluyendo institución"""
        ubicacion_parts = []
        if self.ubicacion:
            ubicacion_parts.append(self.ubicacion)
        if self.institucion:
            ubicacion_parts.append(self.institucion.nombre_institucion)
        return ' - '.join(ubicacion_parts) if ubicacion_parts else 'Ubicación no especificada'
    
    def puede_solicitar(self):
        """Verifica si el laboratorio puede ser solicitado"""
        return self.disponibilidad == 'Activo'

    def to_dict(self):
        return {
            'id_laboratorio': self.id_laboratorio,
            'nombre_laboratorio': self.nombre_laboratorio,
            'disponibilidad': self.disponibilidad,
            'estado_disponibilidad': self.estado_disponibilidad,
            'color_disponibilidad': self.color_disponibilidad,
            'descripcion': self.descripcion,
            'capacidad': self.capacidad,
            'horario': self.horario_formateado,
            'ubicacion': self.ubicacion_completa,
            'telefono': self.telefono,
            'email_contacto': self.email_contacto,
            'superficie_m2': float(self.superficie_m2) if self.superficie_m2 else None,
            'equipamiento': self.equipamiento_lista,
            'normas_uso': self.normas_uso,
            'requiere_capacitacion': self.requiere_capacitacion,
            'imagen_url': self.imagen_url,
            'institucion': self.institucion.nombre_institucion if self.institucion else None,
            'area': self.area.nombre_area if self.area else None,
            'tipo_laboratorio': self.tipo_laboratorio.nombre_tipo_laboratorio if self.tipo_laboratorio else None,
            'encargado': {
                'id': self.encargado.id_usuario if self.encargado else None,
                'nombre': self.encargado.nombre if self.encargado else None,
                'imagen': self.encargado.ruta_imagen if self.encargado else None
            } if self.encargado else None,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None
        }