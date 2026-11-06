
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date

from app import db
from app.services import nota_service, matricula_service, turma_service

notas = Blueprint(
    "notas",
    __name__,
    url_prefix="/instrutor/notas"
)


def instrutor_required():
    if "usuario" not in session:
        return redirect(url_for("auth.login"))

    if session.get("perfil") != "instrutor":
        return redirect(url_for("auth.dashboard"))

    return None


@notas.route("/")
def listar():
    acesso = instrutor_required()
    if acesso:
        return acesso

    turmas = turma_service.listar_turmas()
    turmas = [turma for turma in turmas if turma.status == "Ativa"]

    return render_template(
        "instrutor/notas/listar.html",
        turmas=turmas
    )


@notas.route("/registrar/<int:turma_id>", methods=["GET", "POST"])
def registrar(turma_id):
    acesso = instrutor_required()
    if acesso:
        return acesso

    turma = turma_service.buscar_turma(turma_id)

    if turma.status != "Ativa":
        flash("Turma não encontrada ou inativa.")
        return redirect(url_for("notas.listar"))

    todas_matriculas = matricula_service.listar_matriculas()

    matriculas = [
        matricula for matricula in todas_matriculas
        if matricula.turma_id == turma_id
        and matricula.status == "Ativa"
    ]

    if request.method == "POST":
        avaliacao = request.form.get("avaliacao", "").strip()
        data_avaliacao = request.form.get("data", "").strip()

        if not avaliacao:
            flash("Informe o nome da avaliação.")
            return render_template(
                "instrutor/notas/registrar.html",
                turma=turma,
                matriculas=matriculas,
                data_hoje=date.today().isoformat()
            )

        try:
            data_avaliacao = date.fromisoformat(data_avaliacao)
        except ValueError:
            flash("Informe uma data válida.")
            return render_template(
                "instrutor/notas/registrar.html",
                turma=turma,
                matriculas=matriculas,
                data_hoje=date.today().isoformat()
            )

        notas_validas = []

        for matricula in matriculas:
            valor = request.form.get(
                f"nota_{matricula.id}", ""
            ).strip()

            try:
                valor = float(valor.replace(",", "."))
            except ValueError:
                flash("Informe uma nota válida para todos os alunos.")
                return render_template(
                    "instrutor/notas/registrar.html",
                    turma=turma,
                    matriculas=matriculas,
                    data_hoje=date.today().isoformat()
                )

            if not 0 <= valor <= 10:
                flash("As notas devem estar entre 0 e 10.")
                return render_template(
                    "instrutor/notas/registrar.html",
                    turma=turma,
                    matriculas=matriculas,
                    data_hoje=date.today().isoformat()
                )

            notas_validas.append({
                "avaliacao": avaliacao,
                "valor": valor,
                "data": data_avaliacao,
                "matricula_id": matricula.id
            })

        try:
            for dados in notas_validas:
                nota_service.cadastrar_nota(dados)

        except Exception:
            db.session.rollback()
            flash("Erro ao registrar notas.")
            return render_template(
                "instrutor/notas/registrar.html",
                turma=turma,
                matriculas=matriculas,
                data_hoje=date.today().isoformat()
            )

        flash("Notas registradas com sucesso!")
        return redirect(url_for("notas.listar"))

    return render_template(
        "instrutor/notas/registrar.html",
        turma=turma,
        matriculas=matriculas,
        data_hoje=date.today().isoformat()
    )
