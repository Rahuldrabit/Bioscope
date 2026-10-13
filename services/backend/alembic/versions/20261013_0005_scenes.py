"""Create persisted validated scene specifications.

Revision ID: 20261013_0005
Revises: 20261013_0004
Create Date: 2026-10-13 00:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0005"
down_revision: str | None = "20261013_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "scenes",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("kind", sa.String(length=48), nullable=False),
        sa.Column("spec_json", sa.Text(), nullable=False),
        sa.Column("approval_status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_scenes_run_id", "scenes", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_scenes_run_id", table_name="scenes")
    op.drop_table("scenes")
