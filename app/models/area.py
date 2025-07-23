from datetime import datetime
from app import db
from flask_login import current_user

def obtener_usuario_actual():
    """
    Devuelve el usuario que ha iniciado sesión actualmente.
    Si no hay usuario autenticado, retorna None.
    """
    if current_user and current_user.is_authenticated:
        return current_user
    return None


class Area(db.Model):
    __tablename__ = 'area'
    
    # Campos según la estructura de la base de datos
    id_area = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre_area = db.Column(db.String(100), nullable=False)
    creado_por = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(
        db.DateTime, 
        nullable=True, 
        default=db.func.current_timestamp(),
        server_default=db.func.current_timestamp()
    )
    ultima_modificacion = db.Column(
        db.DateTime, 
        nullable=True, 
        default=db.func.current_timestamp(),
        server_default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )
    modificado_por = db.Column(db.String(100), nullable=False)
    
    # Relación inversa con Usuario
    usuarios = db.relationship('User', back_populates='area', lazy=True)
    
    def __init__(self, nombre_area, creado_por = obtener_usuario_actual(), modificado_por=None, **kwargs):
        """
        Constructor personalizado para asegurar que los campos requeridos se llenen
        """
        self.nombre_area = nombre_area.strip() if nombre_area else None
        self.creado_por = creado_por.strip() if creado_por else 'Sistema'
        self.modificado_por = modificado_por.strip() if modificado_por else self.creado_por
        
        # Los campos de fecha se dejan que la base de datos los maneje automáticamente
        # No los establecemos explícitamente a menos que se proporcionen
        if 'fecha_creacion' in kwargs:
            self.fecha_creacion = kwargs['fecha_creacion']
        if 'ultima_modificacion' in kwargs:
            self.ultima_modificacion = kwargs['ultima_modificacion']
    
    def __repr__(self):
        return f'<Area {self.nombre_area}>'
    
    def to_dict(self):
        """Convierte el área a diccionario para JSON"""
        return {
            'id_area': self.id_area,
            'nombre_area': self.nombre_area,
            'creado_por': self.creado_por,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultima_modificacion': self.ultima_modificacion.isoformat() if self.ultima_modificacion else None,
            'modificado_por': self.modificado_por
        }
    
    def actualizar(self, nombre_area=None, modificado_por=None):
        """
        Método para actualizar el área de forma segura
        """
        if nombre_area:
            self.nombre_area = nombre_area.strip()
        if modificado_por:
            self.modificado_por = modificado_por.strip()
        # ultima_modificacion se actualiza automáticamente por onupdate
    
    @classmethod
    def crear_nueva(cls, nombre_area, creado_por):
        """
        Método de clase para crear una nueva área de forma segura
        """
        if not nombre_area or not nombre_area.strip():
            raise ValueError("El nombre del área es obligatorio")
        if not creado_por or not creado_por.strip():
            raise ValueError("El creador es obligatorio")
        
        return cls(
            nombre_area=nombre_area.strip(),
            creado_por=creado_por.strip(),
            modificado_por=creado_por.strip()
        )
