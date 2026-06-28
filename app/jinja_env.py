"""Shared Jinja2 templates with site branding globals."""

from pathlib import Path

from fastapi.templating import Jinja2Templates

from app.site_branding import inject_template_globals

_BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(_BASE_DIR / "templates"))
inject_template_globals(templates.env)
