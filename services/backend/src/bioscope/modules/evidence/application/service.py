"""Evidence creation against explicit source snapshots."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from bioscope.modules.evidence.domain.models import (
    CanonicalEntity,
    EvidenceClaim,
    SourceRecord,
    SourceSnapshot,
)
from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.shared.domain.ids import new_id


class EvidenceService:
    def __init__(self, repository: EvidenceRepository) -> None:
        self._repository = repository

    async def create_demo_bundle(self, medicine_label: str) -> EvidenceClaim:
        """Create an explicitly synthetic fixture, never a hidden biomedical assertion."""

        source = SourceRecord(
            id=new_id("src"),
            provider="BioScope synthetic test fixture",
            stable_url="https://example.invalid/bioscope/demo-fixture",
            citation=(
                "Synthetic software-testing fixture; not a biomedical source or clinical fact."
            ),
            license_policy="INTERNAL_TEST_ONLY",
            provenance="DEMO",
        )
        source_record = {
            "label": medicine_label,
            "notice": "Synthetic fixture used only to verify provenance and visualization paths.",
        }
        snapshot = SourceSnapshot(
            id=new_id("snap"),
            source_id=source.id,
            release_version="demo-2026-10",
            retrieved_at=datetime.now(UTC),
            content_sha256=hashlib.sha256(
                json.dumps(source_record, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        )
        subject = CanonicalEntity(
            id=new_id("ent"),
            entity_type="compound",
            label=f"{medicine_label} (DEMO)",
            organism="not_applicable",
            provenance="DEMO",
        )
        object_ = CanonicalEntity(
            id=new_id("ent"),
            entity_type="concept",
            label="Educational evidence placeholder (DEMO)",
            organism="not_applicable",
            provenance="DEMO",
        )
        claim = EvidenceClaim(
            id=new_id("claim"),
            subject_entity_id=subject.id,
            predicate="ASSOCIATED_WITH",
            object_entity_id=object_.id,
            context={"patient_specific": False, "organism": None, "scope": "synthetic testing"},
            status="APPROVED",
            provenance="DEMO",
        )
        await self._repository.create_bundle(
            subject=subject,
            object_=object_,
            source=source,
            snapshot=snapshot,
            claim=claim,
            evidence_location="fixture:demo-claim",
            directness="SYNTHETIC",
        )
        return claim
