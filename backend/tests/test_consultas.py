"""Consultas de notas e frequência (secretaria e coordenação) e telas do instrutor."""
import re

import pytest

from tests.conftest import linhas


@pytest.mark.parametrize("area,url_notas", [("secretaria", "/secretaria/notas"),
                                            ("coordenacao", "/coordenacao/desempenho")])
def test_notas_com_resumo_e_filtros(request, escola, area, url_notas):
    cliente = request.getfixturevalue(area)
    html = cliente.get(url_notas).get_data(as_text=True)
    assert linhas(html) == 20
    assert re.search(rf">\s*{escola['ativas']}\s*<", html)  # resumo conta todas as páginas
    assert "7.0" in html
    assert '<optgroup label="2026">' in html

    html = cliente.get(url_notas + "?busca=zuleica").get_data(as_text=True)
    assert "Zuleica Prado" in html and linhas(html) == 1


@pytest.mark.parametrize("area,url", [("secretaria", "/secretaria/frequencia"),
                                      ("coordenacao", "/coordenacao/frequencia")])
def test_frequencia_com_resumo_e_filtros(request, escola, area, url):
    cliente = request.getfixturevalue(area)
    html = cliente.get(url).get_data(as_text=True)
    assert linhas(html) == 20 and "80%" in html and "Observação" not in html
    assert re.search(rf">\s*{escola['ativas'] * 4}\s*<", html)

    html = cliente.get(url + "?busca=987654&ano=2022").get_data(as_text=True)
    assert "Zuleica Prado" in html and linhas(html) == 5
    assert linhas(cliente.get(url + "?busca=987654&ano=2026").get_data(as_text=True)) == 0

    html = cliente.get(f"{url}?turma_id={escola['turma_aluno_001']}").get_data(as_text=True)
    assert "de 150" in html  # 30 alunos x 5 dias
    # Nessa turma todos estão cancelados, menos a Zuleica: só os 5 registros dela aparecem
    html = cliente.get(f"{url}?turma_id={escola['turma_zuleica']}").get_data(as_text=True)
    assert linhas(html) == 5 and html.count("Zuleica Prado") == 5


def test_cores_por_area(secretaria, coordenacao, escola):
    assert "bg-blue-600 text-white" in secretaria.get("/secretaria/notas?pagina=2").get_data(as_text=True)
    html = coordenacao.get("/coordenacao/desempenho?pagina=2").get_data(as_text=True)
    assert "bg-purple-600 text-white" in html


def test_coordenacao_alunos(coordenacao, escola):
    html = coordenacao.get("/coordenacao/alunos").get_data(as_text=True)
    assert linhas(html) == 20 and "de 601" in html

    html = coordenacao.get("/coordenacao/alunos?busca=98765432100").get_data(as_text=True)
    assert "Zuleica Prado" in html and linhas(html) == 1

    html = coordenacao.get("/coordenacao/alunos?busca=Aluno+001").get_data(as_text=True)
    assert re.search(r"<td class=\"p-4\">\s*1\s*</td>", html)  # 1 matrícula ativa


def test_coordenacao_matriculas(coordenacao, escola):
    total = escola["ativas"] + escola["canceladas"]
    html = coordenacao.get("/coordenacao/matriculas").get_data(as_text=True)
    assert linhas(html) == 20 and f"de {total}" in html

    html = coordenacao.get("/coordenacao/matriculas?status=Cancelada").get_data(as_text=True)
    assert f"de {escola['canceladas']}" in html

    html = coordenacao.get("/coordenacao/matriculas?status=Ativa&ano=2026&busca=Turma+B").get_data(as_text=True)
    assert linhas(html) > 0 and "Cancelada" not in html.split("<tbody>")[1]

    assert coordenacao.get("/coordenacao/matriculas?status=xyz").status_code == 200


def test_textos_do_painel(secretaria, coordenacao):
    assert "Boas-vindas à Secretaria!" in secretaria.get("/secretaria/painel").get_data(as_text=True)
    html = coordenacao.get("/coordenacao/painel").get_data(as_text=True)
    assert "Total de alunos" in html and "Consultar frequência" in html


def test_instrutor_sem_turmas(instrutor):
    assert "Nenhuma turma ativa cadastrada." in instrutor.get("/instrutor/frequencia/").get_data(as_text=True)
    assert "Nenhuma turma ativa cadastrada." in instrutor.get("/instrutor/notas/").get_data(as_text=True)


def test_instrutor_lanca_frequencia_e_notas(app, instrutor):
    from datetime import date

    from app import db
    from app.models.aluno import Aluno
    from app.models.curso import Curso
    from app.models.frequencia import Frequencia
    from app.models.matricula import Matricula
    from app.models.nota import Nota
    from app.models.turma import Turma

    with app.app_context():
        curso = Curso(nome="ADS", carga_horaria=100, modalidade="EAD", status="Ativo")
        db.session.add(curso)
        db.session.flush()
        turma = Turma(nome="T1", ano=2026, turno="Noturno", status="Ativa", curso_id=curso.id)
        aluno = Aluno(nome="Ana", email="a@x.com", cpf="52998224725", data_nascimento=date(2005, 1, 1))
        db.session.add_all([turma, aluno])
        db.session.flush()
        matricula = Matricula(aluno_id=aluno.id, turma_id=turma.id, data_matricula=date.today(), status="Ativa")
        db.session.add(matricula)
        db.session.commit()
        turma_id, matricula_id = turma.id, matricula.id

    html = instrutor.get(f"/instrutor/frequencia/registrar/{turma_id}").get_data(as_text=True)
    assert "529.982.247-25" in html

    dados = {"data": "2026-03-02", f"status_{matricula_id}": "Presente"}
    r = instrutor.post(f"/instrutor/frequencia/registrar/{turma_id}", data=dados, follow_redirects=True)
    assert "Frequências registradas com sucesso!" in r.get_data(as_text=True)
    dados[f"status_{matricula_id}"] = "Falta"
    instrutor.post(f"/instrutor/frequencia/registrar/{turma_id}", data=dados)

    dados = {"avaliacao": "P1", "data": "2026-03-02", f"nota_{matricula_id}": "8,5"}
    r = instrutor.post(f"/instrutor/notas/registrar/{turma_id}", data=dados, follow_redirects=True)
    assert "Notas registradas com sucesso!" in r.get_data(as_text=True)

    url_notas = f"/instrutor/notas/registrar/{turma_id}"
    html = instrutor.post(url_notas, data=dict(dados, avaliacao="p1")).get_data(as_text=True)
    assert "já possui notas lançadas" in html

    html = instrutor.post(f"/instrutor/notas/registrar/{turma_id}",
                          data=dict(dados, avaliacao="P2", **{f"nota_{matricula_id}": "11"})).get_data(as_text=True)
    assert "entre 0 e 10" in html

    with app.app_context():
        assert Frequencia.query.one().status == "Falta"  # o segundo envio atualiza, não duplica
        assert Nota.query.one().valor == 8.5
