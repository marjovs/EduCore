
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

from app import db
from app.services import curso_service

cursos = Blueprint("cursos", __name__, url_prefix="/secretaria/cursos")


def secretaria_required():
    return (
        "usuario" in session
        and session.get("perfil") == "secretaria"
    )


@cursos.route("/")
def listar():
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    lista_cursos = curso_service.listar_cursos()

    return render_template(
        "secretaria/cursos/listar.html",
        cursos=lista_cursos
    )


@cursos.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        carga_horaria = request.form.get("carga_horaria", "")
        modalidade = request.form.get("modalidade", "")
        status = request.form.get("status", "Ativo")

        if not nome or not carga_horaria or not modalidade:
            flash("Preencha os campos obrigatórios.")
            return render_template("secretaria/cursos/cadastrar.html")

        try:
            carga_horaria = int(carga_horaria)
            if carga_horaria <= 0:
                raise ValueError
        except ValueError:
            flash("Informe uma carga horária válida.")
            return render_template("secretaria/cursos/cadastrar.html")

        dados = {
            "nome": nome,
            "descricao": descricao or None,
            "carga_horaria": carga_horaria,
            "modalidade": modalidade,
            "status": status
        }

        try:
            curso_service.cadastrar_curso(dados)
        except Exception:
            db.session.rollback()
            flash("Erro ao cadastrar curso. Verifique os dados.")
            return render_template("secretaria/cursos/cadastrar.html")

        flash("Curso cadastrado com sucesso!")
        return redirect(url_for("cursos.listar"))

    return render_template("secretaria/cursos/cadastrar.html")


@cursos.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    curso = curso_service.buscar_curso(id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        descricao = request.form.get("descricao", "").strip()
        carga_horaria = request.form.get("carga_horaria", "")
        modalidade = request.form.get("modalidade", "")
        status = request.form.get("status", "Ativo")

        if not nome or not carga_horaria or not modalidade:
            flash("Preencha os campos obrigatórios.")
            return render_template(
                "secretaria/cursos/editar.html",
                curso=curso
            )

        try:
            carga_horaria = int(carga_horaria)
            if carga_horaria <= 0:
                raise ValueError
        except ValueError:
            flash("Informe uma carga horária válida.")
            return render_template(
                "secretaria/cursos/editar.html",
                curso=curso
            )

        dados = {
            "nome": nome,
            "descricao": descricao or None,
            "carga_horaria": carga_horaria,
            "modalidade": modalidade,
            "status": status
        }

        try:
            curso_service.atualizar_curso(curso, dados)
        except Exception:
            db.session.rollback()
            flash("Erro ao atualizar curso. Verifique os dados.")
            return render_template(
                "secretaria/cursos/editar.html",
                curso=curso
            )

        flash("Curso atualizado com sucesso!")
        return redirect(url_for("cursos.listar"))

    return render_template(
        "secretaria/cursos/editar.html",
        curso=curso
    )


@cursos.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    curso = curso_service.buscar_curso(id)

    try:
        curso_service.excluir_curso(curso)
    except Exception:
        db.session.rollback()
        flash("Não foi possível excluir o curso.")
        return redirect(url_for("cursos.listar"))

    flash("Curso excluído com sucesso!")
    return redirect(url_for("cursos.listar"))
