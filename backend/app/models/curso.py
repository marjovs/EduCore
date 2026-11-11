from app import db


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    carga_horaria = db.Column(db.Integer, nullable=False)
    modalidade = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default="Ativo", nullable=False)
