from datetime import datetime

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.acesso import perfil_required
from app.routes.filtros import ler_filtros
from app.services import RegraNegocioError, aluno_service

alunos = Blueprint("alunos", __name__, url_prefix="/secretaria/alunos")


def _ler_formulario():
    """Lê e valida o formulário. Retorna (dados, erro)."""
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip()
    cpf = request.form.get("cpf", "").strip()
    telefone = request.form.get("telefone", "").strip()
    nascimento = request.form.get("data_nascimento", "")

    if not all([nome, email, cpf, nascimento]):
        return None, "Preencha todos os campos obrigatórios."

    try:
        data_nascimento = datetime.strptime(nascimento, "%Y-%m-%d").date()
    except ValueError:
        return None, "Data de nascimento inválida."

    return {
        "nome": nome,
        "email": email,
        "cpf": cpf,
        "telefone": telefone or None,
        "data_nascimento": data_nascimento
    }, None


@alunos.route("/")
@perfil_required("secretaria")
def listar():
    filtros = ler_filtros()

    return render_template(
        "secretaria/alunos/listar.html",
        pagina=aluno_service.buscar_alunos_com_matriculas_ativas(
            busca=filtros["busca"], pagina=filtros["pagina"]
        ),
        filtros=filtros
    )


@alunos.route("/buscar")
@perfil_required("secretaria")
def buscar():
    """Sugestões para o campo de aluno (ex.: cadastro de matrícula). ?q= nome ou CPF."""
    texto = request.args.get("q", "").strip()[:100]

    if len(texto) < 2:
        return jsonify([])

    return jsonify([
        {"id": aluno.id, "nome": aluno.nome, "cpf": aluno.cpf}
        for aluno in aluno_service.sugerir_alunos(texto)
    ])


@alunos.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("secretaria")
def cadastrar():
    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return render_template("secretaria/alunos/cadastrar.html")

        try:
            aluno_service.cadastrar_aluno(dados)
        except RegraNegocioError as e:
            db.session.rollback()
            flash(str(e))
            return render_template("secretaria/alunos/cadastrar.html")
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao cadastrar aluno")
            flash("Erro ao cadastrar aluno. Verifique os dados.")
            return render_template("secretaria/alunos/cadastrar.html")

        flash("Aluno cadastrado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return render_template("secretaria/alunos/cadastrar.html")


@alunos.route("/editar/<int:id>", methods=["GET", "POST"])
@perfil_required("secretaria")
def editar(id):
    aluno = aluno_service.buscar_aluno(id)

    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return render_template("secretaria/alunos/editar.html", aluno=aluno)

        try:
            aluno_service.atualizar_aluno(aluno, dados)
        except RegraNegocioError as e:
            db.session.rollback()
            flash(str(e))
            return render_template("secretaria/alunos/editar.html", aluno=aluno)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao atualizar aluno")
            flash("Erro ao atualizar aluno. Verifique os dados.")
            return render_template("secretaria/alunos/editar.html", aluno=aluno)

        flash("Aluno atualizado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return render_template("secretaria/alunos/editar.html", aluno=aluno)


@alunos.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def excluir(id):
    aluno = aluno_service.buscar_aluno(id)

    try:
        aluno_service.excluir_aluno(aluno)
    except RegraNegocioError as e:
        flash(str(e))
        return redirect(url_for("alunos.listar"))
    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.exception("Erro ao excluir aluno")
        flash("Não foi possível excluir o aluno.")
        return redirect(url_for("alunos.listar"))

    flash("Aluno excluído com sucesso!")
    return redirect(url_for("alunos.listar"))
