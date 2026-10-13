"""Strict SceneSpec validation before any browser renderer receives data."""

from __future__ import annotations

from typing import Any

from jsonschema import Draft202012Validator

from bioscope.shared.domain.errors import EvidenceInsufficient

SCENE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "scene_id",
        "kind",
        "title",
        "epistemic_label",
        "claim_ids",
        "elements",
        "relations",
        "fallback",
    ],
    "properties": {
        "schema_version": {"const": "1.0"},
        "scene_id": {"type": "string", "pattern": "^scene_[a-z0-9]+$"},
        "kind": {
            "enum": ["interaction_network", "evidence_table", "molecular_structure", "skin_layer"]
        },
        "title": {"type": "string", "maxLength": 160},
        "epistemic_label": {
            "enum": ["DEMO_SYNTHETIC", "CURATED_EDUCATIONAL_SCHEMATIC", "VERIFIED_STRUCTURE"]
        },
        "claim_ids": {"type": "array", "items": {"type": "string"}, "minItems": 0, "maxItems": 50},
        "elements": {"type": "array", "maxItems": 100},
        "relations": {"type": "array", "maxItems": 200},
        "fallback": {
            "type": "object",
            "additionalProperties": False,
            "required": ["kind", "reason"],
            "properties": {
                "kind": {"const": "evidence_table"},
                "reason": {"type": "string", "maxLength": 240},
            },
        },
        "structure": {
            "type": "object",
            "additionalProperties": False,
            "required": ["pdb_id", "source_url"],
            "properties": {
                "pdb_id": {"type": "string", "pattern": "^[0-9A-Za-z]{4}$"},
                "source_url": {"type": "string", "pattern": "^https://www\\.rcsb\\.org/"},
            },
        },
        "asset_ref": {
            "type": "object",
            "additionalProperties": False,
            "required": ["id", "provenance", "license"],
            "properties": {
                "id": {"type": "string", "pattern": "^asset_[a-z0-9_]+$"},
                "provenance": {"const": "CURATED_EDUCATIONAL_SCHEMATIC"},
                "license": {"type": "string", "maxLength": 160},
            },
        },
    },
}


def validate_scene_spec(spec: dict[str, Any], approved_claim_ids: set[str]) -> None:
    errors = list(Draft202012Validator(SCENE_SCHEMA).iter_errors(spec))
    if errors:
        raise EvidenceInsufficient("The scene specification is invalid.")
    claim_ids = spec["claim_ids"]
    if not claim_ids and spec["kind"] != "skin_layer":
        raise EvidenceInsufficient("Non-anatomy scenes require an approved claim reference.")
    if spec["kind"] == "skin_layer" and not claim_ids and "asset_ref" not in spec:
        raise EvidenceInsufficient("An anatomy scene needs reviewed educational asset provenance.")
    if not set(claim_ids).issubset(approved_claim_ids):
        raise EvidenceInsufficient("The scene references an unavailable claim.")
    for relation in spec["relations"]:
        if relation.get("claim_id") not in claim_ids:
            raise EvidenceInsufficient("Every visual relationship must reference a listed claim.")
        if (
            relation.get("predicate") == "CAUSES"
            and relation.get("source_predicate") == "ASSOCIATED_WITH"
        ):
            raise EvidenceInsufficient(
                "An association cannot be rendered as a causal relationship."
            )
    labels = [spec["title"]]
    labels.extend(str(item.get("label", "")) for item in spec["elements"])
    if any("<" in label or "patient-specific" in label.lower() for label in labels):
        raise EvidenceInsufficient("The scene contains unsafe or unsupported labels.")
