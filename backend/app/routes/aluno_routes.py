from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import datetime

from app.services import aluno_service


alunos = Blueprint("alunos", __name__, url_prefix="/secretaria/alunos")


def secretaria_required():
    return (
        "usuario" in session
        and session.get("perfil") == "secretaria"
    )


@alunos.route("/")
def listar():
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    lista_alunos = aluno_service.listar_alunos()

    return render_template(
        "secretaria/alunos/listar.html",
        alunos=lista_alunos
    )


@alunos.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        nascimento = request.form.get("data_nascimento", "")

        if not all([nome, email, cpf, nascimento]):
            flash("Preencha todos os campos obrigatórios.")
            return render_template("secretaria/alunos/cadastrar.html")

        try:
            data_nascimento = datetime.strptime(
                nascimento, "%Y-%m-%d"
            ).date()
        except ValueError:
            flash("Data de nascimento inválida.")
            return render_template("secretaria/alunos/cadastrar.html")

        dados = {
            "nome": nome,
            "email": email,
            "cpf": cpf,
            "telefone": telefone or None,
            "data_nascimento": data_nascimento
        }

        try:
            aluno_service.cadastrar_aluno(dados)
        except Exception:
            from app import db
            db.session.rollback()
            flash("Erro ao cadastrar aluno. Verifique os dados.")
            return render_template("secretaria/alunos/cadastrar.html")

        flash("Aluno cadastrado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return render_template("secretaria/alunos/cadastrar.html")


@alunos.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    aluno = aluno_service.buscar_aluno(id)

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        cpf = request.form.get("cpf", "").strip()
        telefone = request.form.get("telefone", "").strip()
        nascimento = request.form.get("data_nascimento", "")

        if not all([nome, email, cpf, nascimento]):
            flash("Preencha todos os campos obrigatórios.")
            return render_template(
                "secretaria/alunos/editar.html",
                aluno=aluno
            )

        try:
            data_nascimento = datetime.strptime(
                nascimento, "%Y-%m-%d"
            ).date()
        except ValueError:
            flash("Data de nascimento inválida.")
            return render_template(
                "secretaria/alunos/editar.html",
                aluno=aluno
            )

        dados = {
            "nome": nome,
            "email": email,
            "cpf": cpf,
            "telefone": telefone or None,
            "data_nascimento": data_nascimento
        }

        try:
            aluno_service.atualizar_aluno(aluno, dados)
        except Exception:
            from app import db
            db.session.rollback()
            flash("Erro ao atualizar aluno. Verifique os dados.")
            return render_template(
                "secretaria/alunos/editar.html",
                aluno=aluno
            )

        flash("Aluno atualizado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return render_template(
        "secretaria/alunos/editar.html",
        aluno=aluno
    )


@alunos.route("/excluir/<int:id>", methods=["POST"])
def excluir(id):
    if not secretaria_required():
        return redirect(url_for("auth.login"))

    aluno = aluno_service.buscar_aluno(id)

    try:
        aluno_service.excluir_aluno(aluno)
    except Exception:
        from app import db
        db.session.rollback()
        flash("Não foi possível excluir o aluno.")
        return redirect(url_for("alunos.listar"))

    flash("Aluno excluído com sucesso!")
    return redirect(url_for("alunos.listar"))