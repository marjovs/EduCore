from app import db


class Matricula(db.Model):
    __tablename__ = "matriculas"

    id = db.Column(db.Integer, primary_key=True)
    data_matricula = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default="Ativa", nullable=False)
    aluno_id = db.Column(db.Integer, db.ForeignKey("alunos.id"), nullable=False)
    turma_id = db.Column(db.Integer, db.ForeignKey("turmas.id"), nullable=False)
    aluno = db.relationship("Aluno", backref=db.backref("matriculas", lazy=True))
    turma = db.relationship("Turma", backref=db.backref("matriculas", lazy=True))
