from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.acesso import perfil_required
from app.services import RegraNegocioError, curso_service, turma_service

turmas = Blueprint("turmas", __name__, url_prefix="/secretaria/turmas")

TURNOS = ("Matutino", "Vespertino", "Noturno")
STATUS_TURMA = ("Ativa", "Inativa")


def _ler_formulario(exigir_status):
    """Lê e valida o formulário. Retorna (dados, erro)."""
    nome = request.form.get("nome", "").strip()
    ano = request.form.get("ano", "").strip()
    turno = request.form.get("turno", "").strip()
    curso_id = request.form.get("curso_id", "").strip()
    status = request.form.get("status", "").strip()

    obrigatorios = [nome, ano, turno, curso_id] + ([status] if exigir_status else [])
    if not all(obrigatorios):
        return None, "Preencha todos os campos obrigatórios."

    try:
        ano = int(ano)
        curso_id = int(curso_id)
    except ValueError:
        return None, "Ano ou curso inválido."

    if ano < 2000 or ano > 2100:
        return None, "Informe um ano válido."

    if turno not in TURNOS:
        return None, "Turno inválido."

    if exigir_status and status not in STATUS_TURMA:
        return None, "Status inválido."

    dados = {"nome": nome, "ano": ano, "turno": turno, "curso_id": curso_id}
    if exigir_status:
        dados["status"] = status

    return dados, None


@turmas.route("/")
@perfil_required("secretaria")
def listar():
    return render_template(
        "secretaria/turmas/listar.html",
        turmas=turma_service.listar_turmas()
    )


@turmas.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("secretaria")
def cadastrar():
    cursos = curso_service.listar_cursos_ativos()

    if not cursos:
        flash("Cadastre um curso ativo antes de criar uma turma.")
        return redirect(url_for("cursos.listar"))

    if request.method == "POST":
        dados, erro = _ler_formulario(exigir_status=False)

        if not erro:
            curso = curso_service.buscar_curso(dados["curso_id"])
            if curso.status != "Ativo":
                erro = "Selecione um curso ativo válido."

        if erro:
            flash(erro)
            return render_template("secretaria/turmas/cadastrar.html", cursos=cursos)

        try:
            turma_service.cadastrar_turma(dados)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao cadastrar turma")
            flash("Erro ao cadastrar turma.")
            return render_template("secretaria/turmas/cadastrar.html", cursos=cursos)

        flash("Turma cadastrada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return render_template("secretaria/turmas/cadastrar.html", cursos=cursos)


@turmas.route("/editar/<int:id>", methods=["GET", "POST"])
@perfil_required("secretaria")
def editar(id):
    turma = turma_service.buscar_turma(id)

    cursos = curso_service.listar_cursos_ativos()
    if turma.curso not in cursos:
        cursos.append(turma.curso)

    if request.method == "POST":
        dados, erro = _ler_formulario(exigir_status=True)

        if not erro:
            curso = curso_service.buscar_curso(dados["curso_id"])
            # Mantém o curso atual mesmo se inativo, mas não permite trocar
            # a turma para outro curso inativo.
            if curso.id != turma.curso_id and curso.status != "Ativo":
                erro = "Selecione um curso ativo válido."

        if erro:
            flash(erro)
            return render_template("secretaria/turmas/editar.html", turma=turma, cursos=cursos)

        try:
            turma_service.atualizar_turma(turma, dados)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao atualizar turma")
            flash("Erro ao atualizar turma.")
            return render_template("secretaria/turmas/editar.html", turma=turma, cursos=cursos)

        flash("Turma atualizada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return render_template("secretaria/turmas/editar.html", turma=turma, cursos=cursos)


@turmas.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def excluir(id):
    turma = turma_service.buscar_turma(id)

    try:
        turma_service.excluir_turma(turma)
    except RegraNegocioError as e:
        flash(str(e))
        return redirect(url_for("turmas.listar"))
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Erro ao excluir turma")
        flash("Não foi possível excluir a turma.")
        return redirect(url_for("turmas.listar"))

    flash("Turma excluída com sucesso!")
    return redirect(url_for("turmas.listar"))
