from sqlalchemy.orm import contains_eager, joinedload

from app import db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.services.busca import condicao_busca, paginar


def listar_matriculas(status=None):
    consulta = Matricula.query.options(
        joinedload(Matricula.aluno),
        joinedload(Matricula.turma).joinedload(Turma.curso),
    )

    if status:
        consulta = consulta.filter(Matricula.status == status)

    return consulta.order_by(
        Matricula.data_matricula.desc(), Matricula.id.desc()
    ).all()


def buscar_matriculas(status, busca=None, ano=None, pagina=1):
    """Lista paginada de matrículas com busca por aluno, CPF, turma ou curso."""
    consulta = (
        Matricula.query
        .join(Matricula.aluno)
        .join(Matricula.turma)
        .join(Turma.curso)
        .options(
            contains_eager(Matricula.aluno),
            contains_eager(Matricula.turma).contains_eager(Turma.curso),
        )
        .filter(Matricula.status == status)
    )

    if busca:
        consulta = consulta.filter(condicao_busca(busca, incluir_turma_curso=True))

    if ano:
        consulta = consulta.filter(Turma.ano == ano)

    consulta = consulta.order_by(Matricula.data_matricula.desc(), Matricula.id.desc())
    return paginar(consulta, pagina)


def contar_matriculas_canceladas():
    return Matricula.query.filter_by(status="Cancelada").count()


def listar_anos_das_turmas():
    """Anos que têm turmas, do mais recente para o mais antigo (para o filtro)."""
    return [
        ano for (ano,) in
        db.session.query(Turma.ano).distinct().order_by(Turma.ano.desc())
    ]


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
