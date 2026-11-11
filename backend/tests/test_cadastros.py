"""Cursos, turmas, alunos e matrículas (área da secretaria)."""
from datetime import date

from app import db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.turma import Turma


def criar_curso_e_turma(app):
    with app.app_context():
        curso = Curso(nome="ADS", carga_horaria=100, modalidade="EAD", status="Ativo")
        db.session.add(curso)
        db.session.flush()
        turma = Turma(nome="T1", ano=2026, turno="Noturno", status="Ativa", curso_id=curso.id)
        db.session.add(turma)
        db.session.commit()
        return curso.id, turma.id


def criar_aluno(app, nome="Ana", cpf="52998224725", email="ana@x.com"):
    with app.app_context():
        aluno = Aluno(nome=nome, email=email, cpf=cpf, data_nascimento=date(2005, 1, 1))
        db.session.add(aluno)
        db.session.commit()
        return aluno.id


# ---- Cursos ----------------------------------------------------------------

def test_cadastrar_e_editar_curso(app, secretaria):
    dados = {"nome": "Redes", "carga_horaria": "800", "modalidade": "Presencial", "status": "Ativo"}
    html = secretaria.post("/secretaria/cursos/cadastrar", data=dados, follow_redirects=True).get_data(as_text=True)
    assert "Curso cadastrado com sucesso!" in html

    html = secretaria.post("/secretaria/cursos/cadastrar", data=dict(dados, nome="REDES")).get_data(as_text=True)
    assert "Já existe um curso com este nome." in html

    with app.app_context():
        curso_id = Curso.query.one().id
    html = secretaria.post(f"/secretaria/cursos/editar/{curso_id}", data=dict(dados, carga_horaria="900"),
                           follow_redirects=True).get_data(as_text=True)
    assert "Curso atualizado com sucesso!" in html


def test_carga_horaria_invalida(secretaria):
    dados = {"nome": "C", "carga_horaria": "99999999999999", "modalidade": "EAD", "status": "Ativo"}
    assert "carga horária válida" in secretaria.post("/secretaria/cursos/cadastrar", data=dados).get_data(as_text=True)


def test_curso_com_turma_nao_pode_ser_excluido(app, secretaria):
    curso_id, _ = criar_curso_e_turma(app)
    html = secretaria.post(f"/secretaria/cursos/excluir/{curso_id}", follow_redirects=True).get_data(as_text=True)
    assert "possui turmas vinculadas" in html


# ---- Turmas ----------------------------------------------------------------

def test_turma_duplicada_e_recusada(app, secretaria):
    curso_id, turma_id = criar_curso_e_turma(app)
    dados = {"nome": "t1", "ano": "2026", "turno": "Noturno", "curso_id": str(curso_id)}

    html = secretaria.post("/secretaria/turmas/cadastrar", data=dados, follow_redirects=True).get_data(as_text=True)
    assert "Já existe a turma" in html

    secretaria.post("/secretaria/turmas/cadastrar", data=dict(dados, nome="T2"))
    with app.app_context():
        t2 = Turma.query.filter_by(nome="T2").one().id

    html = secretaria.post(f"/secretaria/turmas/editar/{t2}", data=dict(dados, nome="T1", status="Ativa"),
                           follow_redirects=True).get_data(as_text=True)
    assert "Já existe a turma" in html

    html = secretaria.post(f"/secretaria/turmas/editar/{t2}", data=dict(dados, nome="T2", status="Ativa"),
                           follow_redirects=True).get_data(as_text=True)
    assert "Turma atualizada com sucesso!" in html


def test_nome_da_turma_longo(app, secretaria):
    curso_id, _ = criar_curso_e_turma(app)
    dados = {"nome": "N" * 120, "ano": "2026", "turno": "Noturno", "curso_id": str(curso_id)}
    assert "no máximo 100" in secretaria.post("/secretaria/turmas/cadastrar", data=dados).get_data(as_text=True)


def test_rotulo_do_cadastro_de_turma(app, secretaria):
    criar_curso_e_turma(app)
    assert "Nome da turma" in secretaria.get("/secretaria/turmas/cadastrar").get_data(as_text=True)


# ---- Alunos ----------------------------------------------------------------

def test_lista_de_alunos_paginada_com_busca(secretaria, escola):
    from tests.conftest import linhas

    html = secretaria.get("/secretaria/alunos/").get_data(as_text=True)
    assert linhas(html) == 20 and "de 601" in html

    html = secretaria.get("/secretaria/alunos/?busca=z%40x.com").get_data(as_text=True)
    assert "Zuleica Prado" in html and linhas(html) == 1
    assert "Editar" in html and "Excluir" in html


def test_exclusao_de_aluno(app, secretaria):
    _, turma_id = criar_curso_e_turma(app)
    aluno_id = criar_aluno(app)
    with app.app_context():
        matricula = Matricula(aluno_id=aluno_id, turma_id=turma_id, data_matricula=date.today(), status="Ativa")
        db.session.add(matricula)
        db.session.commit()
        matricula_id = matricula.id

    html = secretaria.post(f"/secretaria/alunos/excluir/{aluno_id}", follow_redirects=True).get_data(as_text=True)
    assert "possui matrícula ativa" in html

    secretaria.post(f"/secretaria/matriculas/cancelar/{matricula_id}")
    with app.app_context():
        db.session.add(Nota(avaliacao="P1", valor=8, data=date.today(), matricula_id=matricula_id))
        db.session.add(Frequencia(data=date.today(), status="Presente", matricula_id=matricula_id))
        db.session.commit()

    html = secretaria.post(f"/secretaria/alunos/excluir/{aluno_id}", follow_redirects=True).get_data(as_text=True)
    assert "Aluno excluído com sucesso!" in html
    with app.app_context():
        assert db.session.get(Aluno, aluno_id) is None
        assert Matricula.query.count() == Nota.query.count() == Frequencia.query.count() == 0


# ---- Matrículas ------------------------------------------------------------

def test_busca_de_alunos_para_matricula(secretaria, escola):
    assert [a["nome"] for a in secretaria.get("/secretaria/alunos/buscar?q=zul").get_json()] == ["Zuleica Prado"]
    assert secretaria.get("/secretaria/alunos/buscar?q=987.654").get_json()[0]["cpf"] == "987.654.321-00"
    assert len(secretaria.get("/secretaria/alunos/buscar?q=Aluno").get_json()) == 10
    assert secretaria.get("/secretaria/alunos/buscar?q=a").get_json() == []
    assert secretaria.get("/secretaria/alunos/buscar?q=xyzxyz").get_json() == []


def test_cadastro_de_matricula(secretaria, escola):
    html = secretaria.get("/secretaria/matriculas/cadastrar").get_data(as_text=True)
    assert "Aluno 599" not in html and 'id="busca-aluno"' in html

    turma = escola["turma_2026_c"]
    html = secretaria.post("/secretaria/matriculas/cadastrar",
                           data={"aluno_id": "", "turma_id": turma}).get_data(as_text=True)
    assert "Selecione o aluno e a turma." in html and f'value="{turma}" selected' in html

    html = secretaria.post("/secretaria/matriculas/cadastrar",
                           data={"aluno_id": "99999999999999999999", "turma_id": turma}).get_data(as_text=True)
    assert "Selecione o aluno e a turma." in html

    r = secretaria.post("/secretaria/matriculas/cadastrar", data={"aluno_id": escola["zuleica"], "turma_id": turma},
                        follow_redirects=True)
    assert "Matrícula realizada com sucesso!" in r.get_data(as_text=True)

    html = secretaria.post("/secretaria/matriculas/cadastrar",
                           data={"aluno_id": escola["zuleica"], "turma_id": turma}).get_data(as_text=True)
    assert "já possui matrícula ativa" in html and "Zuleica Prado" in html


def test_lista_de_matriculas(secretaria, escola):
    from tests.conftest import linhas

    ativas, canceladas = escola["ativas"], escola["canceladas"]
    html = secretaria.get("/secretaria/matriculas/").get_data(as_text=True)
    assert linhas(html) == 20 and f"de {ativas}" in html and f"Canceladas ({canceladas})" in html

    for busca in ("zuleica", "98765432100", "987.654.321-00"):
        html = secretaria.get(f"/secretaria/matriculas/?busca={busca}").get_data(as_text=True)
        assert "Zuleica Prado" in html and linhas(html) == 1, busca

    html = secretaria.get("/secretaria/matriculas/?canceladas=1&busca=Aluno+004").get_data(as_text=True)
    assert "Aluno 004" in html and linhas(html) == 1
    assert 'href="/secretaria/matriculas/?canceladas=1"' in html

    html = secretaria.get("/secretaria/matriculas/?busca=Aluno+004").get_data(as_text=True)
    assert "Nenhuma matrícula encontrada" in html

    html = secretaria.get("/secretaria/matriculas/?busca=Aluno&pagina=2").get_data(as_text=True)
    assert "busca=Aluno" in html and "pagina=3" in html


def test_cancelar_matricula(app, secretaria, escola):
    r = secretaria.post(f"/secretaria/matriculas/cancelar/{escola['matricula_zuleica']}", follow_redirects=True)
    html = r.get_data(as_text=True)
    assert "Matrícula cancelada com sucesso!" in html
    assert f"Canceladas ({escola['canceladas'] + 1})" in html
    assert "Nenhuma nota encontrada" in secretaria.get("/secretaria/notas?busca=zuleica").get_data(as_text=True)
