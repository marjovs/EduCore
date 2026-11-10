from sqlalchemy import case, func
from sqlalchemy.orm import contains_eager

from app import db
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.turma import Turma
from app.services.busca import condicao_busca, paginar


def _consulta_filtrada(consulta, busca=None, turma_id=None, ano=None):
    """Aplica os filtros da secretaria. Considera só matrículas ativas."""
    consulta = (
        consulta
        .join(Frequencia.matricula)
        .join(Matricula.aluno)
        .join(Matricula.turma)
        .filter(Matricula.status == "Ativa")
    )

    if busca:
        consulta = consulta.filter(condicao_busca(busca))

    if turma_id:
        consulta = consulta.filter(Matricula.turma_id == turma_id)

    if ano:
        consulta = consulta.filter(Turma.ano == ano)

    return consulta


def buscar_frequencias(busca=None, turma_id=None, ano=None, pagina=1):
    """Retorna (página de registros, resumo) com os filtros aplicados.

    Presenças e faltas são contadas no banco sobre todos os resultados.
    """
    consulta = (
        _consulta_filtrada(Frequencia.query, busca, turma_id, ano)
        .options(
            contains_eager(Frequencia.matricula).contains_eager(Matricula.aluno),
            contains_eager(Frequencia.matricula)
            .contains_eager(Matricula.turma)
            .joinedload(Turma.curso),
        )
        .order_by(Frequencia.data.desc(), Frequencia.id.desc())
    )

    total, presencas = _consulta_filtrada(
        db.session.query(
            func.count(Frequencia.id),
            func.coalesce(func.sum(case((Frequencia.status == "Presente", 1), else_=0)), 0),
        ),
        busca, turma_id, ano
    ).one()

    return paginar(consulta, pagina), {
        "presencas": presencas,
        "faltas": total - presencas,
        "percentual": presencas * 100 / total if total else None,
    }


def registrar_frequencias(lista_dados, data):
    """Grava (ou atualiza) a frequência de vários alunos numa única transação.

    lista_dados: [{"matricula_id": int, "status": "Presente" ou "Falta"}, ...]
    """
    ids = [dados["matricula_id"] for dados in lista_dados]

    existentes = {
        frequencia.matricula_id: frequencia
        for frequencia in Frequencia.query.filter(
            Frequencia.matricula_id.in_(ids),
            Frequencia.data == data
        )
    }

    for dados in lista_dados:
        frequencia = existentes.get(dados["matricula_id"])

        if frequencia:
            frequencia.status = dados["status"]
        else:
            db.session.add(Frequencia(
                matricula_id=dados["matricula_id"],
                data=data,
                status=dados["status"],
                observacao=dados.get("observacao")
            ))

    db.session.commit()
