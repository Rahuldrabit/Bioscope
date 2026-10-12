from fastapi.testclient import TestClient

from bioscope.bootstrap.container import ApplicationContainer
from bioscope.bootstrap.settings import Settings
from bioscope.main import create_app


class FailedProbe:
    async def ping(self) -> bool:
        return False


def build_container(*, dependency_probes: list[FailedProbe] | None = None) -> ApplicationContainer:
    settings = Settings(database_url="sqlite+aiosqlite:///:memory:")
    return ApplicationContainer(settings, dependency_probes=dependency_probes or [])


def test_live_health_does_not_require_database() -> None:
    app = create_app(Settings(database_url="sqlite+aiosqlite:///:memory:"))
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "live"}


def test_ready_health_checks_database() -> None:
    container = build_container()
    app = create_app(container.settings, container=container)
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_ready_health_reports_failed_dependency() -> None:
    container = build_container(dependency_probes=[FailedProbe()])
    app = create_app(container.settings, container=container)
    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready", headers={"X-Request-ID": "dependency"})

    assert response.status_code == 503
    assert response.json()["error"] == {
        "code": "DEPENDENCY_UNAVAILABLE",
        "message": "A required service is temporarily unavailable.",
        "retryable": True,
        "details": {},
        "trace_id": "dependency",
    }


def test_not_found_uses_standard_error_envelope() -> None:
    app = create_app(Settings(database_url="sqlite+aiosqlite:///:memory:"))
    with TestClient(app) as client:
        response = client.get("/api/v1/not-a-route", headers={"X-Request-ID": "test-trace"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "The requested resource was not found.",
            "retryable": False,
            "details": {},
            "trace_id": "test-trace",
        }
    }


def test_unhandled_error_uses_same_trace_id_in_header_and_body() -> None:
    container = build_container()
    app = create_app(container.settings, container=container)

    async def explode() -> None:
        raise RuntimeError("test failure")

    app.get("/test/error")(explode)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/test/error")

    assert response.status_code == 500
    assert response.headers["X-Request-ID"] == response.json()["error"]["trace_id"]
