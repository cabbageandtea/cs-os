"""Health endpoint payload."""

from __future__ import annotations

from app.health import build_health_payload


def test_health_payload_reports_database(client, db_session) -> None:
    del db_session
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in ("ok", "degraded")
    assert payload["checks"]["database"] is True
    assert payload["version"]
