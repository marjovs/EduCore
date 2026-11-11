from app import db
from app.acesso import PERFIS
from app.models.usuario import Usuario
from app.services import RegraNegocioError, obter_ou_404
from app.validacao import email_valido

TAMANHO_MINIMO_SENHA = 8


def listar_usuarios():
    return Usuario.query.order_by(Usuario.perfil, Usuario.email).all()


def buscar_usuario(usuario_id):
    return obter_ou_404(Usuario, usuario_id)


def buscar_por_email(email):
    return Usuario.query.filter_by(email=(email or "").strip().lower()).first()


def validar_senha(senha, confirmacao):
    if len(senha or "") < TAMANHO_MINIMO_SENHA:
        raise RegraNegocioError(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
    if len(senha) > 128:
        raise RegraNegocioError("A senha aceita no máximo 128 caracteres.")
    if senha != confirmacao:
        raise RegraNegocioError("A confirmação não é igual à senha.")


def cadastrar_usuario(email, perfil, senha, confirmacao):
    email = (email or "").strip().lower()

    if not email_valido(email) or len(email) > 120:
        raise RegraNegocioError("Informe um e-mail válido.")
    if perfil not in PERFIS:
        raise RegraNegocioError("Perfil inválido.")
    if buscar_por_email(email):
        raise RegraNegocioError("Já existe um usuário com este e-mail.")
    validar_senha(senha, confirmacao)

    usuario = Usuario(email=email, perfil=perfil)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def redefinir_senha(usuario, senha, confirmacao):
    validar_senha(senha, confirmacao)
    usuario.definir_senha(senha)
    db.session.commit()


def trocar_propria_senha(usuario, senha_atual, senha, confirmacao):
    if not usuario.verificar_senha(senha_atual):
        raise RegraNegocioError("A senha atual está incorreta.")
    validar_senha(senha, confirmacao)
    usuario.definir_senha(senha)
    db.session.commit()


def excluir_usuario(usuario, email_logado):
    if usuario.email == email_logado:
        raise RegraNegocioError("Você não pode excluir o seu próprio usuário.")

    if usuario.perfil == "coordenacao" and Usuario.query.filter_by(perfil="coordenacao").count() <= 1:
        raise RegraNegocioError("O sistema precisa de pelo menos um usuário da coordenação.")

    db.session.delete(usuario)
    db.session.commit()
