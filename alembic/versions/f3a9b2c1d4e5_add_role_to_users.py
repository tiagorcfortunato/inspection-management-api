"""add role to users

Revision ID: f3a9b2c1d4e5
Revises: cb036a6df90a
Create Date: 2026-03-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f3a9b2c1d4e5'
down_revision: Union[str, Sequence[str], None] = 'cb036a6df90a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('role', sa.String(), nullable=False, server_default='user'))


def downgrade() -> None:
    op.drop_column('users', 'role')
