from app import db
from app.models.curso import Curso


def listar_cursos():
    return Curso.query.order_by(Curso.nome).all()


def buscar_curso(curso_id):
    return Curso.query.get_or_404(curso_id)


def cadastrar_curso(dados):
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
    curso.nome = dados["nome"]
    curso.descricao = dados.get("descricao")
    curso.carga_horaria = dados["carga_horaria"]
    curso.modalidade = dados["modalidade"]
    curso.status = dados.get("status", curso.status)

    db.session.commit()

    return curso


def excluir_curso(curso):
    db.session.delete(curso)
    db.session.commit()