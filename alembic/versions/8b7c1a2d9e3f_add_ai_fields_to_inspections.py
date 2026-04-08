"""add ai fields to inspections

Revision ID: 8b7c1a2d9e3f
Revises: f3a9b2c1d4e5
Create Date: 2026-04-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8b7c1a2d9e3f"
down_revision: Union[str, Sequence[str], None] = "f3a9b2c1d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("inspections", sa.Column("ai_rationale", sa.String(), nullable=True))
    op.add_column(
        "inspections",
        sa.Column("is_ai_processed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )


def downgrade() -> None:
    op.drop_column("inspections", "is_ai_processed")
    op.drop_column("inspections", "ai_rationale")

