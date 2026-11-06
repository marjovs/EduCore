from sqlalchemy import func

from app import db
from app.models.curso import Curso
from app.services import RegraNegocioError


def listar_cursos():
    return Curso.query.order_by(Curso.nome).all()


def listar_cursos_ativos():
    return Curso.query.filter_by(status="Ativo").order_by(Curso.nome).all()


def buscar_curso(curso_id):
    return db.get_or_404(Curso, curso_id)


def _validar_nome(nome, curso_id=None):
    # O PostgreSQL diferencia maiúsculas; aqui a comparação ignora maiúsculas.
    consulta = Curso.query.filter(func.lower(Curso.nome) == nome.lower())
    if curso_id is not None:
        consulta = consulta.filter(Curso.id != curso_id)

    if consulta.first():
        raise RegraNegocioError("Já existe um curso com este nome.")


def cadastrar_curso(dados):
    _validar_nome(dados["nome"])

    curso = Curso(
        nome=dados["nome"],
        descricao=dados.get("descricao"),
        carga_horaria=dados["carga_horaria"],
        modalidade=dados["modalidade"],
        status=dados.get("status", "Ativo")
    )

    db.session.add(curso)
    db.session.commit()

    return curso


def atualizar_curso(curso, dados):
    _validar_nome(dados["nome"], curso_id=curso.id)

    curso.nome = dados["nome"]
    curso.descricao = dados.get("descricao")
    curso.carga_horaria = dados["carga_horaria"]
    curso.modalidade = dados["modalidade"]
    curso.status = dados.get("status", curso.status)

    db.session.commit()

    return curso


def excluir_curso(curso):
    if curso.turmas:
        raise RegraNegocioError(
            "Não é possível excluir: o curso possui turmas vinculadas. "
            "Altere o status para Inativo."
        )

    db.session.delete(curso)
    db.session.commit()
