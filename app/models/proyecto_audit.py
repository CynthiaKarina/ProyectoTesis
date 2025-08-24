from app import db
from datetime import datetime


class ProyectoAudit(db.Model):
    __tablename__ = 'proyecto_audit'

    id_audit = db.Column(db.BigInteger, primary_key=True)
    id_proyecto = db.Column(db.BigInteger, db.ForeignKey('proyecto.id_proyecto'), nullable=False)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuario.id_usuario'), nullable=True)
    accion = db.Column(db.String(40), nullable=False)  # crear, editar, finalizar
    detalles = db.Column(db.Text, nullable=True)  # JSON/string con cambios
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProyectoAudit proyecto={self.id_proyecto} accion={self.accion} fecha={self.fecha}>'


