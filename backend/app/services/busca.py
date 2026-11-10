"""Filtros de busca e paginação reaproveitados pelas listagens."""
import re

from sqlalchemy import func, or_

from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.turma import Turma

POR_PAGINA = 20


def _somente_digitos(texto):
    return re.sub(r"\D", "", texto)


def cpf_sem_pontuacao():
    """Expressão SQL do CPF sem pontos e traço."""
    return func.replace(func.replace(Aluno.cpf, ".", ""), "-", "")


def condicao_busca(texto, incluir_turma_curso=False):
    """Condição SQL para buscar por nome do aluno ou CPF (com ou sem pontuação).

    Com incluir_turma_curso=True também procura no nome da turma e do curso.
    A consulta precisa ter join com Aluno (e com Turma/Curso nesse caso).
    """
    termo = "%" + texto.strip() + "%"
    condicoes = [Aluno.nome.ilike(termo)]

    digitos = _somente_digitos(texto)
    if digitos:
        condicoes.append(cpf_sem_pontuacao().like("%" + digitos + "%"))

    if incluir_turma_curso:
        condicoes += [Turma.nome.ilike(termo), Curso.nome.ilike(termo)]

    return or_(*condicoes)


def paginar(consulta, pagina):
    """Pagina uma consulta do ORM (Model.query ou db.session.query)."""
    return consulta.paginate(page=pagina, per_page=POR_PAGINA, error_out=False)
