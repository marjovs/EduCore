from app import db


class Turma(db.Model):
    __tablename__ = "turmas"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    turno = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default="Ativa", nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey("cursos.id"), nullable=False)
    curso = db.relationship("Curso", backref=db.backref("turmas", lazy=True))
