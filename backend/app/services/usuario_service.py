from datetime import datetime, timedelta, timezone

from app import db
from app.acesso import PERFIS
from app.models.usuario import Usuario
from app.services import RegraNegocioError, obter_ou_404
from app.validacao import email_valido

TAMANHO_MINIMO_SENHA = 8

# Limite de tentativas de login
MAXIMO_TENTATIVAS = 5
TEMPO_DE_BLOQUEIO = timedelta(minutes=15)

MENSAGEM_LOGIN_INVALIDO = "E-mail ou senha incorretos."


def _agora():
    """Horário atual em UTC, sem fuso (como fica gravado no banco)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def listar_usuarios():
    return Usuario.query.order_by(Usuario.ativo.desc(), Usuario.perfil, Usuario.email).all()


def buscar_usuario(usuario_id):
    return obter_ou_404(Usuario, usuario_id)


def buscar_por_email(email):
    return Usuario.query.filter_by(email=(email or "").strip().lower()).first()


def esta_bloqueado(usuario):
    return bool(usuario.bloqueado_ate and usuario.bloqueado_ate > _agora())


def minutos_de_bloqueio(usuario):
    restante = usuario.bloqueado_ate - _agora()
    return max(1, -(-int(restante.total_seconds()) // 60))  # arredonda para cima


# ---- Login -------------------------------------------------------------------

def autenticar(email, senha):
    """Confere e-mail e senha aplicando o limite de tentativas.

    Retorna o usuário, se der certo, ou lança RegraNegocioError com a mensagem
    para a tela de login. Depois de MAXIMO_TENTATIVAS senhas erradas seguidas,
    a conta fica bloqueada por TEMPO_DE_BLOQUEIO.
    """
    usuario = buscar_por_email(email)

    if usuario is None:
        raise RegraNegocioError(MENSAGEM_LOGIN_INVALIDO)

    if esta_bloqueado(usuario):
        raise RegraNegocioError(
            f"Muitas tentativas com senha errada. Tente de novo em {minutos_de_bloqueio(usuario)} minuto(s) "
            "ou peça à coordenação para redefinir sua senha."
        )

    if not usuario.verificar_senha(senha):
        usuario.tentativas_falhas += 1
        if usuario.tentativas_falhas >= MAXIMO_TENTATIVAS:
            usuario.tentativas_falhas = 0
            usuario.bloqueado_ate = _agora() + TEMPO_DE_BLOQUEIO
        db.session.commit()
        raise RegraNegocioError(MENSAGEM_LOGIN_INVALIDO)

    if not usuario.ativo:
        raise RegraNegocioError("Este usuário está desativado. Procure a coordenação.")

    if usuario.tentativas_falhas or usuario.bloqueado_ate:
        usuario.tentativas_falhas = 0
        usuario.bloqueado_ate = None
        db.session.commit()

    return usuario


# ---- Senhas ------------------------------------------------------------------

def validar_senha(senha, confirmacao):
    if len(senha or "") < TAMANHO_MINIMO_SENHA:
        raise RegraNegocioError(f"A senha precisa ter pelo menos {TAMANHO_MINIMO_SENHA} caracteres.")
    if len(senha) > 128:
        raise RegraNegocioError("A senha aceita no máximo 128 caracteres.")
    if senha != confirmacao:
        raise RegraNegocioError("A confirmação não é igual à senha.")


def redefinir_senha(usuario, senha, confirmacao):
    """Feito pela coordenação. Também libera um usuário bloqueado por tentativas."""
    validar_senha(senha, confirmacao)
    usuario.definir_senha(senha)
    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    db.session.commit()


def trocar_propria_senha(usuario, senha_atual, senha, confirmacao):
    if not usuario.verificar_senha(senha_atual):
        raise RegraNegocioError("A senha atual está incorreta.")
    validar_senha(senha, confirmacao)
    usuario.definir_senha(senha)
    db.session.commit()


# ---- Cadastro e situação -----------------------------------------------------

def cadastrar_usuario(email, perfil, senha, confirmacao):
    email = (email or "").strip().lower()

    if not email_valido(email) or len(email) > 120:
        raise RegraNegocioError("Informe um e-mail válido.")
    if perfil not in PERFIS:
        raise RegraNegocioError("Perfil inválido.")
    if buscar_por_email(email):
        raise RegraNegocioError("Já existe um usuário com este e-mail.")
    validar_senha(senha, confirmacao)

    usuario = Usuario(email=email, perfil=perfil, ativo=True, tentativas_falhas=0)
    usuario.definir_senha(senha)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def desativar_usuario(usuario, email_logado):
    if usuario.email == email_logado:
        raise RegraNegocioError("Você não pode desativar o seu próprio usuário.")

    if usuario.perfil == "coordenacao":
        coordenacoes_ativas = Usuario.query.filter_by(perfil="coordenacao", ativo=True).count()
        if coordenacoes_ativas <= 1:
            raise RegraNegocioError("O sistema precisa de pelo menos um usuário ativo da coordenação.")

    usuario.ativo = False
    db.session.commit()


def reativar_usuario(usuario):
    usuario.ativo = True
    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    db.session.commit()
