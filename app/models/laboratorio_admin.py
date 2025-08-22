from app import db


class LaboratorioAdmin(db.Model):
    __tablename__ = 'laboratorio_admins'

    id = db.Column(db.Integer, primary_key=True)
    id_laboratorio = db.Column(db.Integer, db.ForeignKey('laboratorio.id_laboratorio'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('id_laboratorio', 'id_usuario', name='uq_lab_admin_usuario'),
    )


