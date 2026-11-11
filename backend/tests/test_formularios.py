"""Formulários voltam preenchidos quando há erro."""
from datetime import date

from app import db
from app.models.aluno import Aluno
from app.models.curso import Curso
from app.models.turma import Turma


def test_cadastro_de_aluno_com_erro_mantem_os_dados(secretaria):
    dados = {"nome": "Maria da Silva", "email": "maria@x.com", "cpf": "123", "telefone": "11 99999-0000",
             "data_nascimento": "2004-05-06"}
    html = secretaria.post("/secretaria/alunos/cadastrar", data=dados).get_data(as_text=True)
    assert "CPF inválido" in html
    for valor in ('value="Maria da Silva"', 'value="maria@x.com"', 'value="123"',
                  'value="11 99999-0000"', 'value="2004-05-06"'):
        assert valor in html, valor


def test_cadastro_de_aluno_vazio_na_primeira_vez(secretaria):
    html = secretaria.get("/secretaria/alunos/cadastrar").get_data(as_text=True)
    assert 'name="nome" required maxlength="120" value=""' in html


def test_edicao_de_aluno_mostra_dados_salvos_e_depois_o_digitado(app, secretaria):
    with app.app_context():
        aluno = Aluno(nome="Ana", email="ana@x.com", cpf="52998224725", data_nascimento=date(2005, 1, 1))
        db.session.add(aluno)
        db.session.commit()
        aluno_id = aluno.id

    html = secretaria.get(f"/secretaria/alunos/editar/{aluno_id}").get_data(as_text=True)
    assert 'value="Ana"' in html and 'value="529.982.247-25"' in html

    dados = {"nome": "Ana Paula", "email": "nao-e-email", "cpf": "529.982.247-25", "data_nascimento": "2005-01-01"}
    html = secretaria.post(f"/secretaria/alunos/editar/{aluno_id}", data=dados).get_data(as_text=True)
    assert "Informe um e-mail válido." in html
    assert 'value="Ana Paula"' in html and 'value="nao-e-email"' in html


def test_cadastro_de_curso_com_erro_mantem_os_dados(secretaria):
    dados = {"nome": "Redes", "descricao": "Curso técnico", "carga_horaria": "0", "modalidade": "EAD",
             "status": "Inativo"}
    html = secretaria.post("/secretaria/cursos/cadastrar", data=dados).get_data(as_text=True)
    assert "carga horária válida" in html
    assert 'value="Redes"' in html and ">Curso técnico</textarea>" in html and 'value="0"' in html
    assert "<option value=\"EAD\" selected>" in html
    assert "<option value=\"Inativo\" selected>" in html


def test_turma_com_erro_mantem_os_dados(app, secretaria):
    with app.app_context():
        curso = Curso(nome="ADS", carga_horaria=100, modalidade="EAD", status="Ativo")
        db.session.add(curso)
        db.session.flush()
        db.session.add(Turma(nome="T1", ano=2026, turno="Noturno", status="Ativa", curso_id=curso.id))
        db.session.commit()
        curso_id = curso.id

    dados = {"nome": "T1", "ano": "2026", "turno": "Noturno", "curso_id": str(curso_id)}
    html = secretaria.post("/secretaria/turmas/cadastrar", data=dados).get_data(as_text=True)
    assert "Já existe a turma" in html
    assert 'value="T1"' in html and 'value="2026"' in html
    assert f'<option value="{curso_id}" selected>' in html
    assert '<option value="Noturno" selected>' in html
