"""Create canonical entities, immutable evidence provenance, and outbox.

Revision ID: 20261013_0003
Revises: 20261013_0002
Create Date: 2026-10-13 00:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20261013_0003"
down_revision: str | None = "20261013_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "canonical_entities",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("entity_type", sa.String(length=40), nullable=False),
        sa.Column("label", sa.String(length=240), nullable=False),
        sa.Column("organism", sa.String(length=120), nullable=False),
        sa.Column("normalizer_version", sa.String(length=40), nullable=False),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "entity_xrefs",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.String(length=64), nullable=False),
        sa.Column("source_namespace", sa.String(length=64), nullable=False),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column("mapping_status", sa.String(length=32), nullable=False),
        sa.Column("mapping_version", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["entity_id"], ["canonical_entities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_entity_xrefs_entity_id", "entity_xrefs", ["entity_id"])
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("provider", sa.String(length=80), nullable=False),
        sa.Column("stable_url", sa.Text(), nullable=False),
        sa.Column("citation", sa.Text(), nullable=False),
        sa.Column("license_policy", sa.String(length=160), nullable=False),
        sa.Column("source_type", sa.String(length=40), nullable=False),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "source_snapshots",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("source_id", sa.String(length=64), nullable=False),
        sa.Column("release_version", sa.String(length=100), nullable=False),
        sa.Column("retrieved_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("record_json", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_source_snapshots_source_id", "source_snapshots", ["source_id"])
    op.create_table(
        "claims",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("subject_entity_id", sa.String(length=64), nullable=False),
        sa.Column("predicate", sa.String(length=64), nullable=False),
        sa.Column("object_entity_id", sa.String(length=64), nullable=False),
        sa.Column("context_json", sa.Text(), nullable=False),
        sa.Column("assertion_type", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("provenance", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["object_entity_id"], ["canonical_entities.id"]),
        sa.ForeignKeyConstraint(["subject_entity_id"], ["canonical_entities.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "claim_evidence",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("claim_id", sa.String(length=64), nullable=False),
        sa.Column("source_snapshot_id", sa.String(length=64), nullable=False),
        sa.Column("evidence_direction", sa.String(length=32), nullable=False),
        sa.Column("location_pointer", sa.String(length=240), nullable=False),
        sa.Column("directness", sa.String(length=32), nullable=False),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.ForeignKeyConstraint(["claim_id"], ["claims.id"]),
        sa.ForeignKeyConstraint(["source_snapshot_id"], ["source_snapshots.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_claim_evidence_claim_id", "claim_evidence", ["claim_id"])
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_outbox_events_aggregate_id", "outbox_events", ["aggregate_id"])


def downgrade() -> None:
    op.drop_index("ix_outbox_events_aggregate_id", table_name="outbox_events")
    op.drop_table("outbox_events")
    op.drop_index("ix_claim_evidence_claim_id", table_name="claim_evidence")
    op.drop_table("claim_evidence")
    op.drop_table("claims")
    op.drop_index("ix_source_snapshots_source_id", table_name="source_snapshots")
    op.drop_table("source_snapshots")
    op.drop_table("sources")
    op.drop_index("ix_entity_xrefs_entity_id", table_name="entity_xrefs")
    op.drop_table("entity_xrefs")
    op.drop_table("canonical_entities")
