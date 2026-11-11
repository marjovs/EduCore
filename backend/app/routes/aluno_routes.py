from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from app.acesso import perfil_required
from app.routes.acoes import executar
from app.routes.filtros import ler_filtros
from app.services import aluno_service
from app.validacao import (
    cpf_valido,
    data_nascimento_valida,
    email_valido,
    formatar_cpf,
    somente_digitos,
    texto_grande_demais,
)

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

    erro = texto_grande_demais({
        "Nome": (nome, 120),
        "E-mail": (email, 120),
        "Telefone": (telefone, 20),
    })
    if erro:
        return None, erro

    if not email_valido(email):
        return None, "Informe um e-mail válido."

    if not cpf_valido(cpf):
        return None, "CPF inválido. Confira os 11 dígitos."

    try:
        data_nascimento = datetime.strptime(nascimento, "%Y-%m-%d").date()
    except ValueError:
        return None, "Data de nascimento inválida."

    if not data_nascimento_valida(data_nascimento):
        return None, "A data de nascimento não pode ser no futuro nem antes de 1900."

    return {
        "nome": nome,
        "email": email,
        # Guardado só com os dígitos; a formatação é feita na tela.
        "cpf": somente_digitos(cpf),
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
        {"id": aluno.id, "nome": aluno.nome, "cpf": formatar_cpf(aluno.cpf)}
        for aluno in aluno_service.sugerir_alunos(texto)
    ])


@alunos.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("secretaria")
def cadastrar():
    def tela():
        return render_template("secretaria/alunos/cadastrar.html")

    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return tela()

        falha = executar(lambda: aluno_service.cadastrar_aluno(dados),
                         "Erro ao cadastrar aluno. Verifique os dados.", tela)
        if falha:
            return falha

        flash("Aluno cadastrado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return tela()


@alunos.route("/editar/<int:id>", methods=["GET", "POST"])
@perfil_required("secretaria")
def editar(id):
    aluno = aluno_service.buscar_aluno(id)

    def tela():
        return render_template("secretaria/alunos/editar.html", aluno=aluno)

    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return tela()

        falha = executar(lambda: aluno_service.atualizar_aluno(aluno, dados),
                         "Erro ao atualizar aluno. Verifique os dados.", tela)
        if falha:
            return falha

        flash("Aluno atualizado com sucesso!")
        return redirect(url_for("alunos.listar"))

    return tela()


@alunos.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def excluir(id):
    aluno = aluno_service.buscar_aluno(id)

    def voltar():
        return redirect(url_for("alunos.listar"))

    falha = executar(lambda: aluno_service.excluir_aluno(aluno), "Não foi possível excluir o aluno.", voltar)
    if falha:
        return falha

    flash("Aluno excluído com sucesso!")
    return voltar()
