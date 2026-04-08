"""add image_data to inspections

Revision ID: c4e2f1a8b3d6
Revises: 8b7c1a2d9e3f
Create Date: 2026-04-08 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e2f1a8b3d6"
down_revision: Union[str, Sequence[str], None] = "8b7c1a2d9e3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("inspections", sa.Column("image_data", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("inspections", "image_data")
