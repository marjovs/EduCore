from sqlalchemy.orm import joinedload

from app import db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.turma import Turma


def listar_matriculas():
    return (
        Matricula.query
        .options(
            joinedload(Matricula.aluno),
            joinedload(Matricula.turma).joinedload(Turma.curso),
        )
        .order_by(Matricula.data_matricula.desc())
        .all()
    )


def listar_matriculas_ativas_da_turma(turma_id):
    return (
        Matricula.query
        .join(Matricula.aluno)
        .options(joinedload(Matricula.aluno))
        .filter(Matricula.turma_id == turma_id, Matricula.status == "Ativa")
        .order_by(Aluno.nome)
        .all()
    )


def existe_matricula_ativa(aluno_id, turma_id):
    return Matricula.query.filter_by(
        aluno_id=aluno_id,
        turma_id=turma_id,
        status="Ativa"
    ).first() is not None


def buscar_matricula(matricula_id):
    return db.get_or_404(Matricula, matricula_id)


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


def cancelar_matricula(matricula):
    matricula.status = "Cancelada"
    db.session.commit()

    return matricula
