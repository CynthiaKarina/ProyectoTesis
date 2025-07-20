from app import db
from datetime import datetime
from app.models.institucion import Institucion
from app.models.roles import Roles
from app.models.area import Area
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128))
    nombre = db.Column(db.String(100))
    apellido_paterno = db.Column(db.String(100))  # Apellido Paterno
    apellido_materno = db.Column(db.String(100))  # Apellido Materno
    telefono = db.Column(db.String(20))
    ruta_imagen = db.Column(db.String(255))
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Claves foráneas
    id_institucion = db.Column(db.Integer, db.ForeignKey('institucion.id_institucion'), nullable=True)
    id_area = db.Column(db.Integer, db.ForeignKey('area.id_area'), nullable=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=True)
    
    # Relaciones
    institucion = db.relationship('Institucion', back_populates='usuarios', lazy=True)
    area = db.relationship('Area', back_populates='usuarios', lazy=True)
    roles = db.relationship('Roles', back_populates='usuarios', lazy=True)
    
    def __repr__(self):
        return f'<User {self.nombre}>'
    
    def get_id(self):
        return str(self.id_usuario)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return self.activo
    
    def is_anonymous(self):
        return False
    
    @property
    def has_role(self):
        """Verifica si el usuario tiene un rol asignado"""
        return hasattr(self, 'id_rol') and self.id_rol is not None
    
    @property
    def role_name(self):
        """Obtiene el nombre del rol de forma segura"""
        if not self.has_role:
            return None
        try:
            from app.models.roles import Roles
            role = Roles.query.get(self.id_rol)
            return role.nombre_rol if role else None
        except Exception:
            return None
    
    def get_imagen_url(self):
        if self.ruta_imagen:
            return self.ruta_imagen
        return 'img/default-profile.png'
    
    def actualizar_password(self, nueva_password):
        self.password = nueva_password
        self.ultima_actualizacion_password = datetime.now()
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        nombres = [self.nombre, self.apellido_paterno, self.apellido_materno]
        return ' '.join([n for n in nombres if n])
    
    @property
    def iniciales(self):
        """Retorna las iniciales del usuario para el avatar"""
        iniciales = ''
        if self.nombre:
            iniciales += self.nombre[0].upper()
        if self.apellido_paterno:
            iniciales += self.apellido_paterno[0].upper()
        return iniciales or 'U'
    
    @property
    def total_solicitudes(self):
        """Retorna el total de solicitudes del usuario"""
        return self.solicitudes.count() if hasattr(self, 'solicitudes') else 0
    
    @property
    def solicitudes_aprobadas(self):
        """Retorna el número de solicitudes aprobadas"""
        if hasattr(self, 'solicitudes'):
            return self.solicitudes.filter_by(id_estatus=3).count()
        return 0
    
    @property
    def horas_laboratorio_usadas(self):
        """Calcula las horas totales de uso de laboratorio"""
        if hasattr(self, 'solicitudes'):
            total_horas = 0
            solicitudes_completadas = self.solicitudes.filter_by(id_estatus=6).all()
            for solicitud in solicitudes_completadas:
                total_horas += solicitud.duracion_horas
            return total_horas
        return 0
    
    @property
    def laboratorios_utilizados(self):
        """Retorna el número de laboratorios diferentes utilizados"""
        if hasattr(self, 'solicitudes'):
            from app.models.solicitud import Solicitud
            laboratorios = set()
            solicitudes_aprobadas = self.solicitudes.filter(Solicitud.id_estatus.in_([3, 6])).all()
            for solicitud in solicitudes_aprobadas:
                laboratorios.add(solicitud.id_laboratorio)
            return len(laboratorios)
        return 0
    
    def to_dict(self):
        """Convierte el usuario a diccionario para JSON"""
        return {
            'id_usuario': self.id_usuario,
            'username': self.username,
            'email': self.email,
            'nombre_completo': self.nombre_completo,
            'nombre': self.nombre,
            'apellido_paterno': self.apellido_paterno,
            'apellido_materno': self.apellido_materno,
            'telefono': self.telefono,
            'ruta_imagen': self.ruta_imagen,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'institucion': self.institucion.nombre_institucion if self.institucion else None,
            'area': self.area.nombre_area if self.area else None,
            'rol': self.roles.nombre_rol if self.roles else None,
            'estadisticas': {
                'total_solicitudes': self.total_solicitudes,
                'solicitudes_aprobadas': self.solicitudes_aprobadas,
                'horas_laboratorio': self.horas_laboratorio_usadas,
                'laboratorios_utilizados': self.laboratorios_utilizados
            }
        }