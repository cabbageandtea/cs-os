"""Operator authentication — cookie session + HTTP Basic fallback."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from urllib.parse import quote

from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials

_security = HTTPBasic(auto_error=False)
SESSION_COOKIE = "csos_ops_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 14  # 14 days — local operator use


def ops_password() -> str:
    return os.environ.get("OPS_PASSWORD", "").strip()


def _session_token(password: str) -> str:
    digest = hmac.new(password.encode(), b"cs-os-ops-v1", hashlib.sha256).digest()
    return base64.urlsafe_b64encode(digest).decode().rstrip("=")


def set_ops_session(response, password: str) -> None:
    database_url = os.environ.get("DATABASE_URL", "").lower()
    response.set_cookie(
        SESSION_COOKIE,
        _session_token(password),
        httponly=True,
        secure=not database_url.startswith("sqlite"),
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )


def clear_ops_session(response) -> None:
    response.delete_cookie(SESSION_COOKIE)


def is_ops_authenticated(request: Request, credentials: HTTPBasicCredentials | None) -> bool:
    password = ops_password()
    if not password:
        return False

    cookie = request.cookies.get(SESSION_COOKIE, "")
    if cookie and secrets.compare_digest(cookie, _session_token(password)):
        return True

    if credentials is not None and secrets.compare_digest(
        credentials.password.encode(), password.encode()
    ):
        return True

    return False


def _login_redirect(request: Request) -> RedirectResponse:
    next_path = request.url.path
    if request.url.query:
        next_path = f"{next_path}?{request.url.query}"
    return RedirectResponse(url=f"/login?next={quote(next_path)}", status_code=303)


def require_ops_auth(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(_security),
) -> str:
    """Validate operator session or HTTP Basic credentials."""
    password = ops_password()
    if not password:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Operator access is not configured (OPS_PASSWORD missing).",
        )

    if is_ops_authenticated(request, credentials):
        return credentials.username if credentials else "operator"

    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        next_path = request.url.path
        if request.url.query:
            next_path = f"{next_path}?{request.url.query}"
        raise HTTPException(
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
            headers={"Location": f"/login?next={quote(next_path)}"},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Operator authentication required.",
        headers={"WWW-Authenticate": "Basic realm=cs-os-ops"},
    )


def verify_ops_password(candidate: str) -> bool:
    password = ops_password()
    if not password or not candidate:
        return False
    return secrets.compare_digest(candidate.encode(), password.encode())
