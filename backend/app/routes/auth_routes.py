from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.acesso import PERFIS, login_required, marcar_verificado
from app.routes.acoes import executar
from app.services import RegraNegocioError, usuario_service

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        try:
            usuario = usuario_service.autenticar(request.form.get("email"), request.form.get("senha"))
        except RegraNegocioError as erro:
            flash(str(erro))
            return render_template("auth/login.html")

        session.clear()
        session["usuario"] = usuario.email
        session["perfil"] = usuario.perfil
        marcar_verificado()

        return redirect(url_for("auth.dashboard"))

    return render_template("auth/login.html")


@auth.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    perfil = session.get("perfil")

    if perfil not in PERFIS:
        session.clear()
        return redirect(url_for("auth.login"))

    return redirect(url_for(f"{perfil}.painel"))


@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))


@auth.route("/minha-senha", methods=["GET", "POST"])
@login_required
def minha_senha():
    """Qualquer usuário logado pode trocar a própria senha."""
    usuario = usuario_service.buscar_por_email(session["usuario"])

    def tela():
        return render_template("auth/minha_senha.html")

    if request.method == "POST":
        falha = executar(
            lambda: usuario_service.trocar_propria_senha(
                usuario, request.form.get("senha_atual"),
                request.form.get("senha"), request.form.get("confirmacao"),
            ),
            "Erro ao trocar a senha.",
            tela,
        )
        if falha:
            return falha

        flash("Senha alterada com sucesso!")
        return redirect(url_for("auth.dashboard"))

    return tela()
