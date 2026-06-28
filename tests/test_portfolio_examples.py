"""Hosted mock portfolio examples."""

from __future__ import annotations

from app.example_portfolios import get_portfolio_example


def test_alex_portfolio_example(client) -> None:
    response = client.get("/example/alex-rivera")
    assert response.status_code == 200
    body = response.text
    assert "alexrivera.me" in body
    assert "View projects" in body
    assert "Fictional example" in body


def test_jordan_portfolio_example(client) -> None:
    response = client.get("/example/jordan-kim")
    assert response.status_code == 200
    assert "jordankim.me" in response.text


def test_resume_example(client) -> None:
    response = client.get("/example/alex-rivera/resume")
    assert response.status_code == 200
    assert "Resume (example)" in response.text


def test_unknown_example_404(client) -> None:
    assert client.get("/example/not-real").status_code == 404


def test_registry_covers_case_studies() -> None:
    from app.sales_content import CASE_STUDIES

    for case in CASE_STUDIES:
        assert get_portfolio_example(case["example_slug"]) is not None
