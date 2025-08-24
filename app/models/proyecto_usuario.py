from app import db


class ProyectoUsuario(db.Model):
    __tablename__ = 'proyecto_usuario'

    id_proyecto_usuario = db.Column(db.BigInteger, primary_key=True)
    id_proyecto = db.Column(db.BigInteger, db.ForeignKey('proyecto.id_proyecto'), nullable=False)
    id_usuario = db.Column(db.BigInteger, db.ForeignKey('usuario.id_usuario'), nullable=False)
    rol_en_proyecto = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<ProyectoUsuario proyecto={self.id_proyecto} usuario={self.id_usuario}>'


