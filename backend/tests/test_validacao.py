from datetime import date

import pytest

from app.validacao import cpf_valido, formatar_cpf, inteiro_seguro


@pytest.mark.parametrize("cpf", ["529.982.247-25", "52998224725", "111.444.777-35"])
def test_cpf_valido(cpf):
    assert cpf_valido(cpf)


@pytest.mark.parametrize("cpf", ["529.982.247-24", "111.111.111-11", "abc", "123", ""])
def test_cpf_invalido(cpf):
    assert not cpf_valido(cpf)


def test_formatar_cpf():
    assert formatar_cpf("52998224725") == "529.982.247-25"
    assert formatar_cpf("123") == "123"


@pytest.mark.parametrize("texto,esperado", [
    ("12", 12), ("0", None), ("-1", None), ("abc", None), ("", None), (None, None),
    ("99999999999999999999", None), ("2147483647", 2147483647), ("2147483648", None),
])
def test_inteiro_seguro(texto, esperado):
    assert inteiro_seguro(texto) == esperado


def cadastrar(cliente, **campos):
    dados = {"nome": "Teste", "email": "t@x.com", "cpf": "39053344705",
             "data_nascimento": "2005-01-01", "telefone": ""}
    dados.update(campos)
    return cliente.post("/secretaria/alunos/cadastrar", data=dados, follow_redirects=True).get_data(as_text=True)


def test_cpf_salvo_so_com_digitos_e_exibido_formatado(app, secretaria):
    from app.models.aluno import Aluno

    html = cadastrar(secretaria, cpf="529.982.247-25", email="ana@x.com")
    assert "529.982.247-25" in html
    with app.app_context():
        assert Aluno.query.filter_by(email="ana@x.com").one().cpf == "52998224725"


def test_cpf_duplicado_com_e_sem_pontuacao(app, secretaria):
    from app import db
    from app.models.aluno import Aluno

    with app.app_context():  # registro antigo salvo com pontuação
        db.session.add(Aluno(nome="Legado", email="l@x.com", cpf="111.444.777-35", data_nascimento=date(2000, 1, 1)))
        db.session.commit()

    assert "Já existe um aluno com este CPF." in cadastrar(secretaria, cpf="11144477735")
    cadastrar(secretaria, cpf="529.982.247-25", email="ana@x.com")
    assert "Já existe um aluno com este CPF." in cadastrar(secretaria, cpf="52998224725", email="b@x.com")


@pytest.mark.parametrize("campos,mensagem", [
    ({"cpf": "abc"}, "CPF inválido"),
    ({"email": "nao-e-email"}, "Informe um e-mail válido."),
    ({"data_nascimento": "2099-01-01"}, "não pode ser no futuro"),
    ({"nome": "X" * 130}, "no máximo 120"),
    ({"telefone": "9" * 25}, "no máximo 20"),
    ({"nome": ""}, "Preencha todos os campos obrigatórios."),
])
def test_validacoes_do_aluno(secretaria, campos, mensagem):
    assert mensagem in cadastrar(secretaria, **campos)


def test_email_duplicado_ignora_maiusculas(secretaria):
    cadastrar(secretaria, email="ana@x.com")
    assert "Já existe um aluno com este e-mail." in cadastrar(secretaria, email="ANA@X.com", cpf="52998224725")


@pytest.mark.parametrize("url", [
    "/secretaria/alunos/?pagina=99999999999999999999",
    "/secretaria/matriculas/?ano=99999999999999999999",
    "/secretaria/notas?turma_id=99999999999999999999",
    "/coordenacao/matriculas?pagina=abc",
])
def test_numeros_gigantes_na_url_nao_quebram(secretaria, coordenacao, url):
    cliente = coordenacao if url.startswith("/coordenacao") else secretaria
    assert cliente.get(url).status_code == 200


@pytest.mark.parametrize("url", ["/secretaria/alunos/editar/99999999999999999999",
                                 "/secretaria/turmas/editar/99999999999999999999",
                                 "/secretaria/cursos/editar/0"])
def test_ids_invalidos_dao_404(secretaria, url):
    assert secretaria.get(url).status_code == 404
