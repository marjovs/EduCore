from sqlalchemy import func, or_, select

from app import db
from app.models.aluno import Aluno
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.services import RegraNegocioError, obter_ou_404
from app.services.busca import condicao_busca, cpf_sem_pontuacao, paginar
from app.validacao import somente_digitos


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
    return obter_ou_404(Aluno, aluno_id)


def _validar_unicidade(email, cpf, aluno_id=None):
    consulta = Aluno.query
    if aluno_id is not None:
        consulta = consulta.filter(Aluno.id != aluno_id)

    if consulta.filter(func.lower(Aluno.email) == email).first():
        raise RegraNegocioError("Já existe um aluno com este e-mail.")

    # Compara só os dígitos, para que 111.222.333-44 e 11122233344 sejam o
    # mesmo CPF (inclusive em registros antigos salvos com pontuação).
    if consulta.filter(cpf_sem_pontuacao() == somente_digitos(cpf)).first():
        raise RegraNegocioError("Já existe um aluno com este CPF.")


def cadastrar_aluno(dados):
    email = dados["email"].strip().lower()
    cpf = somente_digitos(dados["cpf"])
    _validar_unicidade(email, cpf)

    aluno = Aluno(
        nome=dados["nome"],
        email=email,
        cpf=cpf,
        telefone=dados.get("telefone"),
        data_nascimento=dados["data_nascimento"]
    )

    db.session.add(aluno)
    db.session.commit()

    return aluno


def atualizar_aluno(aluno, dados):
    email = dados["email"].strip().lower()
    cpf = somente_digitos(dados["cpf"])
    _validar_unicidade(email, cpf, aluno_id=aluno.id)

    aluno.nome = dados["nome"]
    aluno.email = email
    aluno.cpf = cpf
    aluno.telefone = dados.get("telefone")
    aluno.data_nascimento = dados["data_nascimento"]

    db.session.commit()

    return aluno


def excluir_aluno(aluno):
    """Exclui o aluno se ele não tiver matrícula ativa.

    As matrículas canceladas do aluno (com as notas e frequências delas) são
    apagadas junto, numa única transação.
    """
    if any(matricula.status == "Ativa" for matricula in aluno.matriculas):
        raise RegraNegocioError(
            "Não é possível excluir: o aluno possui matrícula ativa. "
            "Cancele a matrícula antes de excluir o aluno."
        )

    ids = [matricula.id for matricula in aluno.matriculas]
    if ids:
        Nota.query.filter(Nota.matricula_id.in_(ids)).delete(synchronize_session=False)
        Frequencia.query.filter(Frequencia.matricula_id.in_(ids)).delete(synchronize_session=False)
        Matricula.query.filter(Matricula.id.in_(ids)).delete(synchronize_session=False)
        db.session.expire(aluno, ["matriculas"])

    db.session.delete(aluno)
    db.session.commit()
