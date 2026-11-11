from functools import wraps

from flask import flash, redirect, session, url_for

PERFIS = ("secretaria", "instrutor", "coordenacao")


def usuario_ainda_valido():
    """Confere no banco se o usuário da sessão ainda existe com o mesmo perfil.

    Assim, excluir um usuário (ou mudar o perfil dele no banco) encerra o
    acesso de quem já estava logado.
    """
    from app import db
    from app.models.usuario import Usuario

    return db.session.query(Usuario.id).filter_by(
        email=session.get("usuario"), perfil=session.get("perfil")
    ).first() is not None


def perfil_required(perfil):
    """Exige usuário logado com o perfil informado.

    - Sem login (ou usuário excluído): redireciona para a tela de login.
    - Logado com outro perfil: redireciona para o painel do próprio perfil.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("auth.login"))

            if not usuario_ainda_valido():
                session.clear()
                flash("Seu acesso foi encerrado. Entre novamente.")
                return redirect(url_for("auth.login"))

            if session.get("perfil") != perfil:
                return redirect(url_for("auth.dashboard"))

            return view(*args, **kwargs)
        return wrapper
    return decorator


def login_required(view):
    """Exige apenas estar logado (qualquer perfil)."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "usuario" not in session or not usuario_ainda_valido():
            session.clear()
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapper
