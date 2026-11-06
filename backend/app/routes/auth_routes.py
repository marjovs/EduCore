
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

auth = Blueprint("auth", __name__)

USUARIOS = {
    "secretaria@educore.com": {
        "senha": "012345",
        "perfil": "secretaria"
    },
    "instrutor@educore.com": {
        "senha": "123456",
        "perfil": "instrutor"
    },
    "coordenacao@educore.com": {
        "senha": "234567",
        "perfil": "coordenacao"
    }
}


@auth.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = USUARIOS.get(email)

        if usuario and usuario["senha"] == senha:

            session["usuario"] = email
            session["perfil"] = usuario["perfil"]

            return redirect(url_for("auth.dashboard"))

        else:
            flash("E-mail ou senha incorretos.", "danger")

    return render_template("auth/login.html")


@auth.route("/dashboard")
def dashboard():

    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    perfil = session["perfil"]

    return redirect(url_for(f"{perfil}.painel"))


@auth.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))
