from app import db
from datetime import datetime


class RoleRequest(db.Model):
    __tablename__ = 'role_request'

    id_request = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    requested_role = db.Column(db.String(50), nullable=False)  # 'administrativo' | 'admin_laboratorio'
    id_laboratorio = db.Column(db.Integer, nullable=True)  # opcional para admin de laboratorio
    status = db.Column(db.String(20), nullable=False, default='pendiente')  # pendiente | aprobado | rechazado
    note = db.Column(db.Text, nullable=True)
    reviewed_by = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id_request': self.id_request,
            'id_usuario': self.id_usuario,
            'requested_role': self.requested_role,
            'status': self.status,
            'note': self.note,
            'reviewed_by': self.reviewed_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
        }


