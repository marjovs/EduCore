from datetime import timedelta

from app import db
from app.models.usuario import Usuario
from app.services import usuario_service
from tests.conftest import SENHAS


def novo(coordenacao, **campos):
    dados = {"email": "Nova@EduCore.com", "perfil": "instrutor",
             "senha": "senha-forte-1", "confirmacao": "senha-forte-1"}
    dados.update(campos)
    return coordenacao.post("/coordenacao/usuarios/cadastrar", data=dados, follow_redirects=True).get_data(as_text=True)


def entrar(cliente, email, senha):
    return cliente.post("/", data={"email": email, "senha": senha})


def id_do(app, perfil):
    with app.app_context():
        return Usuario.query.filter_by(perfil=perfil).one().id


def expirar_verificacao(cliente):
    """Simula que já passou o intervalo de conferência do acesso."""
    with cliente.session_transaction() as sessao:
        sessao["verificado_em"] = 0


# ---- Cadastro e senhas -------------------------------------------------------

def test_coordenacao_cadastra_usuario_que_consegue_entrar(coordenacao, cliente):
    html = novo(coordenacao)
    assert "Usuário cadastrado com sucesso!" in html and "nova@educore.com" in html
    assert entrar(cliente, "nova@educore.com", "senha-forte-1").headers["Location"].endswith("/dashboard")


def test_validacoes_do_cadastro(coordenacao):
    assert "pelo menos 8" in novo(coordenacao, senha="curta", confirmacao="curta")
    assert "confirmação não é igual" in novo(coordenacao, confirmacao="outra-senha")
    assert "Perfil inválido." in novo(coordenacao, perfil="admin")
    assert "Informe um e-mail válido." in novo(coordenacao, email="sem-arroba")
    assert "Já existe um usuário com este e-mail." in novo(coordenacao, email="SECRETARIA@educore.com")


def test_cadastro_com_erro_mantem_email_e_perfil(coordenacao):
    html = novo(coordenacao, senha="curta", confirmacao="curta")
    assert 'value="Nova@EduCore.com"' in html and 'value="instrutor" selected' in html


def test_redefinir_senha(app, coordenacao, cliente):
    html = coordenacao.post(f"/coordenacao/usuarios/senha/{id_do(app, 'instrutor')}",
                            data={"senha": "nova-senha-123", "confirmacao": "nova-senha-123"},
                            follow_redirects=True).get_data(as_text=True)
    assert "redefinida com sucesso" in html
    assert entrar(cliente, "instrutor@educore.com", "nova-senha-123").headers["Location"].endswith("/dashboard")


def test_minha_senha(secretaria, cliente):
    html = secretaria.post("/minha-senha", data={"senha_atual": "errada", "senha": "nova-senha-1",
                                                 "confirmacao": "nova-senha-1"}).get_data(as_text=True)
    assert "A senha atual está incorreta." in html

    r = secretaria.post("/minha-senha", data={"senha_atual": SENHAS["secretaria"], "senha": "nova-senha-1",
                                              "confirmacao": "nova-senha-1"}, follow_redirects=True)
    assert "Senha alterada com sucesso!" in r.get_data(as_text=True)
    assert entrar(cliente, "secretaria@educore.com", "nova-senha-1").headers["Location"].endswith("/dashboard")


def test_minha_senha_exige_login(cliente):
    assert cliente.get("/minha-senha").status_code == 302


# ---- Desativar e reativar ----------------------------------------------------

def test_desativar_impede_login_e_encerra_o_acesso(app, coordenacao, instrutor, cliente):
    assert instrutor.get("/instrutor/painel").status_code == 200

    instrutor_id = id_do(app, "instrutor")
    html = coordenacao.post(f"/coordenacao/usuarios/desativar/{instrutor_id}",
                            follow_redirects=True).get_data(as_text=True)
    assert "desativado com sucesso" in html and "Desativado" in html

    # Quem estava logado perde o acesso na próxima conferência (até 1 minuto)
    expirar_verificacao(instrutor)
    r = instrutor.get("/instrutor/painel")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")

    html = entrar(cliente, "instrutor@educore.com", SENHAS["instrutor"]).get_data(as_text=True)
    assert "Este usuário está desativado" in html

    html = coordenacao.post(f"/coordenacao/usuarios/reativar/{instrutor_id}",
                            follow_redirects=True).get_data(as_text=True)
    assert "reativado com sucesso" in html
    assert entrar(cliente, "instrutor@educore.com", SENHAS["instrutor"]).headers["Location"].endswith("/dashboard")


def test_nao_desativa_a_si_mesmo(app, coordenacao):
    html = coordenacao.post(f"/coordenacao/usuarios/desativar/{id_do(app, 'coordenacao')}",
                            follow_redirects=True).get_data(as_text=True)
    assert "seu próprio usuário" in html


def test_nao_desativa_a_ultima_coordenacao_ativa(app):
    from app.services import RegraNegocioError

    with app.app_context():
        unica = Usuario.query.filter_by(perfil="coordenacao").one()
        try:
            usuario_service.desativar_usuario(unica, "outra@educore.com")
            assert False, "deveria recusar"
        except RegraNegocioError as erro:
            assert "pelo menos um usuário ativo da coordenação" in str(erro)


# ---- Conferência de acesso ---------------------------------------------------

def test_acesso_e_conferido_no_maximo_uma_vez_por_minuto(app, instrutor):
    from sqlalchemy import event

    assert instrutor.get("/instrutor/painel").status_code == 200  # confere e marca

    consultas = []
    with app.app_context():
        def contar(conn, cursor, sql, *args):
            if "FROM usuarios" in sql:
                consultas.append(sql)
        event.listen(db.engine, "before_cursor_execute", contar)
        try:
            for _ in range(3):
                assert instrutor.get("/instrutor/notas/").status_code == 200
            assert consultas == []  # dentro do intervalo, nenhuma consulta extra

            expirar_verificacao(instrutor)
            assert instrutor.get("/instrutor/notas/").status_code == 200
            assert len(consultas) == 1
        finally:
            event.remove(db.engine, "before_cursor_execute", contar)


def test_perfil_alterado_no_banco_encerra_a_sessao(app, instrutor):
    with app.app_context():
        Usuario.query.filter_by(perfil="instrutor").one().perfil = "secretaria"
        db.session.commit()
    expirar_verificacao(instrutor)
    assert instrutor.get("/instrutor/painel").status_code == 302


# ---- Limite de tentativas ----------------------------------------------------

def test_bloqueia_apos_5_senhas_erradas(app, cliente):
    for _ in range(4):
        assert "E-mail ou senha incorretos." in entrar(cliente, "secretaria@educore.com", "x").get_data(as_text=True)

    html = entrar(cliente, "secretaria@educore.com", "x").get_data(as_text=True)  # 5ª: bloqueia
    assert "E-mail ou senha incorretos." in html

    html = entrar(cliente, "secretaria@educore.com", SENHAS["secretaria"]).get_data(as_text=True)
    assert "Muitas tentativas" in html and "15 minuto" in html  # nem a senha certa entra


def test_senha_certa_zera_as_tentativas(app, cliente):
    for _ in range(4):
        entrar(cliente, "secretaria@educore.com", "x")
    assert entrar(cliente, "secretaria@educore.com", SENHAS["secretaria"]).status_code == 302
    with app.app_context():
        assert Usuario.query.filter_by(perfil="secretaria").one().tentativas_falhas == 0
    for _ in range(4):
        entrar(cliente, "secretaria@educore.com", "x")
    assert entrar(cliente, "secretaria@educore.com", SENHAS["secretaria"]).status_code == 302


def test_bloqueio_expira_e_redefinir_senha_libera(app, coordenacao, cliente):
    for _ in range(5):
        entrar(cliente, "instrutor@educore.com", "x")

    html = coordenacao.get("/coordenacao/usuarios/").get_data(as_text=True)
    assert "Bloqueado" in html

    with app.app_context():  # simula que os 15 minutos passaram
        usuario = Usuario.query.filter_by(perfil="instrutor").one()
        usuario.bloqueado_ate -= timedelta(minutes=16)
        db.session.commit()
    assert entrar(cliente, "instrutor@educore.com", SENHAS["instrutor"]).status_code == 302

    for _ in range(5):
        entrar(cliente, "instrutor@educore.com", "x")
    coordenacao.post(f"/coordenacao/usuarios/senha/{id_do(app, 'instrutor')}",
                     data={"senha": "nova-senha-123", "confirmacao": "nova-senha-123"})
    assert entrar(cliente, "instrutor@educore.com", "nova-senha-123").status_code == 302


def test_email_inexistente_responde_igual(cliente):
    html = entrar(cliente, "ninguem@educore.com", "x").get_data(as_text=True)
    assert "E-mail ou senha incorretos." in html
