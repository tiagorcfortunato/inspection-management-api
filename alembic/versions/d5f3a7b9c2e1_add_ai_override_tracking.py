"""add ai override tracking fields

Revision ID: d5f3a7b9c2e1
Revises: c4e2f1a8b3d6
Create Date: 2026-04-08 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5f3a7b9c2e1"
down_revision: Union[str, Sequence[str], None] = "c4e2f1a8b3d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("inspections", sa.Column("ai_damage_type", sa.String(), nullable=True))
    op.add_column("inspections", sa.Column("ai_severity", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("inspections", "ai_severity")
    op.drop_column("inspections", "ai_damage_type")
