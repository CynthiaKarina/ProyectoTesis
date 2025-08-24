from app import db
from datetime import datetime


class ProyectoRequest(db.Model):
    __tablename__ = 'proyecto_request'

    id_request = db.Column(db.BigInteger, primary_key=True)
    id_proyecto = db.Column(db.BigInteger, db.ForeignKey('proyecto.id_proyecto'), nullable=False)
    id_solicitante = db.Column(db.BigInteger, db.ForeignKey('usuario.id_usuario'), nullable=False)
    tipo = db.Column(db.String(30), nullable=False, default='publicacion')  # publicacion | actualizacion
    cambios = db.Column(db.Text, nullable=True)  # descripción de cambios / diff resumido
    estatus = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente | aprobado | rechazado
    reviewer_id = db.Column(db.BigInteger, db.ForeignKey('usuario.id_usuario'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    proyecto = db.relationship('Proyecto', backref=db.backref('solicitudes_publicacion', lazy=True))


