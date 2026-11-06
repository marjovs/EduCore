from app import db
from app.models.turma import Turma


def listar_turmas():
    return Turma.query.order_by(Turma.nome).all()


def buscar_turma(turma_id):
    return Turma.query.get_or_404(turma_id)


def cadastrar_turma(dados):
    turma = Turma(
        nome=dados["nome"],
        ano=dados["ano"],
        turno=dados["turno"],
        status=dados.get("status", "Ativa"),
        curso_id=dados["curso_id"]
    )

    db.session.add(turma)
    db.session.commit()

    return turma


def atualizar_turma(turma, dados):
    turma.nome = dados["nome"]
    turma.ano = dados["ano"]
    turma.turno = dados["turno"]
    turma.status = dados.get("status", turma.status)
    turma.curso_id = dados["curso_id"]

    db.session.commit()

    return turma


def excluir_turma(turma):
    db.session.delete(turma)
    db.session.commit()