from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.acesso import perfil_required
from app.routes.acoes import executar
from app.services import curso_service
from app.validacao import inteiro_seguro, texto_grande_demais

cursos = Blueprint("cursos", __name__, url_prefix="/secretaria/cursos")

MODALIDADES = ("Presencial", "EAD", "Híbrido")
STATUS_CURSO = ("Ativo", "Inativo")


def _ler_formulario():
    """Lê e valida o formulário. Retorna (dados, erro)."""
    nome = request.form.get("nome", "").strip()
    descricao = request.form.get("descricao", "").strip()
    carga_horaria = request.form.get("carga_horaria", "")
    modalidade = request.form.get("modalidade", "")
    status = request.form.get("status", "Ativo")

    if not nome or not carga_horaria or not modalidade:
        return None, "Preencha todos os campos obrigatórios."

    erro = texto_grande_demais({"Nome do curso": (nome, 120)})
    if erro:
        return None, erro

    carga_horaria = inteiro_seguro(carga_horaria)
    if carga_horaria is None or carga_horaria > 20000:
        return None, "Informe uma carga horária válida (de 1 a 20000 horas)."

    if modalidade not in MODALIDADES:
        return None, "Modalidade inválida."

    if status not in STATUS_CURSO:
        return None, "Status inválido."

    return {
        "nome": nome,
        "descricao": descricao or None,
        "carga_horaria": carga_horaria,
        "modalidade": modalidade,
        "status": status
    }, None


@cursos.route("/")
@perfil_required("secretaria")
def listar():
    return render_template(
        "secretaria/cursos/listar.html",
        cursos=curso_service.listar_cursos()
    )


@cursos.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("secretaria")
def cadastrar():
    def tela():
        return render_template("secretaria/cursos/cadastrar.html")

    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return tela()

        falha = executar(lambda: curso_service.cadastrar_curso(dados),
                         "Erro ao cadastrar curso. Verifique os dados.", tela)
        if falha:
            return falha

        flash("Curso cadastrado com sucesso!")
        return redirect(url_for("cursos.listar"))

    return tela()


@cursos.route("/editar/<int:id>", methods=["GET", "POST"])
@perfil_required("secretaria")
def editar(id):
    curso = curso_service.buscar_curso(id)

    def tela():
        return render_template("secretaria/cursos/editar.html", curso=curso)

    if request.method == "POST":
        dados, erro = _ler_formulario()

        if erro:
            flash(erro)
            return tela()

        falha = executar(lambda: curso_service.atualizar_curso(curso, dados),
                         "Erro ao atualizar curso. Verifique os dados.", tela)
        if falha:
            return falha

        flash("Curso atualizado com sucesso!")
        return redirect(url_for("cursos.listar"))

    return tela()


@cursos.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def excluir(id):
    curso = curso_service.buscar_curso(id)

    def voltar():
        return redirect(url_for("cursos.listar"))

    falha = executar(lambda: curso_service.excluir_curso(curso), "Não foi possível excluir o curso.", voltar)
    if falha:
        return falha

    flash("Curso excluído com sucesso!")
    return voltar()
