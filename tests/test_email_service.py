"""Sender identity for transactional email."""

from __future__ import annotations

import os

import pytest

from app import email_service


@pytest.mark.parametrize(
    ("email_from", "expected_addr"),
    [
        ("Malik Lomax <hello@doggybagg.cc>", "hello@doggybagg.cc"),
        ("Doggybagg <hello@doggybagg.cc>", "hello@doggybagg.cc"),
        ("hello@doggybagg.cc", "hello@doggybagg.cc"),
        ("", "hello@doggybagg.cc"),
    ],
)
def test_email_from_strips_personal_display_name(
    monkeypatch: pytest.MonkeyPatch,
    email_from: str,
    expected_addr: str,
) -> None:
    monkeypatch.setenv("SITE_NAME", "Doggybagg")
    monkeypatch.setenv("SITE_DOMAIN", "doggybagg.cc")
    monkeypatch.delenv("EMAIL_FROM_NAME", raising=False)
    if email_from:
        monkeypatch.setenv("EMAIL_FROM", email_from)
    else:
        monkeypatch.delenv("EMAIL_FROM", raising=False)

    formatted = email_service._email_from()

    assert expected_addr in formatted
    assert "Malik" not in formatted
    assert "Lomax" not in formatted
    assert formatted.startswith("Doggybagg")


def test_email_from_name_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SITE_NAME", "Doggybagg")
    monkeypatch.setenv("SITE_DOMAIN", "doggybagg.cc")
    monkeypatch.setenv("EMAIL_FROM", "Someone <hello@doggybagg.cc>")
    monkeypatch.setenv("EMAIL_FROM_NAME", "DoggyBagg Support")

    formatted = email_service._email_from()

    assert formatted.startswith("DoggyBagg Support")
    assert "Someone" not in formatted
