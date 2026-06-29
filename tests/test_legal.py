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


def test_checkout_lists_revision_caps(client: TestClient) -> None:
    response = client.get("/checkout")
    assert response.status_code == 200
    html = response.text.lower()
    assert "1 revision round" in html or "1 revision rounds" in html
    assert "2 revision round" in html
    assert "3 revision round" in html
    assert "not included" in html
    assert 'href="/terms#revisions"' in response.text


def test_checkout_lists_full_package_scope(client: TestClient) -> None:
    """Marketing compare table claims scope is visible pre-payment — keep checkout in sync."""
    from app.package_config import PACKAGES, package_display_order

    response = client.get("/checkout")
    assert response.status_code == 200
    html = response.text

    for slug in package_display_order():
        pkg = PACKAGES[slug]
        for item in pkg.deliverables:
            assert item in html, f"missing deliverable {item!r} for {slug}"
        for item in pkg.excludes_display:
            assert item in html, f"missing exclusion {item!r} for {slug}"
        assert pkg.turnaround_display in html, f"missing turnaround for {slug}"


def test_terms_revision_section_is_specific(client: TestClient) -> None:
    response = client.get("/terms")
    assert response.status_code == 200
    html = response.text
    assert 'id="revisions"' in html
    assert "consolidated feedback" in html.lower()
    assert "Foundation" in html and "1 round" in html


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
