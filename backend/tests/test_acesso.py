import pytest

from tests.conftest import SENHAS


def test_login_com_senha_correta_vai_para_o_painel(cliente):
    r = cliente.post("/", data={"email": "Secretaria@EduCore.com", "senha": SENHAS["secretaria"]})
    assert r.status_code == 302
    assert r.headers["Location"].endswith("/dashboard")
    assert cliente.get("/dashboard").headers["Location"].endswith("/secretaria/painel")


def test_login_com_senha_errada(cliente):
    html = cliente.post("/", data={"email": "secretaria@educore.com", "senha": "x"}).get_data(as_text=True)
    assert "E-mail ou senha incorretos." in html


def test_titulo_da_tela_de_login(cliente):
    assert "EduCore | Entrar" in cliente.get("/").get_data(as_text=True)


@pytest.mark.parametrize("url", ["/secretaria/painel", "/coordenacao/painel", "/instrutor/painel"])
def test_paginas_exigem_login(cliente, url):
    r = cliente.get(url)
    assert r.status_code == 302 and r.headers["Location"].endswith("/")


@pytest.mark.parametrize("url", ["/secretaria/notas", "/secretaria/alunos/", "/secretaria/alunos/buscar?q=ab"])
def test_coordenacao_nao_entra_na_secretaria(coordenacao, url):
    assert coordenacao.get(url).status_code == 302


@pytest.mark.parametrize("url", ["/coordenacao/alunos", "/coordenacao/usuarios/"])
def test_secretaria_nao_entra_na_coordenacao(secretaria, url):
    assert secretaria.get(url).status_code == 302


def test_csrf_invalido_mostra_mensagem(app):
    app.config["WTF_CSRF_ENABLED"] = True
    try:
        c = app.test_client()
        r = c.post("/", data={"email": "a", "senha": "b"}, headers={"Referer": "/"}, follow_redirects=True)
        assert "Sua sessão expirou" in r.get_data(as_text=True)
    finally:
        app.config["WTF_CSRF_ENABLED"] = False


def test_todas_as_paginas_abrem(secretaria, coordenacao, instrutor):
    paginas = {
        secretaria: ["/secretaria/painel", "/secretaria/alunos/", "/secretaria/alunos/cadastrar",
                     "/secretaria/cursos/", "/secretaria/cursos/cadastrar", "/secretaria/turmas/",
                     "/secretaria/matriculas/", "/secretaria/notas", "/secretaria/frequencia",
                     "/minha-senha"],
        coordenacao: ["/coordenacao/painel", "/coordenacao/alunos", "/coordenacao/matriculas",
                      "/coordenacao/desempenho", "/coordenacao/frequencia", "/coordenacao/usuarios/"],
        instrutor: ["/instrutor/painel", "/instrutor/frequencia/", "/instrutor/notas/"],
    }
    for cliente, urls in paginas.items():
        for url in urls:
            r = cliente.get(url)
            assert r.status_code in (200, 302), url
            if r.status_code == 200:
                html = r.get_data(as_text=True)
                assert "_tema" not in html  # include resolvido
                assert "tema-escuro.css" in html, f"{url} sem o tema"
                assert "data-alternar-tema" in html, f"{url} sem o botão de tema"
