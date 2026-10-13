"""Compile only approved claim artifacts into declarative scene specs."""

from __future__ import annotations

from typing import Any

from bioscope.scenes.validators import validate_scene_spec
from bioscope.shared.domain.ids import new_id


class SceneCompiler:
    def compile(
        self, claims: list[dict[str, object]], *, include_general_skin_scene: bool = False
    ) -> list[dict[str, Any]]:
        approved_claim_ids = {str(claim["id"]) for claim in claims if claim["status"] == "APPROVED"}
        if not approved_claim_ids:
            return []
        elements: list[dict[str, str]] = []
        relations: list[dict[str, str]] = []
        for index, claim in enumerate(claims, start=1):
            claim_id = str(claim["id"])
            if claim_id not in approved_claim_ids:
                continue
            subject_id = str(claim["subject_entity_id"])
            object_id = str(claim["object_entity_id"])
            elements.extend(
                [
                    {"id": subject_id, "label": str(claim["subject_label"]), "kind": "compound"},
                    {"id": object_id, "label": "Evidence placeholder (DEMO)", "kind": "concept"},
                ]
            )
            relations.append(
                {
                    "id": f"edge_{index}",
                    "from": subject_id,
                    "to": object_id,
                    "predicate": str(claim["predicate"]),
                    "claim_id": claim_id,
                }
            )
        network = {
            "schema_version": "1.0",
            "scene_id": new_id("scene"),
            "kind": "interaction_network",
            "title": "Synthetic evidence relationship (DEMO)",
            "epistemic_label": "DEMO_SYNTHETIC",
            "claim_ids": sorted(approved_claim_ids),
            "elements": elements,
            "relations": relations,
            "fallback": {
                "kind": "evidence_table",
                "reason": "Network rendering is unavailable; inspect the evidence table instead.",
            },
        }
        evidence = {
            "schema_version": "1.0",
            "scene_id": new_id("scene"),
            "kind": "evidence_table",
            "title": "Evidence and provenance (DEMO)",
            "epistemic_label": "DEMO_SYNTHETIC",
            "claim_ids": sorted(approved_claim_ids),
            "elements": [],
            "relations": [],
            "fallback": {"kind": "evidence_table", "reason": "Evidence table is always available."},
        }
        specs = [network, evidence]
        if include_general_skin_scene:
            specs.append(
                {
                    "schema_version": "1.0",
                    "scene_id": new_id("scene"),
                    "kind": "skin_layer",
                    "title": "General skin-layer anatomy (educational schematic)",
                    "epistemic_label": "CURATED_EDUCATIONAL_SCHEMATIC",
                    "claim_ids": [],
                    "elements": [],
                    "relations": [],
                    "asset_ref": {
                        "id": "asset_general_skin_layers_v1",
                        "provenance": "CURATED_EDUCATIONAL_SCHEMATIC",
                        "license": "BioScope original educational schematic",
                    },
                    "fallback": {
                        "kind": "evidence_table",
                        "reason": "General anatomy fallback is available without diagnosis.",
                    },
                }
            )
        for spec in specs:
            validate_scene_spec(spec, approved_claim_ids)
        return specs
