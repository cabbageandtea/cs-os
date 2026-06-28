"""Transactional email for intake reminders."""

from __future__ import annotations

import logging
import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr, parseaddr
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


from app.site_branding import site_domain, site_name, support_email


def _email_from_address() -> str:
    """Mailbox address only — ignores any display name in EMAIL_FROM."""
    raw = os.environ.get("EMAIL_FROM", "").strip()
    if not raw:
        return f"hello@{site_domain()}"
    _, addr = parseaddr(raw)
    if addr and "@" in addr:
        return addr.strip().lower()
    if "@" in raw and "<" not in raw:
        return raw.strip().lower()
    return f"hello@{site_domain()}"


def _email_from_display_name() -> str:
    custom = os.environ.get("EMAIL_FROM_NAME", "").strip()
    return custom or site_name()


def _email_from() -> str:
    return formataddr((_email_from_display_name(), _email_from_address()))


def _resend_api_key() -> str:
    return os.environ.get("RESEND_API_KEY", "").strip()


def _smtp_config() -> dict[str, Any] | None:
    host = os.environ.get("SMTP_HOST", "").strip()
    if not host:
        return None
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER", "").strip()
    password = os.environ.get("SMTP_PASSWORD", "").strip()
    use_tls = os.environ.get("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
    return {"host": host, "port": port, "user": user, "password": password, "use_tls": use_tls}


def build_intake_reminder_email(
    *,
    client_name: str,
    package_name: str,
    intake_url: str,
    start_url: str,
) -> tuple[str, str, str]:
    """Return (subject, plain text, html)."""
    subject = f"Complete your intake — {package_name}"
    plain = f"""Hi {client_name},

Payment received for {package_name}. Delivery starts when your intake form is complete.

Complete intake (bookmark this link):
{intake_url}

Account checklist before you submit:
{start_url}

If you close this tab, use the same intake link above or visit:
{start_url.replace('/start', '/purchase/return')}

Questions: {support_email()}

— {site_name()}
"""
    html = f"""<!DOCTYPE html>
<html lang="en"><body style="font-family:system-ui,sans-serif;line-height:1.55;color:#111;max-width:36rem;">
<p>Hi {client_name},</p>
<p>Payment received for <strong>{package_name}</strong>. Delivery starts when your intake form is complete.</p>
<p><a href="{intake_url}" style="display:inline-block;background:#111;color:#fff;padding:12px 18px;text-decoration:none;border-radius:3px;">Complete intake</a></p>
<p style="font-size:14px;color:#555;">Account checklist: <a href="{start_url}">{start_url}</a></p>
<p style="font-size:14px;color:#555;">Lost your link? <a href="{start_url.replace('/start', '/purchase/return')}">Resume with session ID</a></p>
<p style="font-size:14px;color:#888;">Questions: <a href="mailto:{support_email()}">{support_email()}</a></p>
<p style="font-size:12px;color:#aaa;margin-top:1.5rem;">— {site_name()}</p>
</body></html>"""
    return subject, plain, html


def send_email(
    *,
    to_email: str,
    subject: str,
    plain: str,
    html: str,
    reply_to: str | None = None,
) -> bool:
    """Send email via Resend, SMTP, or dev log. Returns True when dispatched."""
    to_email = (to_email or "").strip().lower()
    if not to_email or "@" not in to_email:
        logger.warning("intake email skipped: missing recipient")
        return False

    from_addr = _email_from()
    resend_key = _resend_api_key()
    if resend_key:
        return _send_resend(
            api_key=resend_key,
            from_addr=from_addr,
            to_email=to_email,
            subject=subject,
            plain=plain,
            html=html,
        )

    smtp = _smtp_config()
    if smtp:
        return _send_smtp(
            smtp=smtp,
            from_addr=from_addr,
            to_email=to_email,
            subject=subject,
            plain=plain,
            html=html,
        )

    logger.info(
        "INTAKE EMAIL (dev — no RESEND_API_KEY / SMTP_HOST)\nTo: %s\nSubject: %s\n\n%s",
        to_email,
        subject,
        plain,
    )
    return True


def send_intake_reminder_email(
    *,
    to_email: str,
    client_name: str,
    package_name: str,
    intake_url: str,
    start_url: str,
) -> bool:
    subject, plain, html = build_intake_reminder_email(
        client_name=client_name,
        package_name=package_name,
        intake_url=intake_url,
        start_url=start_url,
    )
    return send_email(to_email=to_email, subject=subject, plain=plain, html=html)


def send_contact_lead_notification(
    *,
    name: str,
    email: str,
    target_role: str,
    current_status: str,
    interested_package: str,
) -> bool:
    """Notify support inbox when a contact form lead is submitted."""
    inbox = support_email()
    if not inbox or "@" not in inbox:
        return False
    package_label = interested_package.strip() or "unsure"
    subject = f"Contact inquiry — {name}"
    plain = f"""New contact form submission on {site_name()}:

Name: {name}
Email: {email}
Target role: {target_role}
Current status: {current_status}
Package interest: {package_label}

Reply directly to {email} to respond.
"""
    html = f"""<!DOCTYPE html>
<html lang="en"><body style="font-family:system-ui,sans-serif;line-height:1.55;color:#111;max-width:36rem;">
<p><strong>New contact form submission</strong> on {site_name()}</p>
<ul>
<li><strong>Name:</strong> {name}</li>
<li><strong>Email:</strong> <a href="mailto:{email}">{email}</a></li>
<li><strong>Target role:</strong> {target_role}</li>
<li><strong>Current status:</strong> {current_status}</li>
<li><strong>Package interest:</strong> {package_label}</li>
</ul>
<p style="font-size:14px;color:#555;">Reply directly to the prospect to respond.</p>
</body></html>"""
    try:
        return send_email(
            to_email=inbox,
            subject=subject,
            plain=plain,
            html=html,
            reply_to=email,
        )
    except EmailDeliveryError:
        logger.warning("contact lead notification failed for %s", email)
        return False


def _send_resend(
    *,
    api_key: str,
    from_addr: str,
    to_email: str,
    subject: str,
    plain: str,
    html: str,
) -> bool:
    try:
        payload: dict[str, Any] = {
            "from": from_addr,
            "to": [to_email],
            "subject": subject,
            "text": plain,
            "html": html,
        }
        reply = (reply_to or support_email()).strip()
        if reply and "@" in reply:
            payload["reply_to"] = reply
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json=payload,
            timeout=15.0,
        )
        response.raise_for_status()
        return True
    except httpx.HTTPError as exc:
        logger.exception("Resend email failed for %s", to_email)
        raise EmailDeliveryError(str(exc)) from exc


def _send_smtp(
    *,
    smtp: dict[str, Any],
    from_addr: str,
    to_email: str,
    subject: str,
    plain: str,
    html: str,
) -> bool:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(plain)
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(smtp["host"], smtp["port"], timeout=15) as server:
            if smtp["use_tls"]:
                server.starttls()
            if smtp["user"]:
                server.login(smtp["user"], smtp["password"])
            server.send_message(msg)
        return True
    except smtplib.SMTPException as exc:
        logger.exception("SMTP email failed for %s", to_email)
        raise EmailDeliveryError(str(exc)) from exc
