from datetime import date

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.acesso import perfil_required
from app.services import frequencia_service, matricula_service, turma_service

frequencias = Blueprint("frequencias", __name__, url_prefix="/instrutor/frequencia")

STATUS_FREQUENCIA = ("Presente", "Falta")


@frequencias.route("/")
@perfil_required("instrutor")
def listar():
    return render_template(
        "instrutor/frequencias/listar.html",
        turmas=turma_service.listar_turmas_ativas()
    )


@frequencias.route("/registrar/<int:turma_id>", methods=["GET", "POST"])
@perfil_required("instrutor")
def registrar(turma_id):
    turma = turma_service.buscar_turma(turma_id)

    if turma.status != "Ativa":
        flash("Turma não encontrada ou inativa.")
        return redirect(url_for("frequencias.listar"))

    matriculas = matricula_service.listar_matriculas_ativas_da_turma(turma_id)

    def tela():
        return render_template(
            "instrutor/frequencias/registrar.html",
            turma=turma,
            matriculas=matriculas,
            data_hoje=date.today().isoformat()
        )

    if request.method == "POST":
        try:
            data_registro = date.fromisoformat(request.form.get("data", "").strip())
        except ValueError:
            flash("Informe uma data válida.")
            return tela()

        dados_frequencias = []

        for matricula in matriculas:
            status = request.form.get(f"status_{matricula.id}")

            if status not in STATUS_FREQUENCIA:
                flash("Selecione presença ou falta para todos os alunos.")
                return tela()

            dados_frequencias.append({
                "matricula_id": matricula.id,
                "status": status
            })

        if not dados_frequencias:
            flash("Esta turma não possui alunos com matrícula ativa.")
            return tela()

        try:
            frequencia_service.registrar_frequencias(dados_frequencias, data_registro)
        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.exception("Erro ao registrar frequências")
            flash("Erro ao registrar frequências.")
            return tela()

        flash("Frequências registradas com sucesso!")
        return redirect(url_for("frequencias.listar"))

    return tela()
