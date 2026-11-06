from flask import Blueprint, render_template, session, redirect, url_for

secretaria = Blueprint("secretaria", __name__, url_prefix="/secretaria")

@secretaria.route("/painel")
def painel():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "secretaria":
        return redirect(url_for("auth.dashboard"))

    return render_template("secretaria/painel.html")