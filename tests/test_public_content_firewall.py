"""Ensure internal strategy language never appears on public routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# Phrases that reveal business model — must not appear on public HTML.
BANNED_PUBLIC_PHRASES: tuple[str, ...] = (
    "career systems",
    "student perk",
    "setup fee",
    "perk arbitrage",
    "loss leader",
    "loss-leader",
    "free to you",
    "activate your student dev perks",
    "why pay if github student pack",
    "we charge for setup and delivery — not",
    "perks remain free",
    "INTERNAL_PLAYBOOK",
    "STUDENT_PERK_MODEL",
)

PUBLIC_ROUTES = [
  "/",
  "/demo",
  "/contact",
  "/checkout",
  "/start",
  "/status",
  "/terms",
  "/privacy",
  "/example/alex-rivera",
  "/example/taylor-nguyen",
  "/example/taylor-nguyen/linkedin",
  "/example/taylor-nguyen/resume",
  "/example/alex-rivera/linkedin",
  "/example/alex-rivera/resume",
  "/purchase/return",
  "/purchase/cancelled",
  "/login",
]


@pytest.mark.parametrize("path", PUBLIC_ROUTES)
def test_public_routes_do_not_leak_strategy(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, path
    body = response.text.lower()
    for phrase in BANNED_PUBLIC_PHRASES:
        assert phrase not in body, f"{path} leaked banned phrase: {phrase!r}"
