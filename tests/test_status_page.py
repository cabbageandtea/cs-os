"""Public system status page."""

from __future__ import annotations


def test_status_page_renders(client) -> None:
    response = client.get("/status")
    assert response.status_code == 200
    body = response.text
    assert "Live checks" in body
    assert "Database" in body


def test_health_redirects_browsers_to_status(client) -> None:
    response = client.get("/health", headers={"Accept": "text/html"}, follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "/status"
