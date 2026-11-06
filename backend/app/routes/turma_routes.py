
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.services import turma_service, curso_service

turmas = Blueprint(
    "turmas",
    __name__,
    url_prefix="/secretaria/turmas"
)


def secretaria_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "secretaria":
        return redirect(url_for("auth.dashboard"))

    return None


@turmas.route("/")
def listar():
    acesso = secretaria_required()
    if acesso:
        return acesso

    lista_turmas = turma_service.listar_turmas()

    return render_template(
        "secretaria/turmas/listar.html",
        turmas=lista_turmas
    )


@turmas.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    acesso = secretaria_required()
    if acesso:
        return acesso

    cursos = curso_service.listar_cursos()
    cursos = [curso for curso in cursos if curso.status == "Ativo"]

    if not cursos:
        flash("Cadastre um curso ativo antes de criar uma turma.")
        return redirect(url_for("cursos.listar"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        ano = request.form.get("ano", "").strip()
        turno = request.form.get("turno", "").strip()
        curso_id = request.form.get("curso_id", "").strip()

        if not nome or not ano or not turno or not curso_id:
            flash("Preencha todos os campos obrigatórios.")
            return render_template(
                "secretaria/turmas/cadastrar.html",
                cursos=cursos
            )

        try:
            ano = int(ano)
            curso_id = int(curso_id)
        except ValueError:
            flash("Ano ou curso inválido.")
            return render_template(
                "secretaria/turmas/cadastrar.html",
                cursos=cursos
            )

        curso = curso_service.buscar_curso(curso_id)

        if curso.status != "Ativo":
            flash("Selecione um curso ativo válido.")
            return render_template(
                "secretaria/turmas/cadastrar.html",
                cursos=cursos
            )

        if ano < 2000 or ano > 2100:
            flash("Informe um ano válido.")
            return render_template(
                "secretaria/turmas/cadastrar.html",
                cursos=cursos
            )

        dados = {
            "nome": nome,
            "ano": ano,
            "turno": turno,
            "curso_id": curso_id
        }

        try:
            turma_service.cadastrar_turma(dados)
        except Exception:
            db.session.rollback()
            flash("Erro ao cadastrar turma.")
            return render_template(
                "secretaria/turmas/cadastrar.html",
                cursos=cursos
            )

        flash("Turma cadastrada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return render_template(
        "secretaria/turmas/cadastrar.html",
        cursos=cursos
    )


@turmas.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    acesso = secretaria_required()
    if acesso:
        return acesso

    turma = turma_service.buscar_turma(id)

    cursos = curso_service.listar_cursos()
    cursos = [curso for curso in cursos if curso.status == "Ativo"]

    if turma.curso not in cursos:
        cursos.append(turma.curso)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        ano = request.form.get("ano", "").strip()
        turno = request.form.get("turno", "").strip()
        curso_id = request.form.get("curso_id", "").strip()
        status = request.form.get("status", "").strip()

        if not nome or not ano or not turno or not curso_id or not status:
            flash("Preencha todos os campos obrigatórios.")
            return render_template(
                "secretaria/turmas/editar.html",
                turma=turma,
                cursos=cursos
            )

        try:
            ano = int(ano)
            curso_id = int(curso_id)
        except ValueError:
            flash("Ano ou curso inválido.")
            return render_template(
                "secretaria/turmas/editar.html",
                turma=turma,
                cursos=cursos
            )

        curso = curso_service.buscar_curso(curso_id)

        if ano < 2000 or ano > 2100:
            flash("Informe um ano válido.")
            return render_template(
                "secretaria/turmas/editar.html",
                turma=turma,
                cursos=cursos
            )

        if status not in ["Ativa", "Inativa"]:
            flash("Status inválido.")
            return render_template(
                "secretaria/turmas/editar.html",
                turma=turma,
                cursos=cursos
            )

        dados = {
            "nome": nome,
            "ano": ano,
            "turno": turno,
            "curso_id": curso.id,
            "status": status
        }

        try:
            turma_service.atualizar_turma(turma, dados)
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar turma.")
            return render_template(
                "secretaria/turmas/editar.html",
                turma=turma,
                cursos=cursos
            )

        flash("Turma atualizada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return render_template(
        "secretaria/turmas/editar.html",
        turma=turma,
        cursos=cursos
    )


@turmas.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    acesso = secretaria_required()
    if acesso:
        return acesso

    turma = turma_service.buscar_turma(id)

    try:
        turma_service.excluir_turma(turma)
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir a turma.")
        return redirect(url_for("turmas.listar"))

    flash("Turma excluída com sucesso!")
    return redirect(url_for("turmas.listar"))
