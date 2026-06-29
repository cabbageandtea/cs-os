"""Ensure internal strategy language never appears on public routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.copy_voice import VOICE_BANNED_PHRASES

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

LEGAL_PUBLIC_ROUTES = ("/terms", "/privacy")

# Legal pages use formal defined terms — voice bans apply to marketing routes only.
VOICE_CHECK_ROUTES = tuple(PUBLIC_ROUTES)
STRATEGY_CHECK_ROUTES = tuple(PUBLIC_ROUTES) + LEGAL_PUBLIC_ROUTES


@pytest.mark.parametrize("path", STRATEGY_CHECK_ROUTES)
def test_public_routes_do_not_leak_strategy(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, path
    body = response.text.lower()
    for phrase in BANNED_PUBLIC_PHRASES:
        assert phrase not in body, f"{path} leaked banned phrase: {phrase!r}"


@pytest.mark.parametrize("path", VOICE_CHECK_ROUTES)
def test_public_routes_avoid_ops_leaks(client: TestClient, path: str) -> None:
    from app.copy_voice import OPS_LEAK_BANNED_PHRASES

    response = client.get(path)
    assert response.status_code == 200, path
    body = response.text.lower()
    for phrase in OPS_LEAK_BANNED_PHRASES:
        assert phrase not in body, f"{path} leaked ops detail: {phrase!r}"


@pytest.mark.parametrize("path", VOICE_CHECK_ROUTES)
def test_public_routes_avoid_ai_voice_tells(client: TestClient, path: str) -> None:
    response = client.get(path)
    assert response.status_code == 200, path
    body = response.text.lower()
    for phrase in VOICE_BANNED_PHRASES:
        assert phrase not in body, f"{path} leaked off-voice phrase: {phrase!r}"
