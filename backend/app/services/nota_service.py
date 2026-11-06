from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app import db
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.turma import Turma
from app.services import RegraNegocioError


def listar_notas():
    return (
        Nota.query
        .options(
            joinedload(Nota.matricula).joinedload(Matricula.aluno),
            joinedload(Nota.matricula)
            .joinedload(Matricula.turma)
            .joinedload(Turma.curso),
        )
        .order_by(Nota.data.desc())
        .all()
    )


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
