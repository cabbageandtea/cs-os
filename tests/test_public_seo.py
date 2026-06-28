"""Public SEO surfaces: meta tags, robots.txt, sitemap."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.site_branding import PUBLIC_SITEMAP_PATHS


def test_landing_has_seo_meta_tags(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    html = response.text
    assert 'rel="canonical"' in html
    assert 'property="og:title"' in html
    assert 'property="og:description"' in html
    assert 'property="og:image"' in html
    assert 'name="twitter:card"' in html
    assert "application/ld+json" in html
    assert "schema.org" in html
    assert "Doggybagg" in html
    assert "Take it with you" in html


def test_login_is_noindex(client: TestClient) -> None:
    response = client.get("/login")
    assert response.status_code == 200
    assert 'content="noindex, nofollow"' in response.text


def test_robots_txt(client: TestClient) -> None:
    response = client.get("/robots.txt")
    assert response.status_code == 200
    body = response.text
    assert "User-agent: *" in body
    assert "Disallow: /login" in body
    assert "Disallow: /clients" in body
    assert "Sitemap:" in body
    assert "sitemap.xml" in body


def test_sitemap_xml_lists_public_paths(client: TestClient) -> None:
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "application/xml" in response.headers.get("content-type", "")
    body = response.text
    for path in PUBLIC_SITEMAP_PATHS:
        assert f"<loc>http://testserver{path}</loc>" in body
