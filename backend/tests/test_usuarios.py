from app import db
from app.models.usuario import Usuario
from tests.conftest import SENHAS


def novo(coordenacao, **campos):
    dados = {"email": "Nova@EduCore.com", "perfil": "instrutor",
             "senha": "senha-forte-1", "confirmacao": "senha-forte-1"}
    dados.update(campos)
    return coordenacao.post("/coordenacao/usuarios/cadastrar", data=dados, follow_redirects=True).get_data(as_text=True)


def test_coordenacao_cadastra_usuario_que_consegue_entrar(app, coordenacao, cliente):
    html = novo(coordenacao)
    assert "Usuário cadastrado com sucesso!" in html and "nova@educore.com" in html

    r = cliente.post("/", data={"email": "nova@educore.com", "senha": "senha-forte-1"})
    assert r.headers["Location"].endswith("/dashboard")


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
    with app.app_context():
        usuario_id = Usuario.query.filter_by(perfil="instrutor").one().id

    html = coordenacao.post(f"/coordenacao/usuarios/senha/{usuario_id}",
                            data={"senha": "nova-senha-123", "confirmacao": "nova-senha-123"},
                            follow_redirects=True).get_data(as_text=True)
    assert "redefinida com sucesso" in html

    r = cliente.post("/", data={"email": "instrutor@educore.com", "senha": "nova-senha-123"})
    assert r.headers["Location"].endswith("/dashboard")


def test_excluir_usuario_encerra_o_acesso(app, coordenacao, instrutor):
    assert instrutor.get("/instrutor/painel").status_code == 200

    with app.app_context():
        usuario_id = Usuario.query.filter_by(perfil="instrutor").one().id
    html = coordenacao.post(f"/coordenacao/usuarios/excluir/{usuario_id}", follow_redirects=True).get_data(as_text=True)
    assert "Usuário excluído com sucesso!" in html

    r = instrutor.get("/instrutor/painel")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")


def test_nao_exclui_a_si_mesmo_nem_a_ultima_coordenacao(app, coordenacao):
    with app.app_context():
        proprio = Usuario.query.filter_by(perfil="coordenacao").one().id
    html = coordenacao.post(f"/coordenacao/usuarios/excluir/{proprio}", follow_redirects=True).get_data(as_text=True)
    assert "seu próprio usuário" in html

    # outra coordenação tenta excluir a única coordenação restante
    novo(coordenacao, email="coord2@educore.com", perfil="coordenacao")
    with app.app_context():
        db.session.delete(db.session.get(Usuario, proprio))
        db.session.commit()
        unica = Usuario.query.filter_by(perfil="coordenacao").one()
        unica_id = unica.id
    c2 = coordenacao.application.test_client()
    with c2.session_transaction() as s:
        s["usuario"], s["perfil"] = "outra@educore.com", "coordenacao"
    with app.app_context():
        db.session.add(Usuario(email="outra@educore.com", perfil="secretaria", senha_hash="x"))
        db.session.commit()
    # sessão com perfil diferente do banco é encerrada
    assert c2.post(f"/coordenacao/usuarios/excluir/{unica_id}").status_code == 302
    with app.app_context():
        assert db.session.get(Usuario, unica_id) is not None


def test_ultima_coordenacao_nao_pode_ser_excluida(app):
    from app.services import RegraNegocioError, usuario_service

    with app.app_context():
        unica = Usuario.query.filter_by(perfil="coordenacao").one()
        try:
            usuario_service.excluir_usuario(unica, "outra@educore.com")
            assert False, "deveria recusar"
        except RegraNegocioError as erro:
            assert "pelo menos um usuário da coordenação" in str(erro)


def test_minha_senha(secretaria, cliente):
    html = secretaria.post("/minha-senha", data={"senha_atual": "errada", "senha": "nova-senha-1",
                                                 "confirmacao": "nova-senha-1"}).get_data(as_text=True)
    assert "A senha atual está incorreta." in html

    r = secretaria.post("/minha-senha", data={"senha_atual": SENHAS["secretaria"], "senha": "nova-senha-1",
                                              "confirmacao": "nova-senha-1"}, follow_redirects=True)
    assert "Senha alterada com sucesso!" in r.get_data(as_text=True)

    r = cliente.post("/", data={"email": "secretaria@educore.com", "senha": "nova-senha-1"})
    assert r.headers["Location"].endswith("/dashboard")


def test_minha_senha_exige_login(cliente):
    assert cliente.get("/minha-senha").status_code == 302
