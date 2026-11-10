from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.models.turma import Turma
from app.services import RegraNegocioError, obter_ou_404


def listar_turmas():
    return (
        Turma.query
        .options(joinedload(Turma.curso))
        .order_by(Turma.nome)
        .all()
    )


def listar_turmas_para_filtro():
    """Turmas da mais recente para a mais antiga, para os selects de filtro."""
    return (
        Turma.query
        .options(joinedload(Turma.curso))
        .order_by(Turma.ano.desc(), Turma.nome)
        .all()
    )


def listar_turmas_ativas():
    return (
        Turma.query
        .options(joinedload(Turma.curso))
        .filter_by(status="Ativa")
        .order_by(Turma.nome)
        .all()
    )


def buscar_turma(turma_id):
    return obter_ou_404(Turma, turma_id)


def _validar_duplicidade(dados, turma_id=None):
    """Não permite duas turmas com o mesmo nome, ano e curso (ignora maiúsculas)."""
    consulta = Turma.query.filter(
        func.lower(Turma.nome) == dados["nome"].lower(),
        Turma.ano == dados["ano"],
        Turma.curso_id == dados["curso_id"],
    )
    if turma_id is not None:
        consulta = consulta.filter(Turma.id != turma_id)

    if consulta.first():
        raise RegraNegocioError(
            "Já existe a turma \"" + dados["nome"] + "\" neste curso e ano."
        )


def cadastrar_turma(dados):
    _validar_duplicidade(dados)

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
    _validar_duplicidade(dados, turma_id=turma.id)

    turma.nome = dados["nome"]
    turma.ano = dados["ano"]
    turma.turno = dados["turno"]
    turma.status = dados.get("status", turma.status)
    turma.curso_id = dados["curso_id"]

    db.session.commit()

    return turma


def excluir_turma(turma):
    if turma.matriculas:
        raise RegraNegocioError(
            "Não é possível excluir: a turma possui matrículas. "
            "Altere o status para Inativa."
        )

    db.session.delete(turma)
    db.session.commit()
