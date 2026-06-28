"""Secure intake token generation and verification."""

from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta, timezone

from app.models import Client, utcnow

DEFAULT_TOKEN_TTL_DAYS = 14


def _pepper() -> str:
    return os.environ.get("INTAKE_TOKEN_PEPPER", "")


def hash_token(token: str) -> str:
    material = f"{token}{_pepper()}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def generate_intake_token() -> str:
    return secrets.token_urlsafe(32)


def token_expires_at(*, days: int = DEFAULT_TOKEN_TTL_DAYS) -> datetime:
    return utcnow() + timedelta(days=days)


def assign_intake_token(client: Client, *, days: int = DEFAULT_TOKEN_TTL_DAYS) -> str:
    """Generate token, store hash on client, return plaintext once."""
    token = generate_intake_token()
    client.intake_token_hash = hash_token(token)
    client.intake_token_expires_at = token_expires_at(days=days)
    return token


def verify_intake_token(client: Client, token: str) -> str | None:
    """Return error message if invalid, else None."""
    if client.customer_lifecycle == "archived":
        return "This intake link is no longer valid."
    if not client.intake_token_hash:
        return "Intake link not found."
    if client.intake_token_expires_at:
        expires = client.intake_token_expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if utcnow() > expires:
            return "This intake link has expired. Contact support for a new link."
    if hash_token(token) != client.intake_token_hash:
        return "Invalid intake link."
    return None


def invalidate_intake_token(client: Client) -> None:
    client.intake_token_hash = None
    client.intake_token_expires_at = None
