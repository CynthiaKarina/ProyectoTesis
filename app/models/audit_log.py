from app import db
from datetime import datetime


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    actor_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=True)
    target_user_id = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=True)
    from_value = db.Column(db.String(255), nullable=True)
    to_value = db.Column(db.String(255), nullable=True)
    extra = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AuditLog {self.action} {self.actor_id}->{self.target_user_id} {self.from_value}->{self.to_value}>"


