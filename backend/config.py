import os
from pathlib import Path

from dotenv import load_dotenv

# Carrega backend/.env (independente da pasta de onde o app é executado)
load_dotenv(Path(__file__).resolve().parent / ".env")


def _normalizar_url_banco(url):
    """O Neon fornece URLs 'postgresql://' ou 'postgres://'.
    O SQLAlchemy precisa do prefixo 'postgresql+psycopg://' para usar o psycopg 3."""
    for prefixo in ("postgres://", "postgresql://"):
        if url.startswith(prefixo):
            return "postgresql+psycopg://" + url[len(prefixo):]
    return url


DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL não definida. Copie backend/.env.example para backend/.env "
        "e cole a connection string do Neon."
    )

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida no backend/.env.")


class Config:
    SECRET_KEY = SECRET_KEY

    SQLALCHEMY_DATABASE_URI = _normalizar_url_banco(DATABASE_URL)

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # O Neon suspende o banco quando fica ocioso; isso evita usar conexões "mortas".
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
