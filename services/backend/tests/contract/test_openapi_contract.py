from pathlib import Path

from bioscope.main import create_app


def test_openapi_declares_health_contract_and_error_envelope() -> None:
    schema = create_app().openapi()

    assert "/api/v1/health/live" in schema["paths"]
    assert "ErrorEnvelope" in schema["components"]["schemas"]


def test_checked_in_generated_client_contains_live_health_path() -> None:
    client_file = (
        Path(__file__).resolve().parents[4]
        / "apps"
        / "web"
        / "src"
        / "shared"
        / "api"
        / "generated"
        / "schema.ts"
    )
    assert '"/api/v1/health/live"' in client_file.read_text(encoding="utf-8")
