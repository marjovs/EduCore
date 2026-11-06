from sqlalchemy.orm import joinedload

from app import db
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.turma import Turma


def listar_frequencias():
    return (
        Frequencia.query
        .options(
            joinedload(Frequencia.matricula).joinedload(Matricula.aluno),
            joinedload(Frequencia.matricula)
            .joinedload(Matricula.turma)
            .joinedload(Turma.curso),
        )
        .order_by(Frequencia.data.desc())
        .all()
    )


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
