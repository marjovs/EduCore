from flask import Blueprint, render_template

from app.acesso import perfil_required

instrutor = Blueprint("instrutor", __name__, url_prefix="/instrutor")


@instrutor.route("/painel")
@perfil_required("instrutor")
def painel():
    return render_template("instrutor/painel.html")
