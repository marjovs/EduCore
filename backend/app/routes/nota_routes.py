from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.acesso import perfil_required
from app.services import RegraNegocioError, matricula_service, nota_service, turma_service

notas = Blueprint("notas", __name__, url_prefix="/instrutor/notas")


@notas.route("/")
@perfil_required("instrutor")
def listar():
    return render_template(
        "instrutor/notas/listar.html",
        turmas=turma_service.listar_turmas_ativas()
    )


@notas.route("/registrar/<int:turma_id>", methods=["GET", "POST"])
@perfil_required("instrutor")
def registrar(turma_id):
    turma = turma_service.buscar_turma(turma_id)

    if turma.status != "Ativa":
        flash("Turma não encontrada ou inativa.")
        return redirect(url_for("notas.listar"))

    matriculas = matricula_service.listar_matriculas_ativas_da_turma(turma_id)

    def tela():
        return render_template(
            "instrutor/notas/registrar.html",
            turma=turma,
            matriculas=matriculas,
            data_hoje=date.today().isoformat()
        )

    if request.method == "POST":
        avaliacao = request.form.get("avaliacao", "").strip()

        if not avaliacao:
            flash("Informe o nome da avaliação.")
            return tela()

        try:
            data_avaliacao = date.fromisoformat(request.form.get("data", "").strip())
        except ValueError:
            flash("Informe uma data válida.")
            return tela()

        notas_validas = []

        for matricula in matriculas:
            valor = request.form.get(f"nota_{matricula.id}", "").strip()

            try:
                valor = float(valor.replace(",", "."))
            except ValueError:
                flash("Informe uma nota válida para todos os alunos.")
                return tela()

            if not 0 <= valor <= 10:
                flash("As notas devem estar entre 0 e 10.")
                return tela()

            notas_validas.append({
                "avaliacao": avaliacao,
                "valor": valor,
                "data": data_avaliacao,
                "matricula_id": matricula.id
            })

        if not notas_validas:
            flash("Esta turma não possui alunos com matrícula ativa.")
            return tela()

        try:
            nota_service.registrar_notas(notas_validas)
        except RegraNegocioError as e:
            db.session.rollback()
            flash(str(e))
            return tela()
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao registrar notas")
            flash("Erro ao registrar notas.")
            return tela()

        flash("Notas registradas com sucesso!")
        return redirect(url_for("notas.listar"))

    return tela()
