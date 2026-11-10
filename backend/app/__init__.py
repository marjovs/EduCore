from flask import Flask, flash, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFError, CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static"
    )

    app.config.from_object("config.Config")

    db.init_app(app)
    csrf.init_app(app)

    # {{ aluno.cpf|cpf }} -> 111.222.333-44 (o banco guarda só os dígitos)
    from app.validacao import formatar_cpf
    app.add_template_filter(formatar_cpf, "cpf")

    @app.errorhandler(CSRFError)
    def csrf_invalido(erro):
        flash("Sua sessão expirou ou o formulário é inválido. Tente novamente.")
        return redirect(request.referrer or url_for("auth.login"))

    from app.routes.auth_routes import auth
    from app.routes.secretaria_routes import secretaria
    from app.routes.aluno_routes import alunos
    from app.routes.curso_routes import cursos
    from app.routes.turma_routes import turmas
    from app.routes.matricula_routes import matriculas
    from app.routes.frequencia_routes import frequencias
    from app.routes.nota_routes import notas
    from app.routes.coordenacao_routes import coordenacao
    from app.routes.instrutor_routes import instrutor

    app.register_blueprint(auth)
    app.register_blueprint(secretaria)
    app.register_blueprint(alunos)
    app.register_blueprint(cursos)
    app.register_blueprint(turmas)
    app.register_blueprint(matriculas)
    app.register_blueprint(frequencias)
    app.register_blueprint(notas)
    app.register_blueprint(coordenacao)
    app.register_blueprint(instrutor)

    return app
