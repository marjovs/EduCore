from flask import Blueprint, render_template

from app.acesso import perfil_required

secretaria = Blueprint("secretaria", __name__, url_prefix="/secretaria")


@secretaria.route("/painel")
@perfil_required("secretaria")
def painel():
    return render_template("secretaria/painel.html")
