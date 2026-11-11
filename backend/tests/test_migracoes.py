from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from flask_migrate import downgrade, upgrade
from sqlalchemy import text

from app import db


def test_migracoes_criam_exatamente_as_tabelas_dos_models(app):
    """Se este teste falhar, algum model mudou sem uma migração nova.
    Rode, na pasta backend:  flask --app run db migrate -m "descrição da mudança"
    """
    with app.app_context():
        db.drop_all()
        try:
            upgrade()
            with db.engine.connect() as conexao:
                diferencas = compare_metadata(MigrationContext.configure(conexao), db.metadata)
            assert diferencas == []

            downgrade(revision="base")
        finally:
            with db.engine.begin() as conexao:
                conexao.execute(text("DROP TABLE IF EXISTS alembic_version"))
            db.create_all()
