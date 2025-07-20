from app import db

class Tipo_Laboratorio(db.Model):
    __tablename__ = 'tipo_laboratorio'

    id_tipo_laboratorio = db.Column(db.BigInteger, primary_key=True)
    nombre_tipo_laboratorio = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

    def __repr__(self):
        return f'<Tipo_Laboratorio {self.nombre_tipo_laboratorio}>'

    def to_dict(self):
        return {
            'id_tipo_laboratorio': self.id_tipo_laboratorio,
            'nombre_tipo_laboratorio': self.nombre_tipo_laboratorio,
            'descripcion': self.descripcion
        }