from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.acesso import perfil_required
from app.services import aluno_service, matricula_service, turma_service

matriculas = Blueprint("matriculas", __name__, url_prefix="/secretaria/matriculas")


@matriculas.route("/")
@perfil_required("secretaria")
def listar():
    return render_template(
        "secretaria/matriculas/listar.html",
        matriculas=matricula_service.listar_matriculas()
    )


@matriculas.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("secretaria")
def cadastrar():
    alunos = aluno_service.listar_alunos()
    turmas = turma_service.listar_turmas_ativas()

    if not alunos:
        flash("Cadastre um aluno antes de realizar uma matrícula.")
        return redirect(url_for("alunos.listar"))

    if not turmas:
        flash("Cadastre uma turma ativa antes de realizar uma matrícula.")
        return redirect(url_for("turmas.listar"))

    def tela():
        return render_template(
            "secretaria/matriculas/cadastrar.html",
            alunos=alunos,
            turmas=turmas
        )

    if request.method == "POST":
        try:
            aluno_id = int(request.form.get("aluno_id", "").strip())
            turma_id = int(request.form.get("turma_id", "").strip())
        except ValueError:
            flash("Selecione o aluno e a turma.")
            return tela()

        aluno = aluno_service.buscar_aluno(aluno_id)
        turma = turma_service.buscar_turma(turma_id)

        if turma.status != "Ativa":
            flash("Selecione uma turma ativa válida.")
            return tela()

        if matricula_service.existe_matricula_ativa(aluno.id, turma.id):
            flash("Este aluno já possui matrícula ativa nesta turma.")
            return tela()

        try:
            matricula_service.cadastrar_matricula({
                "aluno_id": aluno.id,
                "turma_id": turma.id,
                "data_matricula": date.today(),
                "status": "Ativa"
            })
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao realizar matrícula")
            flash("Erro ao realizar matrícula.")
            return tela()

        flash("Matrícula realizada com sucesso!")
        return redirect(url_for("matriculas.listar"))

    return tela()


@matriculas.route("/cancelar/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def cancelar(id):
    matricula = matricula_service.buscar_matricula(id)

    if matricula.status == "Cancelada":
        flash("Esta matrícula já está cancelada.")
        return redirect(url_for("matriculas.listar"))

    try:
        matricula_service.cancelar_matricula(matricula)
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Erro ao cancelar matrícula")
        flash("Erro ao cancelar matrícula.")
        return redirect(url_for("matriculas.listar"))

    flash("Matrícula cancelada com sucesso!")
    return redirect(url_for("matriculas.listar"))
