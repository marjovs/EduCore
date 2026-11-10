from sqlalchemy import func, or_, select

from app import db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.services import RegraNegocioError
from app.services.busca import condicao_busca, paginar


def existe_aluno():
    return db.session.query(Aluno.id).first() is not None


def sugerir_alunos(texto, limite=10):
    """Até `limite` alunos cujo nome ou CPF contém o texto (para o autocompletar)."""
    return (
        Aluno.query
        .filter(condicao_busca(texto))
        .order_by(Aluno.nome, Aluno.id)
        .limit(limite)
        .all()
    )


def buscar_alunos_com_matriculas_ativas(busca=None, pagina=1):
    """Página de (aluno, nº de matrículas ativas), com busca por nome, CPF ou e-mail.

    A contagem vem de uma subconsulta, para não consultar o banco uma vez
    por aluno.
    """
    ativas = (
        select(func.count(Matricula.id))
        .where(Matricula.aluno_id == Aluno.id, Matricula.status == "Ativa")
        .correlate(Aluno)
        .scalar_subquery()
    )

    consulta = db.session.query(Aluno, ativas.label("ativas"))

    if busca:
        consulta = consulta.filter(or_(
            condicao_busca(busca),
            Aluno.email.ilike("%" + busca.strip() + "%"),
        ))

    return paginar(consulta.order_by(Aluno.nome, Aluno.id), pagina)


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
