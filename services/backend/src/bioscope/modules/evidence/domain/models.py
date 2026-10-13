"""Typed evidence records and relationship invariants."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Final

from bioscope.shared.domain.errors import EvidenceInsufficient

ALLOWED_PREDICATES: Final[frozenset[str]] = frozenset(
    {
        "HAS_ACTIVE_INGREDIENT",
        "BINDS_TO",
        "INHIBITS",
        "ACTIVATES",
        "PARTICIPATES_IN",
        "ENCODES",
        "EXPRESSED_IN",
        "LOCATED_IN",
        "REGULATES",
        "CAUSES",
        "ASSOCIATED_WITH",
        "ADVERSE_EFFECT_REPORTED",
        "TREATS_INDICATION",
        "HAS_PHENOTYPE",
    }
)


@dataclass(frozen=True, slots=True)
class CanonicalEntity:
    id: str
    entity_type: str
    label: str
    organism: str
    provenance: str


@dataclass(frozen=True, slots=True)
class SourceRecord:
    id: str
    provider: str
    stable_url: str
    citation: str
    license_policy: str
    provenance: str


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    id: str
    source_id: str
    release_version: str
    retrieved_at: datetime
    content_sha256: str


@dataclass(frozen=True, slots=True)
class EvidenceClaim:
    id: str
    subject_entity_id: str
    predicate: str
    object_entity_id: str
    context: dict[str, str | bool | None]
    status: str
    provenance: str


def validate_predicate(predicate: str) -> None:
    if predicate not in ALLOWED_PREDICATES:
        raise EvidenceInsufficient("The requested relationship predicate is not allowed.")


def prevent_causal_promotion(*, source_predicate: str, requested_predicate: str) -> None:
    if source_predicate == "ASSOCIATED_WITH" and requested_predicate == "CAUSES":
        raise EvidenceInsufficient("An association cannot be promoted to causation.")
