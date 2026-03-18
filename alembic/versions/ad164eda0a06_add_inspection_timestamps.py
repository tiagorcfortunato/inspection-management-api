"""add inspection timestamps

Revision ID: ad164eda0a06
Revises: f1d210e1fe25
Create Date: 2026-03-18 22:39:52.633272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ad164eda0a06"
down_revision: Union[str, Sequence[str], None] = "f1d210e1fe25"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("inspections", sa.Column("created_at", sa.DateTime(), nullable=True))
    op.add_column("inspections", sa.Column("updated_at", sa.DateTime(), nullable=True))

    op.execute(
        """
        UPDATE inspections
        SET created_at = reported_at,
            updated_at = reported_at
        WHERE created_at IS NULL
           OR updated_at IS NULL
        """
    )

    op.alter_column("inspections", "created_at", nullable=False)
    op.alter_column("inspections", "updated_at", nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("inspections", "updated_at")
    op.drop_column("inspections", "created_at")