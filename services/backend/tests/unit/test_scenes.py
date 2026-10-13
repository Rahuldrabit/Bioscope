import pytest

from bioscope.scenes.validators import validate_scene_spec
from bioscope.shared.domain.errors import EvidenceInsufficient


def valid_spec() -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "scene_id": "scene_123abc",
        "kind": "interaction_network",
        "title": "Known relationship",
        "epistemic_label": "DEMO_SYNTHETIC",
        "claim_ids": ["claim_1"],
        "elements": [],
        "relations": [],
        "fallback": {"kind": "evidence_table", "reason": "Fallback"},
    }


def test_scene_rejects_missing_claim_reference() -> None:
    spec = valid_spec()
    spec["relations"] = [
        {"id": "edge_1", "from": "a", "to": "b", "predicate": "INHIBITS", "claim_id": "claim_2"}
    ]

    with pytest.raises(EvidenceInsufficient, match="relationship"):
        validate_scene_spec(spec, {"claim_1"})


def test_scene_rejects_html_and_unsupported_causal_promotion() -> None:
    html = valid_spec()
    html["title"] = "<script>alert(1)</script>"
    with pytest.raises(EvidenceInsufficient, match="unsafe"):
        validate_scene_spec(html, {"claim_1"})

    causal = valid_spec()
    causal["relations"] = [
        {
            "id": "edge_1",
            "from": "a",
            "to": "b",
            "predicate": "CAUSES",
            "source_predicate": "ASSOCIATED_WITH",
            "claim_id": "claim_1",
        }
    ]
    with pytest.raises(EvidenceInsufficient, match="association"):
        validate_scene_spec(causal, {"claim_1"})


def test_general_skin_scene_requires_reviewed_schematic_asset_provenance() -> None:
    skin = valid_spec()
    skin["kind"] = "skin_layer"
    skin["claim_ids"] = []
    skin["asset_ref"] = {
        "id": "asset_general_skin_layers_v1",
        "provenance": "CURATED_EDUCATIONAL_SCHEMATIC",
        "license": "BioScope original educational schematic",
    }
    validate_scene_spec(skin, set())

    skin.pop("asset_ref")
    with pytest.raises(EvidenceInsufficient, match="asset provenance"):
        validate_scene_spec(skin, set())
