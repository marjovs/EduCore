"""Telas de consulta de notas e frequência, compartilhadas pela secretaria e
pela coordenação (mudam só as cores e os links, definidos no template)."""
from flask import render_template

from app.routes.filtros import ler_filtros
from app.services import frequencia_service, matricula_service, nota_service, turma_service


def opcoes_de_filtro():
    """Turmas e anos para os selects de filtro."""
    return {
        "turmas": turma_service.listar_turmas_para_filtro(),
        "anos": matricula_service.listar_anos_das_turmas(),
    }


def tela_de_notas(area):
    filtros = ler_filtros()
    pagina, resumo = nota_service.buscar_notas(**filtros)
    return render_template("consultas/notas.html", area=area, pagina=pagina, resumo=resumo,
                           filtros=filtros, **opcoes_de_filtro())


def tela_de_frequencia(area):
    filtros = ler_filtros()
    pagina, resumo = frequencia_service.buscar_frequencias(**filtros)
    return render_template("consultas/frequencia.html", area=area, pagina=pagina, resumo=resumo,
                           filtros=filtros, **opcoes_de_filtro())
