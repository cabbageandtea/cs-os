"""Shared Jinja2 templates with site branding globals."""

from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.site_branding import (
    dd_rum_application_id,
    dd_rum_client_token,
    inject_template_globals,
)
from app.legal_content import inject_legal_template_globals

_BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_BASE_DIR / "templates"))
inject_template_globals(templates.env)
inject_legal_template_globals(templates.env)
templates.env.globals.update(
    {
        "dd_rum_application_id": dd_rum_application_id(),
        "dd_rum_client_token": dd_rum_client_token(),
    }
)
