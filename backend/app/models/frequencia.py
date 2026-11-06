from app import db

class Frequencia(db.Model):
    __tablename__ = "frequencias"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    observacao = db.Column(db.Text)
    matricula_id = db.Column(db.Integer, db.ForeignKey("matriculas.id"), nullable=False)
    matricula = db.relationship("Matricula", backref=db.backref("frequencias", lazy=True))