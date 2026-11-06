from flask import Blueprint, render_template, redirect, url_for, session
from app import db
from app.models.aluno import Aluno
from app.models.matricula import Matricula
from app.models.nota import Nota
from app.models.frequencia import Frequencia

coordenacao = Blueprint("coordenacao", __name__, url_prefix="/coordenacao")


def coordenacao_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "coordenacao":
        return redirect(url_for("auth.dashboard"))

    return None


@coordenacao.route("/painel")
def painel():
    acesso = coordenacao_required()
    if acesso:
        return acesso
    
    total_alunos = Aluno.query.count()
    total_matriculas = Matricula.query.filter_by(status="Ativa").count()
    total_notas = Nota.query.count()
    total_frequencias = Frequencia.query.count()

    return render_template(
        "coordenacao/painel.html", 
        total_alunos=total_alunos,
        total_matriculas=total_matriculas, 
        total_notas=total_notas, 
        total_frequencias=total_frequencias
    )


@coordenacao.route("/alunos")
def alunos():
    acesso = coordenacao_required()
    if acesso:
        return acesso
    
    lista_alunos = Aluno.query.order_by(Aluno.nome).all()

    return render_template(
        "coordenacao/alunos.html",
        alunos=lista_alunos
    )


@coordenacao.route("/matriculas")
def matriculas():
    acesso = coordenacao_required()
    if acesso:
        return acesso

    lista_matriculas = Matricula.query.order_by(
        Matricula.data_matricula.desc()
    ).all()

    return render_template(
        "coordenacao/matriculas.html",
        matriculas=lista_matriculas
    )


@coordenacao.route("/desempenho")
def desempenho():
    acesso = coordenacao_required()
    if acesso:
        return acesso

    lista_notas = Nota.query.order_by(Nota.data.desc()).all()

    return render_template(
        "coordenacao/desempenho.html",
        notas=lista_notas
    )


@coordenacao.route("/frequencia")
def frequencia():
    acesso = coordenacao_required()
    if acesso:
        return acesso

    lista_frequencias = Frequencia.query.order_by(
        Frequencia.data.desc()
        ).all()

    return render_template(
        "coordenacao/frequencia.html",
        frequencias=lista_frequencias
    )