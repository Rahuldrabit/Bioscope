from __future__ import annotations

import asyncio
from io import BytesIO
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.settings import Settings
from bioscope.main import create_app


def build_client(tmp_path: Path) -> TestClient:
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        local_asset_dir=tmp_path / "private-assets",
    )
    container = ApplicationContainer(settings, dependency_probes=[])
    asyncio.run(container.database.create_test_schema())
    return TestClient(create_app(settings, container=container))


def png_bytes() -> bytes:
    output = BytesIO()
    Image.new("RGB", (32, 32), color="navy").save(output, format="PNG")
    return output.getvalue()


def create_session(client: TestClient, owner: str = "owner-a") -> dict[str, object]:
    response = client.post(
        "/api/v1/sessions",
        json={"title": "Medicine learning"},
        headers={"X-Demo-User-ID": owner},
    )
    assert response.status_code == 201
    return response.json()


def create_intent(
    client: TestClient, session_id: str, filename: str = "demo-aspirin.png"
) -> dict[str, str]:
    response = client.post(
        "/api/v1/assets/upload-intents",
        json={
            "session_id": session_id,
            "filename": filename,
            "content_type": "image/png",
            "consent_sensitive_processing": True,
        },
        headers={"X-Demo-User-ID": "owner-a"},
    )
    assert response.status_code == 201
    return response.json()


def test_owner_scopes_sessions_and_assets(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        session = create_session(client)
        forbidden = client.get(
            f"/api/v1/sessions/{session['id']}", headers={"X-Demo-User-ID": "owner-b"}
        )
        assert forbidden.status_code == 403

        intent = create_intent(client, str(session["id"]))
        forbidden_asset = client.get(
            f"/api/v1/assets/{intent['asset_id']}", headers={"X-Demo-User-ID": "owner-b"}
        )
        assert forbidden_asset.status_code == 403


def test_combination_candidate_requires_explicit_confirmation(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        session = create_session(client)
        candidate_response = client.post(
            f"/api/v1/sessions/{session['id']}/medicine-items",
            json={"label": "acetaminophen + caffeine"},
            headers={"X-Demo-User-ID": "owner-a"},
        )
        assert candidate_response.status_code == 201
        candidate = candidate_response.json()
        assert candidate["status"] == "CANDIDATE"
        assert candidate["ingredients"] == ["acetaminophen", "caffeine"]

        candidates = client.get(
            f"/api/v1/sessions/{session['id']}/entity-candidates",
            headers={"X-Demo-User-ID": "owner-a"},
        ).json()
        assert candidates["confirmed"] == []

        confirmed = client.post(
            f"/api/v1/sessions/{session['id']}/confirm-entities",
            json={"candidate_id": candidate["id"], "expected_session_version": session["version"]},
            headers={"X-Demo-User-ID": "owner-a"},
        )
        assert confirmed.status_code == 200
        assert confirmed.json()["ingredients"] == ["acetaminophen", "caffeine"]


def test_upload_rejects_missing_consent_and_malformed_content(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        session = create_session(client)
        no_consent = client.post(
            "/api/v1/assets/upload-intents",
            json={
                "session_id": session["id"],
                "filename": "image.png",
                "content_type": "image/png",
                "consent_sensitive_processing": False,
            },
            headers={"X-Demo-User-ID": "owner-a"},
        )
        assert no_consent.status_code == 422

        intent = create_intent(client, str(session["id"]), filename="ordinary.png")
        malformed = client.post(
            f"/api/v1/assets/{intent['asset_id']}/content",
            data={"upload_token": intent["upload_token"]},
            files={"file": ("ordinary.png", b"not an image", "image/png")},
            headers={"X-Demo-User-ID": "owner-a"},
        )
        assert malformed.status_code == 422
        assert malformed.json()["error"]["code"] == "UPLOAD_REJECTED"


def test_private_demo_fixture_is_candidate_not_auto_confirmed_and_deletes(tmp_path: Path) -> None:
    with build_client(tmp_path) as client:
        session = create_session(client)
        intent = create_intent(client, str(session["id"]))
        uploaded = client.post(
            f"/api/v1/assets/{intent['asset_id']}/content",
            data={"upload_token": intent["upload_token"]},
            files={"file": ("demo-aspirin.png", png_bytes(), "image/png")},
            headers={"X-Demo-User-ID": "owner-a"},
        )
        assert uploaded.status_code == 200
        assert "storage_key" not in uploaded.json()

        candidates = client.get(
            f"/api/v1/sessions/{session['id']}/entity-candidates",
            headers={"X-Demo-User-ID": "owner-a"},
        ).json()
        assert candidates["candidates"][0]["provenance"] == "DEMO_OCR_FIXTURE"
        assert candidates["candidates"][0]["status"] == "CANDIDATE"

        deleted = client.delete(
            f"/api/v1/sessions/{session['id']}", headers={"X-Demo-User-ID": "owner-a"}
        )
        assert deleted.status_code == 204
        assert not list((tmp_path / "private-assets").glob("*"))
