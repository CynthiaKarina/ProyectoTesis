from app import db
from datetime import datetime
from sqlalchemy import func

class Proyecto(db.Model):
    __tablename__ = 'proyecto'

    id_proyecto = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    nombre_proyecto = db.Column(db.String(300), nullable=False)
    resumen = db.Column(db.Text)
    adjunto = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.Date)
    tipo_proyecto = db.Column(db.String(100))
    estatus = db.Column(db.String(50), default='En Desarrollo')
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, nullable=False, default=func.current_timestamp(), onupdate=func.current_timestamp())

    def __repr__(self):
        return f'<Proyecto {self.nombre_proyecto}>'

    @property
    def estado_proyecto(self):
        """Retorna el estado del proyecto con formato legible"""
        estados = {
            'En Desarrollo': 'En Desarrollo',
            'Completado': 'Completado',
            'Suspendido': 'Suspendido',
            'Cancelado': 'Cancelado',
            'En Revision': 'En Revisión',
            'Aprobado': 'Aprobado'
        }
        return estados.get(self.estatus, self.estatus)
    
    @property
    def color_estado(self):
        """Retorna el color asociado al estado del proyecto"""
        colores = {
            'En Desarrollo': '#17a2b8',    # Azul
            'Completado': '#28a745',       # Verde
            'Suspendido': '#ffc107',       # Amarillo
            'Cancelado': '#dc3545',        # Rojo
            'En Revision': '#6c757d',      # Gris
            'Aprobado': '#20c997'          # Verde agua
        }
        return colores.get(self.estatus, '#6c757d')
    
    @property
    def icono_estado(self):
        """Retorna el icono asociado al estado del proyecto"""
        iconos = {
            'En Desarrollo': 'fas fa-cogs',
            'Completado': 'fas fa-check-circle',
            'Suspendido': 'fas fa-pause-circle',
            'Cancelado': 'fas fa-times-circle',
            'En Revision': 'fas fa-search',
            'Aprobado': 'fas fa-thumbs-up'
        }
        return iconos.get(self.estatus, 'fas fa-project-diagram')
    
    @property
    def tipo_proyecto_icono(self):
        """Retorna el icono asociado al tipo de proyecto"""
        iconos_tipo = {
            'Investigación': 'fas fa-microscope',
            'Desarrollo': 'fas fa-code',
            'Innovación': 'fas fa-lightbulb',
            'Educativo': 'fas fa-graduation-cap',
            'Empresarial': 'fas fa-building',
            'Social': 'fas fa-users',
            'Tecnológico': 'fas fa-laptop-code',
            'Científico': 'fas fa-atom'
        }
        return iconos_tipo.get(self.tipo_proyecto, 'fas fa-project-diagram')
    
    @property
    def resumen_corto(self):
        """Retorna un resumen cortado para mostrar en listas"""
        if self.resumen and len(self.resumen) > 100:
            return self.resumen[:100] + '...'
        return self.resumen or 'Sin resumen disponible'
    
    @property
    def fecha_formateada(self):
        """Retorna la fecha formateada en español"""
        if self.fecha:
            meses = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            return f"{self.fecha.day} de {meses[self.fecha.month]} de {self.fecha.year}"
        return 'Fecha no especificada'
    
    @property
    def tiempo_desde_creacion(self):
        """Calcula el tiempo transcurrido desde la creación"""
        if self.fecha_creacion:
            delta = datetime.utcnow() - self.fecha_creacion
            if delta.days > 0:
                return f"Hace {delta.days} días"
            elif delta.seconds > 3600:
                horas = delta.seconds // 3600
                return f"Hace {horas} horas"
            else:
                minutos = delta.seconds // 60
                return f"Hace {minutos} minutos"
        return "Recién creado"

    def to_dict(self):
        return {
            'id_proyecto': self.id_proyecto,
            'nombre_proyecto': self.nombre_proyecto,
            'resumen': self.resumen,
            'resumen_corto': self.resumen_corto,
            'adjunto': self.adjunto,
            'fecha': self.fecha.isoformat() if self.fecha else None,
            'fecha_formateada': self.fecha_formateada,
            'tipo_proyecto': self.tipo_proyecto,
            'tipo_proyecto_icono': self.tipo_proyecto_icono,
            'estatus': self.estatus,
            'estado_proyecto': self.estado_proyecto,
            'color_estado': self.color_estado,
            'icono_estado': self.icono_estado,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'fecha_modificacion': self.fecha_modificacion.isoformat() if self.fecha_modificacion else None,
            'tiempo_desde_creacion': self.tiempo_desde_creacion
        } 