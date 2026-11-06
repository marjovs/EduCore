from flask import Blueprint, render_template, redirect, url_for, session

instrutor = Blueprint("instrutor", __name__, url_prefix="/instrutor")


def instrutor_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "instrutor":
        return redirect(url_for("auth.dashboard"))

    return None


@instrutor.route("/painel")
def painel():
    acesso = instrutor_required()

    if acesso:
        return acesso

    return render_template("instrutor/painel.html")