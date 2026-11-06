from flask import Blueprint, render_template
from sqlalchemy import func, select

from app import db
from app.acesso import perfil_required
from app.models.aluno import Aluno
from app.models.frequencia import Frequencia
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.services import aluno_service, frequencia_service, matricula_service, nota_service

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


@coordenacao.route("/alunos")
@perfil_required("coordenacao")
def alunos():
    return render_template(
        "coordenacao/alunos.html",
        alunos=aluno_service.listar_alunos()
    )


@coordenacao.route("/matriculas")
@perfil_required("coordenacao")
def matriculas():
    return render_template(
        "coordenacao/matriculas.html",
        matriculas=matricula_service.listar_matriculas()
    )


@coordenacao.route("/desempenho")
@perfil_required("coordenacao")
def desempenho():
    return render_template(
        "coordenacao/desempenho.html",
        notas=nota_service.listar_notas()
    )


@coordenacao.route("/frequencia")
@perfil_required("coordenacao")
def frequencia():
    return render_template(
        "coordenacao/frequencia.html",
        frequencias=frequencia_service.listar_frequencias()
    )
