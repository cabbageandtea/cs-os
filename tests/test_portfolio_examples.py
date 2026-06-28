"""Hosted mock portfolio examples."""

from __future__ import annotations

from app.example_portfolios import get_portfolio_example


def test_alex_portfolio_example(client) -> None:
    response = client.get("/example/alex-rivera")
    assert response.status_code == 200
    body = response.text
    assert "alexrivera.me" in body
    assert "Education" in body
    assert "State University" in body
    assert "example-suite-nav" in body
    assert 'href="/example/alex-rivera/repo/campus-dining"' in body
    assert "https://github.com" not in body
    assert "← Portfolio" not in body  # no self-link on home


def test_jordan_portfolio_example(client) -> None:
    response = client.get("/example/jordan-kim")
    assert response.status_code == 200
    body = response.text
    assert "jordankim.me" in body
    assert "CodeForge Bootcamp" in body
    assert 'href="/example/jordan-kim/demo/shiftsync"' in body
    assert 'href="/example/jordan-kim/repo/inventory-anomaly"' in body


def test_resume_example(client) -> None:
    response = client.get("/example/alex-rivera/resume")
    assert response.status_code == 200
    assert "Fictional example" in response.text
    assert "Download PDF" in response.text
    assert "Education" in response.text


def test_resume_pdf_download(client) -> None:
    response = client.get("/example/alex-rivera/resume.pdf")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content[:4] == b"%PDF"


def test_resume_pdf_unknown_slug_404(client) -> None:
    assert client.get("/example/not-real/resume.pdf").status_code == 404


def test_landing_proof_has_pdf_download(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "/example/alex-rivera/resume.pdf" in response.text
    assert "Download PDF" in response.text
    assert "/example/alex-rivera/linkedin" in response.text


def test_mock_repo_page(client) -> None:
    response = client.get("/example/alex-rivera/repo/campus-dining")
    assert response.status_code == 200
    assert "Campus Dining Insights" in response.text
    assert "README" in response.text


def test_mock_demo_page(client) -> None:
    response = client.get("/example/jordan-kim/demo/shiftsync")
    assert response.status_code == 200
    assert "ShiftSync" in response.text
    assert "mock" in response.text.lower()


def test_mock_github_profile(client) -> None:
    response = client.get("/example/alex-rivera/github")
    assert response.status_code == 200
    assert "alexrivera-dev" in response.text
    assert "/example/alex-rivera/repo/" in response.text


def test_mock_linkedin_profile(client) -> None:
    response = client.get("/example/jordan-kim/linkedin")
    assert response.status_code == 200
    assert "Junior Software Engineer" in response.text
    assert "Education" in response.text


def test_mock_repo_notebook(client) -> None:
    response = client.get("/example/jordan-kim/repo/inventory-anomaly")
    assert response.status_code == 200
    assert "inventory_anomaly.ipynb" in response.text
    assert "IsolationForest" in response.text


def test_demo_404_without_flag(client) -> None:
    assert client.get("/example/alex-rivera/demo/campus-dining").status_code == 404


def test_subpage_has_portfolio_back(client) -> None:
    response = client.get("/example/alex-rivera/repo/campus-dining")
    assert "← Portfolio" in response.text
    assert "example-suite-nav" in response.text


def test_unknown_example_404(client) -> None:
    assert client.get("/example/not-real").status_code == 404


def test_registry_covers_case_studies() -> None:
    from app.sales_content import CASE_STUDIES

    for case in CASE_STUDIES:
        assert get_portfolio_example(case["example_slug"]) is not None
