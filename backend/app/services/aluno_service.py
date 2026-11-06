from app import db
from app.models.aluno import Aluno


def listar_alunos():
    return Aluno.query.order_by(Aluno.nome).all()


def buscar_aluno(aluno_id):
    return Aluno.query.get_or_404(aluno_id)


def cadastrar_aluno(dados):
    aluno = Aluno(
        nome=dados["nome"],
        email=dados["email"],
        cpf=dados["cpf"],
        telefone=dados.get("telefone"),
        data_nascimento=dados["data_nascimento"]
    )

    db.session.add(aluno)
    db.session.commit()

    return aluno


def atualizar_aluno(aluno, dados):
    aluno.nome = dados["nome"]
    aluno.email = dados["email"]
    aluno.cpf = dados["cpf"]
    aluno.telefone = dados.get("telefone")
    aluno.data_nascimento = dados["data_nascimento"]

    db.session.commit()

    return aluno


def excluir_aluno(aluno):
    db.session.delete(aluno)
    db.session.commit()