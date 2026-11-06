from app import db
from app.models.frequencia import Frequencia


def listar_frequencias():
    return Frequencia.query.order_by(Frequencia.data.desc()).all()


def buscar_frequencia(frequencia_id):
    return Frequencia.query.get_or_404(frequencia_id)


def buscar_frequencia_por_data(matricula_id, data):
    return Frequencia.query.filter_by(
        matricula_id=matricula_id,
        data=data
    ).first()


def registrar_frequencia(dados):
    frequencia = Frequencia(
        matricula_id=dados["matricula_id"],
        data=dados["data"],
        status=dados["status"],
        observacao=dados.get("observacao")
    )

    db.session.add(frequencia)
    db.session.commit()

    return frequencia


def atualizar_frequencia(frequencia, dados):
    frequencia.status = dados["status"]

    if "observacao" in dados:
        frequencia.observacao = dados["observacao"]

    db.session.commit()

    return frequencia


def excluir_frequencia(frequencia):
    db.session.delete(frequencia)
    db.session.commit()
