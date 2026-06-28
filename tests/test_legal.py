"""Public legal pages and consent gates."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.site_branding import PUBLIC_SITEMAP_PATHS


def test_terms_page_is_public_and_indexable(client: TestClient) -> None:
    response = client.get("/terms")
    assert response.status_code == 200
    html = response.text
    assert "Terms of Service" in html
    assert "Doggybagg" in html or "doggybagg" in html.lower()
    assert "Limitation of liability" in html or "LIMITATION OF LIABILITY" in html.upper()
    assert 'content="index, follow"' in html
    assert "/privacy" in html


def test_privacy_page_is_public_and_indexable(client: TestClient) -> None:
    response = client.get("/privacy")
    assert response.status_code == 200
    html = response.text
    assert "Privacy Policy" in html
    assert "Stripe" in html
    assert 'content="index, follow"' in html
    assert "/terms" in html


def test_footer_links_to_legal_pages(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert 'href="/terms"' in response.text
    assert 'href="/privacy"' in response.text
    assert "hello@" in response.text.lower()


def test_terms_lists_support_email(client: TestClient) -> None:
    response = client.get("/terms")
    assert response.status_code == 200
    assert "hello@" in response.text.lower()


def test_sitemap_includes_legal_paths(client: TestClient) -> None:
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    for path in ("/terms", "/privacy"):
        assert path in PUBLIC_SITEMAP_PATHS
        assert f"<loc>http://testserver{path}</loc>" in response.text


def test_checkout_requires_terms_acceptance(client: TestClient) -> None:
    response = client.post(
        "/checkout/create",
        data={"package_slug": "launch"},
        follow_redirects=False,
    )
    assert response.status_code == 422
    assert "Terms of Service" in response.text


def test_contact_requires_privacy_consent(client: TestClient) -> None:
    response = client.post(
        "/contact",
        data={
            "name": "Jordan Lee",
            "email": "jordan@example.com",
            "target_role": "Software Engineer Intern",
            "current_status": "Student",
            "interested_package": "launch",
        },
    )
    assert response.status_code == 422
    assert "Privacy Policy" in response.text
