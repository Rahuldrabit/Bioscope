"""Transactional canonical evidence persistence."""

from __future__ import annotations

import hashlib
import json

from sqlalchemy import insert, select, update
from sqlalchemy.engine import RowMapping

from bioscope.modules.evidence.domain.models import (
    CanonicalEntity,
    EvidenceClaim,
    SourceRecord,
    SourceSnapshot,
    validate_predicate,
)
from bioscope.shared.domain.errors import EvidenceInsufficient
from bioscope.shared.domain.ids import new_id
from bioscope.shared.infrastructure.db import Database
from bioscope.shared.infrastructure.models import (
    canonical_entities,
    claim_evidence,
    claims,
    outbox_events,
    source_snapshots,
    sources,
)


class EvidenceRepository:
    def __init__(self, database: Database) -> None:
        self._database = database

    async def create_bundle(
        self,
        *,
        subject: CanonicalEntity,
        object_: CanonicalEntity,
        source: SourceRecord,
        snapshot: SourceSnapshot,
        claim: EvidenceClaim,
        evidence_location: str,
        directness: str,
    ) -> None:
        validate_predicate(claim.predicate)
        if not evidence_location:
            raise EvidenceInsufficient("A released claim must include an evidence location.")
        if claim.status != "APPROVED":
            raise EvidenceInsufficient("Only approved claims can be released in a scene.")
        async with self._database.session() as session:
            await session.execute(
                insert(canonical_entities),
                [
                    _entity_values(subject),
                    _entity_values(object_),
                ],
            )
            await session.execute(
                insert(sources).values(
                    id=source.id,
                    provider=source.provider,
                    stable_url=source.stable_url,
                    citation=source.citation,
                    license_policy=source.license_policy,
                    source_type="DATASET",
                    provenance=source.provenance,
                )
            )
            await session.execute(
                insert(source_snapshots).values(
                    id=snapshot.id,
                    source_id=snapshot.source_id,
                    release_version=snapshot.release_version,
                    retrieved_at=snapshot.retrieved_at,
                    content_sha256=snapshot.content_sha256,
                    record_json=json.dumps({"provenance": source.provenance}),
                )
            )
            await session.execute(
                insert(claims).values(
                    id=claim.id,
                    subject_entity_id=claim.subject_entity_id,
                    predicate=claim.predicate,
                    object_entity_id=claim.object_entity_id,
                    context_json=json.dumps(claim.context),
                    assertion_type="EDUCATIONAL",
                    status=claim.status,
                    provenance=claim.provenance,
                )
            )
            await session.execute(
                insert(claim_evidence).values(
                    id=new_id("clmev"),
                    claim_id=claim.id,
                    source_snapshot_id=snapshot.id,
                    evidence_direction="SUPPORTS",
                    location_pointer=evidence_location,
                    directness=directness,
                    review_status="DEMO" if source.provenance == "DEMO" else "PENDING_REVIEW",
                )
            )
            await session.execute(
                insert(outbox_events).values(
                    id=new_id("evt"),
                    aggregate_id=claim.id,
                    event_type="EvidenceApproved",
                    payload_hash=hashlib.sha256(claim.id.encode("utf-8")).hexdigest(),
                )
            )
            await session.commit()

    async def get_claim(self, claim_id: str) -> dict[str, object] | None:
        async with self._database.session() as session:
            result = await session.execute(
                select(
                    claims,
                    canonical_entities.c.label.label("subject_label"),
                    sources.c.id.label("source_id"),
                    sources.c.provider,
                    sources.c.stable_url,
                    sources.c.citation,
                    sources.c.provenance.label("source_provenance"),
                    sources.c.status.label("source_status"),
                    source_snapshots.c.id.label("snapshot_id"),
                    source_snapshots.c.release_version,
                )
                .join(
                    canonical_entities,
                    canonical_entities.c.id == claims.c.subject_entity_id,
                )
                .join(claim_evidence, claim_evidence.c.claim_id == claims.c.id)
                .join(
                    source_snapshots, source_snapshots.c.id == claim_evidence.c.source_snapshot_id
                )
                .join(sources, sources.c.id == source_snapshots.c.source_id)
                .where(claims.c.id == claim_id)
            )
            row = result.mappings().first()
        return _claim_payload(row) if row is not None else None

    async def get_source(self, source_id: str) -> dict[str, object] | None:
        async with self._database.session() as session:
            result = await session.execute(select(sources).where(sources.c.id == source_id))
            row = result.mappings().first()
        if row is None:
            return None
        return {
            "id": str(row["id"]),
            "provider": str(row["provider"]),
            "stable_url": str(row["stable_url"]),
            "citation": str(row["citation"]),
            "license_policy": str(row["license_policy"]),
            "provenance": str(row["provenance"]),
            "status": str(row["status"]),
        }

    async def deprecate_source(self, source_id: str) -> list[str]:
        """Invalidate dependent claims without mutating their immutable provenance."""

        async with self._database.session() as session:
            claim_rows = await session.execute(
                select(claim_evidence.c.claim_id)
                .join(
                    source_snapshots,
                    source_snapshots.c.id == claim_evidence.c.source_snapshot_id,
                )
                .where(source_snapshots.c.source_id == source_id)
            )
            claim_ids = [str(value) for value in claim_rows.scalars().all()]
            await session.execute(
                update(sources).where(sources.c.id == source_id).values(status="RETRACTED")
            )
            if claim_ids:
                await session.execute(
                    update(claims).where(claims.c.id.in_(claim_ids)).values(status="DEPRECATED")
                )
            await session.commit()
        return claim_ids

    async def get_entity(self, entity_id: str) -> dict[str, object] | None:
        async with self._database.session() as session:
            result = await session.execute(
                select(canonical_entities).where(canonical_entities.c.id == entity_id)
            )
            row = result.mappings().first()
        if row is None:
            return None
        return {
            "id": str(row["id"]),
            "entity_type": str(row["entity_type"]),
            "label": str(row["label"]),
            "organism": str(row["organism"]),
            "provenance": str(row["provenance"]),
        }


def _entity_values(entity: CanonicalEntity) -> dict[str, str]:
    return {
        "id": entity.id,
        "entity_type": entity.entity_type,
        "label": entity.label,
        "organism": entity.organism,
        "normalizer_version": "demo-v1",
        "provenance": entity.provenance,
    }


def _claim_payload(row: RowMapping) -> dict[str, object]:
    return {
        "id": str(row["id"]),
        "subject_entity_id": str(row["subject_entity_id"]),
        "subject_label": str(row["subject_label"]),
        "predicate": str(row["predicate"]),
        "object_entity_id": str(row["object_entity_id"]),
        "context": json.loads(str(row["context_json"])),
        "status": str(row["status"]),
        "provenance": str(row["provenance"]),
        "source": {
            "id": str(row["source_id"]),
            "provider": str(row["provider"]),
            "stable_url": str(row["stable_url"]),
            "citation": str(row["citation"]),
            "provenance": str(row["source_provenance"]),
            "status": str(row["source_status"]),
            "snapshot_id": str(row["snapshot_id"]),
            "release_version": str(row["release_version"]),
        },
    }
