"""Public header branding regressions: logo asset + mobile density rules."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient


def test_public_header_uses_square_icon_and_brand_name(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.text

    assert 'class="brand-mark brand-mark--icon"' in html
    assert 'src="/static/logo-icon.png?v=' in html
    assert 'width="48"' in html
    assert 'height="48"' in html
    assert '<span class="brand-name">Doggybagg</span>' in html


def test_mobile_header_hides_secondary_nav_links() -> None:
    css = Path("app/static/public.css").read_text(encoding="utf-8")
    assert "@media (max-width: 40rem)" in css
    assert ".public-header .brand-name { display: none; }" in css
    assert ".public-header nav .nav-secondary { display: none; }" in css
