import os
import sys

from sqlalchemy import inspect

from app import db
from app.models.usuario import Usuario

# Usuários iniciais, criados apenas se a tabela "usuarios" estiver vazia.
# As senhas vêm do .env; os valores padrão existem só para desenvolvimento.
USUARIOS_INICIAIS = [
    ("secretaria@educore.com", "secretaria", "SENHA_SECRETARIA", "012345"),
    ("instrutor@educore.com", "instrutor", "SENHA_INSTRUTOR", "123456"),
    ("coordenacao@educore.com", "coordenacao", "SENHA_COORDENACAO", "234567"),
]


def criar_usuarios_iniciais():
    if Usuario.query.first():
        return

    for email, perfil, variavel, senha_padrao in USUARIOS_INICIAIS:
        usuario = Usuario(email=email, perfil=perfil)
        usuario.definir_senha(os.getenv(variavel) or senha_padrao)
        db.session.add(usuario)

    db.session.commit()
    print("Usuários iniciais criados.")


def inicializar_banco(app):
    """Confere se o banco já tem as tabelas e cria os usuários iniciais.

    As tabelas são criadas e alteradas pelas migrações (Flask-Migrate), não
    mais pelo create_all(). Num banco novo, rode antes, na pasta backend:
        flask --app run db upgrade
    """
    with app.app_context():
        if not inspect(db.engine).has_table("usuarios"):
            print(
                "\nO banco ainda não tem as tabelas do EduCore.\n"
                "Na pasta backend, rode:  flask --app run db upgrade\n"
                "e depois inicie o sistema de novo.\n",
                file=sys.stderr,
            )
            sys.exit(1)

        criar_usuarios_iniciais()
        print("Banco de dados EduCore inicializado com sucesso!")
