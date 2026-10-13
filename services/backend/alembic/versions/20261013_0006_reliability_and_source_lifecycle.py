"""Add reliability reports and explicit source lifecycle state.

Revision ID: 20261013_0006
Revises: 20261013_0005
Create Date: 2026-10-13 00:45:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0006"
down_revision: str | None = "20261013_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "sources",
        sa.Column("status", sa.String(length=32), server_default="ACTIVE", nullable=False),
    )
    op.create_table(
        "reliability_reports",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("schema_version", sa.String(length=20), nullable=False),
        sa.Column("assessment_mode", sa.String(length=48), nullable=False),
        sa.Column("dimensions_json", sa.Text(), nullable=False),
        sa.Column("claim_assessments_json", sa.Text(), nullable=False),
        sa.Column("unsupported_claim_ids_json", sa.Text(), nullable=False),
        sa.Column("critical_gaps_json", sa.Text(), nullable=False),
        sa.Column("overall_probability", sa.String(length=20), nullable=True),
        sa.Column("calibration_model_version", sa.String(length=80), nullable=True),
        sa.Column("disclaimer", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["workflow_runs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_reliability_reports_run_id", "reliability_reports", ["run_id"])


def downgrade() -> None:
    op.drop_index("ix_reliability_reports_run_id", table_name="reliability_reports")
    op.drop_table("reliability_reports")
    op.drop_column("sources", "status")
