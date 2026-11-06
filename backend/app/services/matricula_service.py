from app import db
from app.models.matricula import Matricula


def listar_matriculas():
    return Matricula.query.order_by(
        Matricula.data_matricula.desc()
    ).all()


def buscar_matricula(matricula_id):
    return Matricula.query.get_or_404(matricula_id)


def cadastrar_matricula(dados):
    matricula = Matricula(
        data_matricula=dados["data_matricula"],
        status=dados.get("status", "Ativa"),
        aluno_id=dados["aluno_id"],
        turma_id=dados["turma_id"]
    )

    db.session.add(matricula)
    db.session.commit()

    return matricula


def atualizar_matricula(matricula, dados):
    matricula.data_matricula = dados["data_matricula"]
    matricula.status = dados.get("status", matricula.status)
    matricula.aluno_id = dados["aluno_id"]
    matricula.turma_id = dados["turma_id"]

    db.session.commit()

    return matricula


def cancelar_matricula(matricula):
    matricula.status = "Cancelada"
    db.session.commit()

    return matricula