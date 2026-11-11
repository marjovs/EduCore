"""Usuários do sistema: a coordenação cadastra, redefine senhas e exclui."""
from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.acesso import PERFIS, perfil_required
from app.routes.acoes import executar
from app.services import usuario_service

usuarios = Blueprint("usuarios", __name__, url_prefix="/coordenacao/usuarios")

NOMES_PERFIS = {"secretaria": "Secretaria", "instrutor": "Instrutor", "coordenacao": "Coordenação"}


@usuarios.route("/")
@perfil_required("coordenacao")
def listar():
    return render_template("coordenacao/usuarios/listar.html", usuarios=usuario_service.listar_usuarios(),
                           nomes_perfis=NOMES_PERFIS)


@usuarios.route("/cadastrar", methods=["GET", "POST"])
@perfil_required("coordenacao")
def cadastrar():
    def tela():
        return render_template("coordenacao/usuarios/cadastrar.html", perfis=PERFIS, nomes_perfis=NOMES_PERFIS,
                               email=request.form.get("email", ""), perfil=request.form.get("perfil", ""))

    if request.method == "POST":
        falha = executar(
            lambda: usuario_service.cadastrar_usuario(
                request.form.get("email"), request.form.get("perfil"),
                request.form.get("senha"), request.form.get("confirmacao"),
            ),
            "Erro ao cadastrar usuário.",
            tela,
        )
        if falha:
            return falha

        flash("Usuário cadastrado com sucesso!")
        return redirect(url_for("usuarios.listar"))

    return tela()


@usuarios.route("/senha/<int:id>", methods=["GET", "POST"])
@perfil_required("coordenacao")
def redefinir_senha(id):
    usuario = usuario_service.buscar_usuario(id)

    def tela():
        return render_template("coordenacao/usuarios/senha.html", usuario=usuario)

    if request.method == "POST":
        falha = executar(
            lambda: usuario_service.redefinir_senha(usuario, request.form.get("senha"),
                                                    request.form.get("confirmacao")),
            "Erro ao redefinir a senha.",
            tela,
        )
        if falha:
            return falha

        flash(f"Senha de {usuario.email} redefinida com sucesso!")
        return redirect(url_for("usuarios.listar"))

    return tela()


@usuarios.route("/excluir/<int:id>", methods=["POST"])
@perfil_required("coordenacao")
def excluir(id):
    usuario = usuario_service.buscar_usuario(id)

    def voltar():
        return redirect(url_for("usuarios.listar"))

    falha = executar(lambda: usuario_service.excluir_usuario(usuario, session.get("usuario")),
                     "Não foi possível excluir o usuário.", voltar)
    if falha:
        return falha

    flash("Usuário excluído com sucesso!")
    return voltar()
