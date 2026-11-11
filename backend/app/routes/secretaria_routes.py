from flask import Blueprint, render_template

from app.acesso import perfil_required
from app.routes.consultas import tela_de_frequencia, tela_de_notas

secretaria = Blueprint("secretaria", __name__, url_prefix="/secretaria")


@secretaria.route("/painel")
@perfil_required("secretaria")
def painel():
    return render_template("secretaria/painel.html")


@secretaria.route("/notas")
@perfil_required("secretaria")
def notas():
    return tela_de_notas("secretaria")


@secretaria.route("/frequencia")
@perfil_required("secretaria")
def frequencia():
    return tela_de_frequencia("secretaria")
