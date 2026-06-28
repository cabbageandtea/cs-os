"""Legal consent validation for checkout and contact flows."""

from __future__ import annotations


class LegalConsentError(ValueError):
    pass


def validate_terms_accepted(checked: bool) -> None:
    if not checked:
        raise LegalConsentError(
            "You must agree to the Terms of Service and Privacy Policy before checkout."
        )


def validate_privacy_consent(checked: bool) -> None:
    if not checked:
        raise LegalConsentError(
            "You must accept the Privacy Policy before we can store and respond to your inquiry."
        )
