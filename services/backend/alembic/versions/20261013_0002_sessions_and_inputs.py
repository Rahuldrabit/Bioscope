"""Create owner-scoped sessions, assets, and medicine input records.

Revision ID: 20261013_0002
Revises: 20261012_0001
Create Date: 2026-10-13 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0002"
down_revision: str | None = "20261012_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=96), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("owner_id", sa.String(length=96), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("risk_scope", sa.String(length=40), server_default="EDUCATION", nullable=False),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_owner_id", "sessions", ["owner_id"])
    op.create_table(
        "messages",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_messages_session_id", "messages", ["session_id"])
    op.create_table(
        "assets",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("owner_id", sa.String(length=96), nullable=False),
        sa.Column("original_filename", sa.String(length=160), nullable=False),
        sa.Column("mime_type", sa.String(length=100), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("sha256", sa.String(length=64), nullable=True),
        sa.Column("storage_key", sa.String(length=240), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("upload_token_hash", sa.String(length=64), nullable=True),
        sa.Column("consent_sensitive_processing", sa.Boolean(), nullable=False),
        sa.Column("retention_deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_assets_owner_id", "assets", ["owner_id"])
    op.create_index("ix_assets_session_id", "assets", ["session_id"])
    op.create_table(
        "medicine_candidates",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("asset_id", sa.String(length=64), nullable=True),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_medicine_candidates_asset_id", "medicine_candidates", ["asset_id"])
    op.create_index("ix_medicine_candidates_session_id", "medicine_candidates", ["session_id"])
    op.create_table(
        "confirmed_medications",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("session_id", sa.String(length=64), nullable=False),
        sa.Column("candidate_id", sa.String(length=64), nullable=True),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("ingredients", sa.Text(), nullable=False),
        sa.Column("confirmed_by", sa.String(length=96), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["medicine_candidates.id"]),
        sa.ForeignKeyConstraint(["confirmed_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_confirmed_medications_session_id", "confirmed_medications", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_confirmed_medications_session_id", table_name="confirmed_medications")
    op.drop_table("confirmed_medications")
    op.drop_index("ix_medicine_candidates_session_id", table_name="medicine_candidates")
    op.drop_index("ix_medicine_candidates_asset_id", table_name="medicine_candidates")
    op.drop_table("medicine_candidates")
    op.drop_index("ix_assets_session_id", table_name="assets")
    op.drop_index("ix_assets_owner_id", table_name="assets")
    op.drop_table("assets")
    op.drop_index("ix_messages_session_id", table_name="messages")
    op.drop_table("messages")
    op.drop_index("ix_sessions_owner_id", table_name="sessions")
    op.drop_table("sessions")
    op.drop_table("users")
