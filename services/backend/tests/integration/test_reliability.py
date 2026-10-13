from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi.testclient import TestClient

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.settings import Settings
from bioscope.main import create_app


def build_client(tmp_path: Path) -> tuple[TestClient, ApplicationContainer]:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        local_asset_dir=tmp_path / "private-assets",
    )
    container = ApplicationContainer(settings, dependency_probes=[])
    asyncio.run(container.database.create_test_schema())
    return TestClient(create_app(settings, container=container)), container


def headers(owner: str = "owner-a") -> dict[str, str]:
    return {"X-Demo-User-ID": owner}


def test_report_has_transparent_null_probability_and_retracted_source_stales_scene(
    tmp_path: Path,
) -> None:
    client, container = build_client(tmp_path)
    with client:
        session = client.post(
            "/api/v1/sessions", json={"title": "Reliability"}, headers=headers()
        ).json()
        candidate = client.post(
            f"/api/v1/sessions/{session['id']}/medicine-items",
            json={"label": "demo medicine"},
            headers=headers(),
        ).json()
        confirmed = client.post(
            f"/api/v1/sessions/{session['id']}/confirm-entities",
            json={"candidate_id": candidate["id"], "expected_session_version": session["version"]},
            headers=headers(),
        )
        assert confirmed.status_code == 200
        run = client.post(
            "/api/v1/runs",
            json={"session_id": session["id"], "question": "Show general skin layers"},
            headers=headers(),
        ).json()

        report = client.get(f"/api/v1/runs/{run['id']}/reliability", headers=headers())
        assert report.status_code == 200
        payload = report.json()
        assert payload["overall_probability"] is None
        assert payload["calibration_model_version"] is None
        assert payload["claim_assessments"][0]["numeric_probability"] is None
        assert payload["claim_assessments"][0]["verdict"] == "INSUFFICIENT"

        claim_id = client.get(
            f"/api/v1/runs/{run['id']}/claims", headers=headers()
        ).json()["claim_ids"][0]
        claim = client.get(f"/api/v1/claims/{claim_id}", headers=headers()).json()
        stale_count = asyncio.run(
            container.source_lifecycle_service.retract_source(claim["source"]["id"])
        )
        assert stale_count == 2
        scenes = client.get(f"/api/v1/runs/{run['id']}/scenes", headers=headers()).json()["items"]
        scene_statuses = {item["kind"]: item["status"] for item in scenes}
        assert scene_statuses == {
            "interaction_network": "STALE",
            "evidence_table": "STALE",
            "skin_layer": "APPROVED",
        }
        network_scene_id = next(
            item["id"] for item in scenes if item["kind"] == "interaction_network"
        )
        stale_scene = client.get(f"/api/v1/scenes/{network_scene_id}", headers=headers())
        assert stale_scene.status_code == 422


def test_reliability_is_owner_scoped(tmp_path: Path) -> None:
    client, _ = build_client(tmp_path)
    with client:
        session = client.post(
            "/api/v1/sessions", json={"title": "Private"}, headers=headers()
        ).json()
        run = client.post(
            "/api/v1/runs",
            json={"session_id": session["id"], "question": "No medicine yet"},
            headers=headers(),
        ).json()
        blocked = client.get(f"/api/v1/runs/{run['id']}/reliability", headers=headers("owner-b"))
        assert blocked.status_code == 403
