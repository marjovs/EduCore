from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.acesso import perfil_required
from app.routes.acoes import executar
from app.services import curso_service, turma_service
from app.validacao import inteiro_seguro, texto_grande_demais

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

    ano = inteiro_seguro(ano)
    curso_id = inteiro_seguro(curso_id)
    if ano is None or curso_id is None:
        return None, "Ano ou curso inválido."

    if ano < 2000 or ano > 2100:
        return None, "Informe um ano válido."

    erro = texto_grande_demais({"Nome da turma": (nome, 100)})
    if erro:
        return None, erro

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

    def tela():
        return render_template("secretaria/turmas/cadastrar.html", cursos=cursos)

    if request.method == "POST":
        dados, erro = _ler_formulario(exigir_status=False)

        if not erro:
            curso = curso_service.buscar_curso(dados["curso_id"])
            if curso.status != "Ativo":
                erro = "Selecione um curso ativo válido."

        if erro:
            flash(erro)
            return tela()

        falha = executar(lambda: turma_service.cadastrar_turma(dados), "Erro ao cadastrar turma.", tela)
        if falha:
            return falha

        flash("Turma cadastrada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return tela()


@turmas.route("/editar/<int:id>", methods=["GET", "POST"])
@perfil_required("secretaria")
def editar(id):
    turma = turma_service.buscar_turma(id)

    cursos = curso_service.listar_cursos_ativos()
    if turma.curso not in cursos:
        cursos.append(turma.curso)

    def tela():
        return render_template("secretaria/turmas/editar.html", turma=turma, cursos=cursos)

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
            return tela()

        falha = executar(lambda: turma_service.atualizar_turma(turma, dados), "Erro ao atualizar turma.", tela)
        if falha:
            return falha

        flash("Turma atualizada com sucesso!")
        return redirect(url_for("turmas.listar"))

    return tela()


@turmas.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("secretaria")
def excluir(id):
    turma = turma_service.buscar_turma(id)

    def voltar():
        return redirect(url_for("turmas.listar"))

    falha = executar(lambda: turma_service.excluir_turma(turma), "Não foi possível excluir a turma.", voltar)
    if falha:
        return falha

    flash("Turma excluída com sucesso!")
    return voltar()
