"""SQLAlchemy metadata for platform and owner-scoped input records."""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
)

metadata = MetaData()

platform_metadata = Table(
    "platform_metadata",
    metadata,
    Column("key", String(100), primary_key=True),
    Column("value", Text, nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

users = Table(
    "users",
    metadata,
    Column("id", String(96), primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("owner_id", String(96), ForeignKey("users.id"), nullable=False, index=True),
    Column("title", String(160), nullable=False),
    Column("risk_scope", String(40), nullable=False, server_default="EDUCATION"),
    Column("version", Integer, nullable=False, server_default="1"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
)

messages = Table(
    "messages",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False, index=True),
    Column("role", String(20), nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

assets = Table(
    "assets",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False, index=True),
    Column("owner_id", String(96), ForeignKey("users.id"), nullable=False, index=True),
    Column("original_filename", String(160), nullable=False),
    Column("mime_type", String(100), nullable=False),
    Column("byte_size", Integer, nullable=False),
    Column("sha256", String(64), nullable=True),
    Column("storage_key", String(240), nullable=False),
    Column("status", String(32), nullable=False),
    Column("upload_token_hash", String(64), nullable=True),
    Column("consent_sensitive_processing", Boolean, nullable=False),
    Column("retention_deadline", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
)

medicine_candidates = Table(
    "medicine_candidates",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False, index=True),
    Column("asset_id", String(64), ForeignKey("assets.id"), nullable=True, index=True),
    Column("label", String(160), nullable=False),
    Column("ingredients", Text, nullable=False),
    Column("status", String(32), nullable=False),
    Column("provenance", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

confirmed_medications = Table(
    "confirmed_medications",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False, index=True),
    Column("candidate_id", String(64), ForeignKey("medicine_candidates.id"), nullable=True),
    Column("label", String(160), nullable=False),
    Column("ingredients", Text, nullable=False),
    Column("confirmed_by", String(96), ForeignKey("users.id"), nullable=False),
    Column("confirmed_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

canonical_entities = Table(
    "canonical_entities",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("entity_type", String(40), nullable=False),
    Column("label", String(240), nullable=False),
    Column("organism", String(120), nullable=False),
    Column("normalizer_version", String(40), nullable=False),
    Column("provenance", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

entity_xrefs = Table(
    "entity_xrefs",
    metadata,
    Column("id", String(64), primary_key=True),
    Column(
        "entity_id", String(64), ForeignKey("canonical_entities.id"), nullable=False, index=True
    ),
    Column("source_namespace", String(64), nullable=False),
    Column("external_id", String(128), nullable=False),
    Column("mapping_status", String(32), nullable=False),
    Column("mapping_version", String(40), nullable=False),
)

sources = Table(
    "sources",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("provider", String(80), nullable=False),
    Column("stable_url", Text, nullable=False),
    Column("citation", Text, nullable=False),
    Column("license_policy", String(160), nullable=False),
    Column("source_type", String(40), nullable=False),
    Column("provenance", String(32), nullable=False),
    Column("status", String(32), nullable=False, server_default="ACTIVE"),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

source_snapshots = Table(
    "source_snapshots",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("source_id", String(64), ForeignKey("sources.id"), nullable=False, index=True),
    Column("release_version", String(100), nullable=False),
    Column("retrieved_at", DateTime(timezone=True), nullable=False),
    Column("content_sha256", String(64), nullable=False),
    Column("record_json", Text, nullable=False),
)

claims = Table(
    "claims",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("subject_entity_id", String(64), ForeignKey("canonical_entities.id"), nullable=False),
    Column("predicate", String(64), nullable=False),
    Column("object_entity_id", String(64), ForeignKey("canonical_entities.id"), nullable=False),
    Column("context_json", Text, nullable=False),
    Column("assertion_type", String(32), nullable=False),
    Column("status", String(32), nullable=False),
    Column("provenance", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

claim_evidence = Table(
    "claim_evidence",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("claim_id", String(64), ForeignKey("claims.id"), nullable=False, index=True),
    Column("source_snapshot_id", String(64), ForeignKey("source_snapshots.id"), nullable=False),
    Column("evidence_direction", String(32), nullable=False),
    Column("location_pointer", String(240), nullable=False),
    Column("directness", String(32), nullable=False),
    Column("review_status", String(32), nullable=False),
)

outbox_events = Table(
    "outbox_events",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("aggregate_id", String(64), nullable=False, index=True),
    Column("event_type", String(80), nullable=False),
    Column("payload_hash", String(64), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("processed_at", DateTime(timezone=True), nullable=True),
)

workflow_runs = Table(
    "workflow_runs",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("session_id", String(64), ForeignKey("sessions.id"), nullable=False, index=True),
    Column("owner_id", String(96), ForeignKey("users.id"), nullable=False, index=True),
    Column("message_id", String(64), ForeignKey("messages.id"), nullable=True),
    Column("question", Text, nullable=False),
    Column("status", String(40), nullable=False),
    Column("policy_version", String(40), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column("updated_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

workflow_tasks = Table(
    "workflow_tasks",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), nullable=False, index=True),
    Column("kind", String(100), nullable=False),
    Column("depends_on_json", Text, nullable=False),
    Column("status", String(32), nullable=False),
    Column("attempt", Integer, nullable=False, server_default="0"),
    Column("max_retries", Integer, nullable=False),
    Column("output_ref", String(64), nullable=True),
)

run_events = Table(
    "run_events",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), nullable=False, index=True),
    Column("sequence", Integer, nullable=False),
    Column("event_type", String(80), nullable=False),
    Column("payload_json", Text, nullable=False),
    Column("occurred_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

run_claims = Table(
    "run_claims",
    metadata,
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), primary_key=True),
    Column("claim_id", String(64), ForeignKey("claims.id"), primary_key=True),
)

verification_reports = Table(
    "verification_reports",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), nullable=False, index=True),
    Column("claim_id", String(64), ForeignKey("claims.id"), nullable=False),
    Column("verdict", String(32), nullable=False),
    Column("reason", Text, nullable=False),
    Column("source_snapshot_ids_json", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

scenes = Table(
    "scenes",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), nullable=False, index=True),
    Column("schema_version", String(20), nullable=False),
    Column("kind", String(48), nullable=False),
    Column("spec_json", Text, nullable=False),
    Column("approval_status", String(32), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)

reliability_reports = Table(
    "reliability_reports",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("run_id", String(64), ForeignKey("workflow_runs.id"), nullable=False, index=True),
    Column("schema_version", String(20), nullable=False),
    Column("assessment_mode", String(48), nullable=False),
    Column("dimensions_json", Text, nullable=False),
    Column("claim_assessments_json", Text, nullable=False),
    Column("unsupported_claim_ids_json", Text, nullable=False),
    Column("critical_gaps_json", Text, nullable=False),
    Column("overall_probability", String(20), nullable=True),
    Column("calibration_model_version", String(80), nullable=True),
    Column("disclaimer", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False, server_default=func.now()),
)
