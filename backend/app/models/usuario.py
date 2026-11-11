from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), nullable=False)

    # Usuário desativado não consegue entrar (em vez de ser excluído).
    ativo = db.Column(db.Boolean, nullable=False, default=True, server_default=db.true())

    # Limite de tentativas de login: após várias senhas erradas seguidas, o
    # usuário fica bloqueado até "bloqueado_ate" (horário UTC).
    tentativas_falhas = db.Column(db.Integer, nullable=False, default=0, server_default="0")
    bloqueado_ate = db.Column(db.DateTime)

    def definir_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha or "")
