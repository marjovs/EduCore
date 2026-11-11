from sqlalchemy import func
from sqlalchemy.orm import contains_eager

from app import db
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.turma import Turma
from app.services import RegraNegocioError
from app.services.busca import filtrar_por_matricula_ativa, paginar


def _consulta_filtrada(consulta, busca=None, turma_id=None, ano=None):
    return filtrar_por_matricula_ativa(consulta, Nota.matricula, busca, turma_id, ano)


def buscar_notas(busca=None, turma_id=None, ano=None, pagina=1):
    """Retorna (página de notas, resumo) com os filtros aplicados.

    O resumo (quantidade e média) é calculado no banco sobre todos os
    resultados, não só sobre a página exibida.
    """
    consulta = (
        _consulta_filtrada(Nota.query, busca, turma_id, ano)
        .options(
            contains_eager(Nota.matricula).contains_eager(Matricula.aluno),
            contains_eager(Nota.matricula)
            .contains_eager(Matricula.turma)
            .joinedload(Turma.curso),
        )
        .order_by(Nota.data.desc(), Nota.id.desc())
    )

    total, media = _consulta_filtrada(
        db.session.query(func.count(Nota.id), func.avg(Nota.valor)),
        busca, turma_id, ano
    ).one()

    return paginar(consulta, pagina), {"total": total, "media": media}


def registrar_notas(lista_dados):
    """Grava as notas de uma avaliação para vários alunos numa única transação.

    Recusa a operação se algum aluno já tiver nota para a mesma avaliação.
    """
    if not lista_dados:
        return

    avaliacao = lista_dados[0]["avaliacao"]
    ids = [dados["matricula_id"] for dados in lista_dados]

    ja_lancadas = Nota.query.filter(
        Nota.matricula_id.in_(ids),
        func.lower(Nota.avaliacao) == avaliacao.lower()
    ).count()

    if ja_lancadas:
        raise RegraNegocioError(
            "A avaliação \"" + avaliacao + "\" já possui notas lançadas "
            "para esta turma. Use outro nome de avaliação."
        )

    for dados in lista_dados:
        db.session.add(Nota(
            avaliacao=dados["avaliacao"],
            valor=dados["valor"],
            data=dados["data"],
            matricula_id=dados["matricula_id"]
        ))

    db.session.commit()
