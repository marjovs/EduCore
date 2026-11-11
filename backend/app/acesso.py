import time
from functools import wraps

from flask import flash, redirect, session, url_for

PERFIS = ("secretaria", "instrutor", "coordenacao")

# De quanto em quanto tempo (segundos) confirmar no banco que o usuário logado
# ainda existe, está ativo e tem o mesmo perfil. Entre uma conferência e outra
# não há consulta extra: desativar alguém corta o acesso em até 1 minuto.
INTERVALO_VERIFICACAO = 60


def marcar_verificado():
    session["verificado_em"] = time.time()


def usuario_ainda_valido():
    """True se o usuário da sessão ainda pode usar o sistema.

    Consulta o banco no máximo uma vez a cada INTERVALO_VERIFICACAO segundos.
    """
    if time.time() - session.get("verificado_em", 0) < INTERVALO_VERIFICACAO:
        return True

    from app import db
    from app.models.usuario import Usuario

    valido = db.session.query(Usuario.id).filter_by(
        email=session.get("usuario"), perfil=session.get("perfil"), ativo=True
    ).first() is not None

    if valido:
        marcar_verificado()
    return valido


def _encerrar_sessao():
    session.clear()
    flash("Seu acesso foi encerrado. Entre novamente.")
    return redirect(url_for("auth.login"))


def perfil_required(perfil):
    """Exige usuário logado com o perfil informado.

    - Sem login: redireciona para a tela de login.
    - Usuário desativado, excluído ou com perfil alterado: encerra a sessão.
    - Logado com outro perfil: redireciona para o painel do próprio perfil.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("auth.login"))

            if not usuario_ainda_valido():
                return _encerrar_sessao()

            if session.get("perfil") != perfil:
                return redirect(url_for("auth.dashboard"))

            return view(*args, **kwargs)
        return wrapper
    return decorator


def login_required(view):
    """Exige apenas estar logado (qualquer perfil)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("auth.login"))
        if not usuario_ainda_valido():
            return _encerrar_sessao()
        return view(*args, **kwargs)
    return wrapper
