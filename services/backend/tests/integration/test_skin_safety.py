from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.settings import Settings
from bioscope.main import create_app


def build_client(tmp_path: Path, *, skin_enabled: bool) -> TestClient:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        local_asset_dir=tmp_path / "private-assets",
        enable_skin_image_upload=skin_enabled,
    )
    container = ApplicationContainer(settings, dependency_probes=[])
    asyncio.run(container.database.create_test_schema())
    return TestClient(create_app(settings, container=container))


def headers(owner: str = "owner-a") -> dict[str, str]:
    return {"X-Demo-User-ID": owner}


def image_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (32, 32), color="peachpuff").save(output, format="PNG")
    return output.getvalue()


def ready_asset(client: TestClient, session_id: str, *, owner: str = "owner-a") -> str:
    intent = client.post(
        "/api/v1/assets/upload-intents",
        json={
            "session_id": session_id,
            "filename": "eczema-definitely.png",
            "content_type": "image/png",
            "consent_sensitive_processing": True,
        },
        headers=headers(owner),
    ).json()
    uploaded = client.post(
        f"/api/v1/assets/{intent['asset_id']}/content",
        data={"upload_token": intent["upload_token"]},
        files={"file": ("eczema-definitely.png", image_bytes(), "image/png")},
        headers=headers(owner),
    )
    assert uploaded.status_code == 200
    return str(intent["asset_id"])


def test_skin_observation_is_opt_in_and_never_diagnoses_uploaded_photo(tmp_path: Path) -> None:
    with build_client(tmp_path, skin_enabled=False) as disabled_client:
        session = disabled_client.post(
            "/api/v1/sessions", json={"title": "Skin"}, headers=headers()
        ).json()
        asset_id = ready_asset(disabled_client, session["id"])
        disabled = disabled_client.post(
            f"/api/v1/sessions/{session['id']}/skin-observations",
            json={"asset_id": asset_id, "question": "Does this prove I have eczema?"},
            headers=headers(),
        )
        assert disabled.status_code == 422
        assert disabled.json()["error"]["code"] == "POLICY_RESTRICTED"

    with build_client(tmp_path, skin_enabled=True) as enabled_client:
        session = enabled_client.post(
            "/api/v1/sessions", json={"title": "Skin"}, headers=headers()
        ).json()
        asset_id = ready_asset(enabled_client, session["id"])
        response = enabled_client.post(
            f"/api/v1/sessions/{session['id']}/skin-observations",
            json={"asset_id": asset_id, "question": "Does this prove I have eczema?"},
            headers=headers(),
        )
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "OBSERVATION_UNAVAILABLE"
        assert payload["image_analysis_performed"] is False
        assert payload["visible_observations"] == []
        assert payload["patient_specific_molecular_state"] == "UNKNOWN"
        assert "eczema" not in " ".join(payload["limitations"]).lower()


def test_skin_red_flags_escalate_and_other_users_cannot_observe_asset(tmp_path: Path) -> None:
    with build_client(tmp_path, skin_enabled=True) as client:
        session = client.post(
            "/api/v1/sessions", json={"title": "Skin"}, headers=headers()
        ).json()
        asset_id = ready_asset(client, session["id"])
        urgent = client.post(
            f"/api/v1/sessions/{session['id']}/skin-observations",
            json={
                "asset_id": asset_id,
                "question": "I have a rapidly spreading rash and facial swelling",
            },
            headers=headers(),
        )
        assert urgent.status_code == 200
        assert urgent.json()["status"] == "SAFETY_ESCALATION"
        assert urgent.json()["image_analysis_performed"] is False

        forbidden = client.post(
            f"/api/v1/sessions/{session['id']}/skin-observations",
            json={"asset_id": asset_id, "question": "Can you assess this?"},
            headers=headers("owner-b"),
        )
        assert forbidden.status_code == 403
