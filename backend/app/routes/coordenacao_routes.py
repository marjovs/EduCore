from flask import Blueprint, render_template, request
from sqlalchemy import func, select

from app import db
from app.acesso import perfil_required
from app.models.aluno import Aluno
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.routes.filtros import ler_filtros
from app.services import (
    aluno_service,
    frequencia_service,
    matricula_service,
    nota_service,
    turma_service,
)

coordenacao = Blueprint("coordenacao", __name__, url_prefix="/coordenacao")


@coordenacao.route("/painel")
@perfil_required("coordenacao")
def painel():
    # Uma única ida ao banco para os 4 indicadores (cada consulta ao Neon
    # custa uma viagem de rede).
    totais = db.session.execute(
        select(
            select(func.count(Aluno.id)).scalar_subquery(),
            select(func.count(Matricula.id))
            .where(Matricula.status == "Ativa").scalar_subquery(),
            select(func.count(Nota.id)).scalar_subquery(),
            select(func.count(Frequencia.id)).scalar_subquery(),
        )
    ).one()

    return render_template(
        "coordenacao/painel.html",
        total_alunos=totais[0],
        total_matriculas=totais[1],
        total_notas=totais[2],
        total_frequencias=totais[3]
    )


STATUS_MATRICULA = ("Ativa", "Cancelada")


def _opcoes_de_filtro():
    return {
        "turmas": turma_service.listar_turmas_para_filtro(),
        "anos": matricula_service.listar_anos_das_turmas(),
    }


@coordenacao.route("/alunos")
@perfil_required("coordenacao")
def alunos():
    filtros = ler_filtros()

    return render_template(
        "coordenacao/alunos.html",
        pagina=aluno_service.buscar_alunos_com_matriculas_ativas(
            busca=filtros["busca"], pagina=filtros["pagina"]
        ),
        filtros=filtros,
    )


@coordenacao.route("/matriculas")
@perfil_required("coordenacao")
def matriculas():
    filtros = ler_filtros()
    status = request.args.get("status")
    filtros["status"] = status if status in STATUS_MATRICULA else ""

    return render_template(
        "coordenacao/matriculas.html",
        pagina=matricula_service.buscar_matriculas(
            status=filtros["status"] or None,
            busca=filtros["busca"],
            ano=filtros["ano"],
            pagina=filtros["pagina"],
        ),
        filtros=filtros,
        anos=matricula_service.listar_anos_das_turmas(),
        status_opcoes=STATUS_MATRICULA,
    )


@coordenacao.route("/desempenho")
@perfil_required("coordenacao")
def desempenho():
    filtros = ler_filtros()
    pagina, resumo = nota_service.buscar_notas(**filtros)

    return render_template(
        "coordenacao/desempenho.html",
        pagina=pagina,
        resumo=resumo,
        filtros=filtros,
        **_opcoes_de_filtro(),
    )


@coordenacao.route("/frequencia")
@perfil_required("coordenacao")
def frequencia():
    filtros = ler_filtros()
    pagina, resumo = frequencia_service.buscar_frequencias(**filtros)

    return render_template(
        "coordenacao/frequencia.html",
        pagina=pagina,
        resumo=resumo,
        filtros=filtros,
        **_opcoes_de_filtro(),
    )
