from functools import wraps

from flask import redirect, session, url_for

PERFIS = ("secretaria", "instrutor", "coordenacao")


def perfil_required(perfil):
    """Exige usuário logado com o perfil informado.

    - Sem login: redireciona para a tela de login.
    - Logado com outro perfil: redireciona para o painel do próprio perfil.
    """
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if "usuario" not in session:
                return redirect(url_for("auth.login"))

            if session.get("perfil") != perfil:
                return redirect(url_for("auth.dashboard"))

            return view(*args, **kwargs)
        return wrapper
    return decorator
