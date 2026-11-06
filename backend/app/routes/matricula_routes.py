
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date

from app import db
from app.services import matricula_service, aluno_service, turma_service

matriculas = Blueprint(
    "matriculas",
    __name__,
    url_prefix="/secretaria/matriculas"
)


def secretaria_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "secretaria":
        return redirect(url_for("auth.dashboard"))

    return None


@matriculas.route("/")
def listar():
    acesso = secretaria_required()
    if acesso:
        return acesso

    lista_matriculas = matricula_service.listar_matriculas()

    return render_template(
        "secretaria/matriculas/listar.html",
        matriculas=lista_matriculas
    )


@matriculas.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    acesso = secretaria_required()
    if acesso:
        return acesso

    alunos = aluno_service.listar_alunos()

    turmas = turma_service.listar_turmas()
    turmas = [turma for turma in turmas if turma.status == "Ativa"]

    if not alunos:
        flash("Cadastre um aluno antes de realizar uma matrícula.")
        return redirect(url_for("alunos.listar"))

    if not turmas:
        flash("Cadastre uma turma ativa antes de realizar uma matrícula.")
        return redirect(url_for("turmas.listar"))

    if request.method == "POST":
        aluno_id = request.form.get("aluno_id", "").strip()
        turma_id = request.form.get("turma_id", "").strip()

        if not aluno_id or not turma_id:
            flash("Selecione o aluno e a turma.")
            return render_template(
                "secretaria/matriculas/cadastrar.html",
                alunos=alunos,
                turmas=turmas
            )

        try:
            aluno_id = int(aluno_id)
            turma_id = int(turma_id)
        except ValueError:
            flash("Aluno ou turma inválidos.")
            return render_template(
                "secretaria/matriculas/cadastrar.html",
                alunos=alunos,
                turmas=turmas
            )

        aluno = aluno_service.buscar_aluno(aluno_id)
        turma = turma_service.buscar_turma(turma_id)

        if turma.status != "Ativa":
            flash("Selecione uma turma ativa válida.")
            return render_template(
                "secretaria/matriculas/cadastrar.html",
                alunos=alunos,
                turmas=turmas
            )

        matriculas_existentes = matricula_service.listar_matriculas()

        matricula_existente = any(
            matricula.aluno_id == aluno.id
            and matricula.turma_id == turma.id
            and matricula.status == "Ativa"
            for matricula in matriculas_existentes
        )

        if matricula_existente:
            flash("Este aluno já possui matrícula ativa nesta turma.")
            return render_template(
                "secretaria/matriculas/cadastrar.html",
                alunos=alunos,
                turmas=turmas
            )

        dados = {
            "aluno_id": aluno.id,
            "turma_id": turma.id,
            "data_matricula": date.today(),
            "status": "Ativa"
        }

        try:
            matricula_service.cadastrar_matricula(dados)
        except Exception:
            db.session.rollback()
            flash("Erro ao realizar matrícula.")
            return render_template(
                "secretaria/matriculas/cadastrar.html",
                alunos=alunos,
                turmas=turmas
            )

        flash("Matrícula realizada com sucesso!")
        return redirect(url_for("matriculas.listar"))

    return render_template(
        "secretaria/matriculas/cadastrar.html",
        alunos=alunos,
        turmas=turmas
    )


@matriculas.route("/cancelar/<int:id>", methods=["POST"])
def cancelar(id):
    acesso = secretaria_required()
    if acesso:
        return acesso

    matricula = matricula_service.buscar_matricula(id)

    if matricula.status == "Cancelada":
        flash("Esta matrícula já está cancelada.")
        return redirect(url_for("matriculas.listar"))

    try:
        matricula_service.cancelar_matricula(matricula)
    except Exception:
        db.session.rollback()
        flash("Erro ao cancelar matrícula.")
        return redirect(url_for("matriculas.listar"))

    flash("Matrícula cancelada com sucesso!")
    return redirect(url_for("matriculas.listar"))
