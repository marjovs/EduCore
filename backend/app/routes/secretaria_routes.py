from flask import Blueprint, render_template

from app.acesso import perfil_required
from app.routes.filtros import ler_filtros
from app.services import frequencia_service, matricula_service, nota_service, turma_service

secretaria = Blueprint("secretaria", __name__, url_prefix="/secretaria")


def _opcoes_de_filtro():
    return {
        "turmas": turma_service.listar_turmas_para_filtro(),
        "anos": matricula_service.listar_anos_das_turmas(),
    }


@secretaria.route("/painel")
@perfil_required("secretaria")
def painel():
    return render_template("secretaria/painel.html")


@secretaria.route("/notas")
@perfil_required("secretaria")
def notas():
    filtros = ler_filtros()
    pagina, resumo = nota_service.buscar_notas(**filtros)

    return render_template(
        "secretaria/notas/listar.html",
        pagina=pagina,
        resumo=resumo,
        filtros=filtros,
        **_opcoes_de_filtro(),
    )


@secretaria.route("/frequencia")
@perfil_required("secretaria")
def frequencia():
    filtros = ler_filtros()
    pagina, resumo = frequencia_service.buscar_frequencias(**filtros)

    return render_template(
        "secretaria/frequencias/listar.html",
        pagina=pagina,
        resumo=resumo,
        filtros=filtros,
        **_opcoes_de_filtro(),
    )
