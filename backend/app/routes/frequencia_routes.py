
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date

from app import db
from app.services import frequencia_service, matricula_service, turma_service

frequencias = Blueprint(
    "frequencias",
    __name__,
    url_prefix="/instrutor/frequencia"
)


def instrutor_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "instrutor":
        return redirect(url_for("auth.dashboard"))

    return None


@frequencias.route("/")
def listar():
    acesso = instrutor_required()
    if acesso:
        return acesso

    lista_turmas = turma_service.listar_turmas()
    lista_turmas = [
        turma for turma in lista_turmas
        if turma.status == "Ativa"
    ]

    return render_template(
        "instrutor/frequencias/listar.html",
        turmas=lista_turmas
    )


@frequencias.route("/registrar/<int:turma_id>", methods=["GET", "POST"])
def registrar(turma_id):
    acesso = instrutor_required()
    if acesso:
        return acesso

    turma = turma_service.buscar_turma(turma_id)

    if turma.status != "Ativa":
        flash("Turma não encontrada ou inativa.")
        return redirect(url_for("frequencias.listar"))

    todas_matriculas = matricula_service.listar_matriculas()

    matriculas = [
        matricula for matricula in todas_matriculas
        if matricula.turma_id == turma_id
        and matricula.status == "Ativa"
    ]

    if request.method == "POST":
        data_registro = request.form.get("data", "").strip()

        try:
            data_registro = date.fromisoformat(data_registro)
        except ValueError:
            flash("Informe uma data válida.")
            return render_template(
                "instrutor/frequencias/registrar.html",
                turma=turma,
                matriculas=matriculas,
                data_hoje=date.today().isoformat()
            )

        dados_frequencias = []

        for matricula in matriculas:
            status = request.form.get(f"status_{matricula.id}")

            if status not in ["Presente", "Falta"]:
                flash("Selecione presença ou falta para todos os alunos.")
                return render_template(
                    "instrutor/frequencias/registrar.html",
                    turma=turma,
                    matriculas=matriculas,
                    data_hoje=date.today().isoformat()
                )

            dados_frequencias.append({
                "matricula_id": matricula.id,
                "data": data_registro,
                "status": status
            })

        try:
            for dados in dados_frequencias:
                frequencia_existente = frequencia_service.buscar_frequencia_por_data(
                    dados["matricula_id"],
                    dados["data"]
                )

                if frequencia_existente:
                    frequencia_service.atualizar_frequencia(
                        frequencia_existente,
                        {"status": dados["status"]}
                    )
                else:
                    frequencia_service.registrar_frequencia(dados)

        except Exception:
            db.session.rollback()
            flash("Erro ao registrar frequências.")
            return render_template(
                "instrutor/frequencias/registrar.html",
                turma=turma,
                matriculas=matriculas,
                data_hoje=date.today().isoformat()
            )

        flash("Frequências registradas com sucesso!")
        return redirect(url_for("frequencias.listar"))

    return render_template(
        "instrutor/frequencias/registrar.html",
        turma=turma,
        matriculas=matriculas,
        data_hoje=date.today().isoformat()
    )
