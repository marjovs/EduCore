from app import db
from app.models.aluno import Aluno
from app.services import RegraNegocioError


def listar_alunos():
    return Aluno.query.order_by(Aluno.nome).all()


def buscar_aluno(aluno_id):
    return db.get_or_404(Aluno, aluno_id)


def _validar_unicidade(email, cpf, aluno_id=None):
    consulta = Aluno.query
    if aluno_id is not None:
        consulta = consulta.filter(Aluno.id != aluno_id)

    if consulta.filter(Aluno.email == email).first():
        raise RegraNegocioError("Já existe um aluno com este e-mail.")

    if consulta.filter(Aluno.cpf == cpf).first():
        raise RegraNegocioError("Já existe um aluno com este CPF.")


def cadastrar_aluno(dados):
    email = dados["email"].strip().lower()
    _validar_unicidade(email, dados["cpf"])

    aluno = Aluno(
        nome=dados["nome"],
        email=email,
        cpf=dados["cpf"],
        telefone=dados.get("telefone"),
        data_nascimento=dados["data_nascimento"]
    )

    db.session.add(aluno)
    db.session.commit()

    return aluno


def atualizar_aluno(aluno, dados):
    email = dados["email"].strip().lower()
    _validar_unicidade(email, dados["cpf"], aluno_id=aluno.id)

    aluno.nome = dados["nome"]
    aluno.email = email
    aluno.cpf = dados["cpf"]
    aluno.telefone = dados.get("telefone")
    aluno.data_nascimento = dados["data_nascimento"]

    db.session.commit()

    return aluno


def excluir_aluno(aluno):
    if aluno.matriculas:
        raise RegraNegocioError(
            "Não é possível excluir: o aluno possui matrículas. "
            "Cancele as matrículas em vez de excluir o aluno."
        )

    db.session.delete(aluno)
    db.session.commit()
