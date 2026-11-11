"""Configuração dos testes.

Os testes rodam num SQLite temporário: nunca tocam no banco do Neon.
Rodar a partir da pasta backend:  python -m pytest
"""
import os
import tempfile
from datetime import date

# Precisa vir antes de importar o app: o config.py lê estas variáveis no import
# (e o load_dotenv não sobrescreve variáveis já definidas).
_PASTA = tempfile.mkdtemp(prefix="educore-testes-")
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(_PASTA, "testes.db")
os.environ["SECRET_KEY"] = "chave-de-teste"

import pytest  # noqa: E402
from sqlalchemy import insert  # noqa: E402

from app import create_app, db  # noqa: E402
from app.models.aluno import Aluno  # noqa: E402
from app.models.curso import Curso  # noqa: E402
from app.models.frequencia import Frequencia  # noqa: E402
from app.models.matricula import Matricula  # noqa: E402
from app.models.nota import Nota  # noqa: E402
from app.models.turma import Turma  # noqa: E402
from app.models.usuario import Usuario  # noqa: E402

SENHAS = {"secretaria": "senha-secretaria", "instrutor": "senha-instrutor", "coordenacao": "senha-coord"}


@pytest.fixture(scope="session")
def app():
    aplicacao = create_app()
    aplicacao.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    return aplicacao


@pytest.fixture(scope="session")
def hashes():
    # O hash scrypt é lento de propósito; calcula uma vez só por execução.
    from werkzeug.security import generate_password_hash
    return {perfil: generate_password_hash(senha) for perfil, senha in SENHAS.items()}


@pytest.fixture(autouse=True)
def banco(app, hashes):
    """Banco limpo, com os 3 usuários iniciais, para cada teste."""
    with app.app_context():
        db.drop_all()
        db.create_all()
        for perfil, senha_hash in hashes.items():
            db.session.add(Usuario(email=f"{perfil}@educore.com", perfil=perfil, senha_hash=senha_hash))
        db.session.commit()
        yield
        db.session.remove()


@pytest.fixture
def cliente(app):
    return app.test_client()


def _logado(app, perfil):
    c = app.test_client()
    with c.session_transaction() as sessao:
        sessao["usuario"] = f"{perfil}@educore.com"
        sessao["perfil"] = perfil
    return c


@pytest.fixture
def secretaria(app):
    return _logado(app, "secretaria")


@pytest.fixture
def coordenacao(app):
    return _logado(app, "coordenacao")


@pytest.fixture
def instrutor(app):
    return _logado(app, "instrutor")


def linhas(html):
    """Quantidade de linhas de dados na primeira tabela da página."""
    corpo = html.split("<tbody>")[1].split("</tbody>")[0]
    return corpo.count("<tr class=\"border")


@pytest.fixture
def escola(app):
    """~5 anos de escola: 601 alunos, 1/4 das matrículas canceladas,
    1 nota e 5 frequências (4 presenças) por matrícula."""
    anos = range(2022, 2027)
    with app.app_context():
        curso = Curso(nome="Informática", carga_horaria=1000, modalidade="Presencial", status="Ativo")
        db.session.add(curso)
        db.session.flush()

        turmas = {}
        for ano in anos:
            for letra in "ABCD":
                turma = Turma(nome=f"Turma {letra}", ano=ano, turno="Matutino", status="Ativa", curso_id=curso.id)
                db.session.add(turma)
                turmas[(ano, letra)] = turma
        db.session.flush()

        # Inserções em lote (insert(...) com lista) para o fixture ser rápido.
        nomes = [(f"Aluno {i:03d}", f"a{i}@x.com", f"{i:03d}11122200") for i in range(600)]
        nomes.append(("Zuleica Prado", "z@x.com", "98765432100"))
        db.session.execute(insert(Aluno), [
            {"id": i + 1, "nome": n, "email": e, "cpf": c, "data_nascimento": date(2005, 1, 1)}
            for i, (n, e, c) in enumerate(nomes)
        ])

        matriculas = []
        for i in range(len(nomes)):
            ano = anos[i % 5]
            matriculas.append({
                "id": i + 1, "aluno_id": i + 1, "turma_id": turmas[(ano, "ABCD"[i % 4])].id,
                "data_matricula": date(ano, 2, 1),
                "status": "Cancelada" if i % 4 == 0 and i < 600 else "Ativa",
            })
        db.session.execute(insert(Matricula), matriculas)

        db.session.execute(insert(Nota), [
            {"avaliacao": "P1", "valor": 7.0, "data": date(2026, 3, 1), "matricula_id": m["id"]}
            for m in matriculas
        ])
        db.session.execute(insert(Frequencia), [
            {"data": date(2026, 3, 2 + dia), "status": "Presente" if dia < 4 else "Falta", "matricula_id": m["id"]}
            for m in matriculas for dia in range(5)
        ])
        db.session.commit()

        return {
            "ativas": sum(1 for m in matriculas if m["status"] == "Ativa"),
            "canceladas": sum(1 for m in matriculas if m["status"] == "Cancelada"),
            "matricula_zuleica": matriculas[-1]["id"],
            "turma_zuleica": matriculas[-1]["turma_id"],
            "turma_aluno_001": matriculas[1]["turma_id"],
            "turma_2026_c": turmas[(2026, "C")].id,
            "zuleica": len(nomes),
        }
