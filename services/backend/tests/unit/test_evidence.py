from __future__ import annotations

import pytest

from bioscope.connectors.chembl.client import ChEMBLClient
from bioscope.modules.evidence.application.service import EvidenceService
from bioscope.modules.evidence.domain.models import prevent_causal_promotion
from bioscope.modules.evidence.infrastructure.repository import EvidenceRepository
from bioscope.shared.domain.errors import EvidenceInsufficient, SourceUnavailable
from bioscope.shared.infrastructure.db import Database


@pytest.mark.asyncio
async def test_demo_claim_preserves_snapshot_and_explicit_demo_provenance() -> None:
    database = Database("sqlite+aiosqlite:///:memory:")
    await database.create_test_schema()
    try:
        repository = EvidenceRepository(database)
        claim = await EvidenceService(repository).create_demo_bundle("Example medicine")
        persisted = await repository.get_claim(claim.id)

        assert persisted is not None
        assert persisted["predicate"] == "ASSOCIATED_WITH"
        assert persisted["provenance"] == "DEMO"
        assert persisted["source"]["provenance"] == "DEMO"  # type: ignore[index]
        assert persisted["source"]["release_version"] == "demo-2026-10"  # type: ignore[index]
        assert "Synthetic" in str(persisted["source"]["citation"])  # type: ignore[index]
    finally:
        await database.close()


def test_association_cannot_be_promoted_to_causation() -> None:
    with pytest.raises(EvidenceInsufficient, match="association"):
        prevent_causal_promotion(source_predicate="ASSOCIATED_WITH", requested_predicate="CAUSES")


@pytest.mark.asyncio
async def test_disabled_live_source_fails_without_fabricating_results() -> None:
    client = ChEMBLClient(enabled=False)

    with pytest.raises(SourceUnavailable):
        await client.search("aspirin", limit=5)
