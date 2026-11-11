"""usuarios: ativo e limite de tentativas

Revision ID: 5dbe7077652b
Revises: 4aca4c82fab5
Create Date: 2026-11-10 21:21:17.890526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5dbe7077652b'
down_revision = '4aca4c82fab5'
branch_labels = None
depends_on = None


def upgrade():
    # Só adiciona colunas. Os usuários que já existem ficam ativos e sem bloqueio
    # (valores padrão). sa.true() vira TRUE no PostgreSQL e 1 no SQLite.
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.add_column(sa.Column('ativo', sa.Boolean(), server_default=sa.true(), nullable=False))
        batch_op.add_column(sa.Column('tentativas_falhas', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('bloqueado_ate', sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table('usuarios', schema=None) as batch_op:
        batch_op.drop_column('bloqueado_ate')
        batch_op.drop_column('tentativas_falhas')
        batch_op.drop_column('ativo')
