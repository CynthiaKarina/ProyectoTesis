"""añadir tabla audit_log

Revision ID: 20250815_add_audit_log
Revises: a44a6dbf8a82
Create Date: 2025-08-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250815_add_audit_log'
down_revision = 'a44a6dbf8a82'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('actor_id', sa.Integer(), nullable=True),
        sa.Column('target_user_id', sa.Integer(), nullable=True),
        sa.Column('from_value', sa.String(length=255), nullable=True),
        sa.Column('to_value', sa.String(length=255), nullable=True),
        sa.Column('extra', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('audit_log')


