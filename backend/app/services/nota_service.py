from app import db
from app.models.nota import Nota


def listar_notas():
    return Nota.query.order_by(Nota.data.desc()).all()


def buscar_nota(nota_id):
    return Nota.query.get_or_404(nota_id)


def cadastrar_nota(dados):
    nota = Nota(
        avaliacao=dados["avaliacao"],
        valor=dados["valor"],
        data=dados["data"],
        matricula_id=dados["matricula_id"]
    )

    db.session.add(nota)
    db.session.commit()

    return nota


def atualizar_nota(nota, dados):
    nota.avaliacao = dados["avaliacao"]
    nota.valor = dados["valor"]
    nota.data = dados["data"]

    db.session.commit()

    return nota


def excluir_nota(nota):
    db.session.delete(nota)
    db.session.commit()