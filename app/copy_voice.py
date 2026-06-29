"""Public copy guardrails — keep marketing voice human, not deck-speak."""

from __future__ import annotations

# Phrases that read AI-generated or off-brand on customer-facing HTML.
VOICE_BANNED_PHRASES: tuple[str, ...] = (
    "coherent professional presence",
    "professional presence as one system",
    "single intake →",
    "single intake->",
    "six-second scan",
    "passes the six-second",
    "operating as one system",
    "structured career system delivery",
    "intake triggers delivery",
    "client-owned accounts",
    "one narrative across",
    "proof-of-work online",
    "coordinated output",
    "commit scope",
    "common gap:",
    "how we handle it:",
    "recruiter snapshot",
    "before:</strong>",
    "after:</strong>",
    "doggybagg delivery",
)
