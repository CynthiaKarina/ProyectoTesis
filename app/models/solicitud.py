from app import db
from datetime import datetime

# Definir la tabla intermedia aquí para evitar problemas de importación circular
solicitud_usuarios = db.Table('solicitud_usuarios',
    db.Column('id_solicitud_usuarios', db.Integer, primary_key=True),
    db.Column('id_solicitud', db.Integer, db.ForeignKey('solicitud.id_solicitud'), nullable=False),
    db.Column('id_usuario', db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
)

class Solicitud(db.Model):
    __tablename__ = 'solicitud'

    id_solicitud = db.Column(db.Integer, primary_key=True)
    id_institucion = db.Column(db.Integer, db.ForeignKey('institucion.id_institucion'), nullable=False)
    id_estatus = db.Column(db.Integer, nullable=False, default=1)  # 1 = Pendiente
    id_tipo_solicitud = db.Column(db.Integer, db.ForeignKey('tipo_solicitud.id_tipo_solicitud'), nullable=False)
    id_insumo = db.Column(db.Integer, nullable=True)
    id_laboratorio = db.Column(db.Integer, db.ForeignKey('laboratorio.id_laboratorio'), nullable=False)
    razon = db.Column(db.Text, nullable=False)
    fecha_solicitud = db.Column(db.Date, nullable=False)  # Solo fecha, sin hora
    prioridad = db.Column(db.String(20), default='Normal')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Campos comentados porque no existen en la base de datos actual
    # hora_inicio = db.Column(db.Time, nullable=False)
    # hora_fin = db.Column(db.Time, nullable=False)
    # num_personas = db.Column(db.Integer, nullable=False, default=1)
    # nombre_solicitante = db.Column(db.String(100), nullable=True)
    # email_solicitante = db.Column(db.String(100), nullable=True)
    # telefono_solicitante = db.Column(db.String(20), nullable=True)

    # Relaciones usando la tabla intermedia
    laboratorio = db.relationship('Laboratorio', backref='solicitudes')
    institucion = db.relationship('Institucion', backref='solicitudes')
    tipo_solicitud = db.relationship('Tipo_Solicitud', backref='solicitudes')
    
    # Relación many-to-many con usuarios a través de solicitud_usuarios
    usuarios = db.relationship('User', 
                              secondary=solicitud_usuarios,
                              backref=db.backref('solicitudes', lazy='dynamic'))

    def __repr__(self):
        return f'<Solicitud {self.id_solicitud} - {self.laboratorio.nombre_laboratorio if self.laboratorio else "Sin laboratorio"}>'
    
    @property
    def investigador_principal(self):
        """Retorna el primer usuario asociado a la solicitud"""
        return self.usuarios[0] if self.usuarios else None
    
    @property
    def nombre_completo_solicitante(self):
        """Retorna el nombre del solicitante principal"""
        investigador = self.investigador_principal
        if investigador:
            return f"{investigador.nombre} {investigador.apellido_paterno}"
        return "Sin nombre"
    
    @property
    def email_contacto(self):
        """Retorna el email de contacto del investigador principal"""
        investigador = self.investigador_principal
        if investigador:
            return investigador.email
        return None
    
    @property
    def telefono_contacto(self):
        """Retorna el teléfono de contacto del investigador principal"""
        investigador = self.investigador_principal
        if investigador and hasattr(investigador, 'telefono'):
            return investigador.telefono
        return None
    
    @property
    def duracion_horas(self):
        """Calcula la duración en horas de la solicitud (valor por defecto)"""
        # Como no tenemos hora_inicio y hora_fin, retornamos un valor por defecto
        return 2.0  # 2 horas por defecto
    
    @property
    def estado_color(self):
        """Retorna el color asociado al estado de la solicitud"""
        colores = {
            1: '#ffc107',  # Pendiente - Amarillo
            2: '#17a2b8',  # En Revisión - Azul claro
            3: '#28a745',  # Aprobada - Verde
            4: '#dc3545',  # Rechazada - Rojo
            5: '#6c757d',  # Cancelada - Gris
            6: '#007bff'   # Completada - Azul
        }
        return colores.get(self.id_estatus, '#6c757d')
    
    @property
    def estado_nombre(self):
        """Retorna el nombre del estado de la solicitud"""
        estados = {
            1: 'Pendiente',
            2: 'En Revisión',
            3: 'Aprobada',
            4: 'Rechazada',
            5: 'Cancelada',
            6: 'Completada'
        }
        return estados.get(self.id_estatus, 'Desconocido')
    
    def puede_cancelar(self):
        """Verifica si la solicitud puede ser cancelada"""
        return self.id_estatus in [1, 2]  # Solo pendientes o en revisión
    
    def puede_modificar(self):
        """Verifica si la solicitud puede ser modificada"""
        return self.id_estatus == 1  # Solo pendientes
