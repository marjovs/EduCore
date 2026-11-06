from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app.acesso import PERFIS
from app.models.usuario import Usuario

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        usuario = Usuario.query.filter_by(email=email).first()

        if usuario and usuario.verificar_senha(senha):

            session.clear()
            session["usuario"] = usuario.email
            session["perfil"] = usuario.perfil

            return redirect(url_for("auth.dashboard"))

        flash("E-mail ou senha incorretos.", "danger")

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
