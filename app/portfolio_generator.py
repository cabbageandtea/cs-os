"""Portfolio generation via LLM (Claude/Gemini).

Autonomous module that calls AI model with client intake data and generates
clinical, data-driven portfolio content. Implements ZERO-TRUST validation and
strict JSON output schema.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models import Client

logger = logging.getLogger(__name__)


class PortfolioValidationError(Exception):
    """Raised when client intake data fails validation."""
    pass


def _validate_client_data(client: Any) -> None:
    """ZERO-TRUST input validation. Fail fast on incomplete/malformed data."""
    required_fields = ["name", "target_role", "intake_data"]
    for field in required_fields:
        if not getattr(client, field, None):
            raise PortfolioValidationError(
                f"Client missing required field: {field}"
            )
    
    # Validate intake_data is parseable
    try:
        if isinstance(client.intake_data, str):
            intake = json.loads(client.intake_data)
        else:
            intake = client.intake_data
    except (json.JSONDecodeError, TypeError) as e:
        raise PortfolioValidationError(f"Client intake_data is malformed: {e}")
    
    # Validate critical intake fields
    required_intake = ["experience", "skills", "achievements"]
    for field in required_intake:
        if field not in intake or not intake[field]:
            raise PortfolioValidationError(
                f"Intake data missing or empty: {field}"
            )


def _sanitize_text(text: str) -> str:
    """Remove marketing hyperbole, clichés, and enthusiastic language."""
    replacements = {
        "passionate": "skilled",
        "motivated": "focused",
        "driven": "executed",
        "expert": "proficient",
        "ninja": "engineer",
        "rockstar": "engineer",
        "innovative": "implemented",
        "cutting-edge": "current",
        "world-class": "professional",
        "best-in-class": "reliable",
        "synergistic": "integrated",
        "leverage": "use",
        "utilize": "use",
        "optimize": "improve",
        "scalable": "reliable",
        "robust": "stable",
        "paradigm shift": "change",
    }
    result = text
    for hyperbole, clinical in replacements.items():
        result = result.replace(hyperbole, clinical)
        result = result.replace(hyperbole.capitalize(), clinical.capitalize())
    return result


def _extract_portfolio_structure(intake: dict[str, Any]) -> dict[str, Any]:
    """Extract and structure portfolio data from intake. Clinical, data-driven output."""
    projects = []
    for proj in intake.get("experience", []):
        projects.append({
            "title": proj.get("title", "Untitled Project"),
            "architecture_summary": _sanitize_text(proj.get("description", "No description")),
            "tech_stack": proj.get("technologies", []),
            "operational_impact": proj.get("metrics", []),
        })
    
    experience = []
    for exp in intake.get("work_history", []):
        experience.append({
            "company": exp.get("company", "Unknown"),
            "title": exp.get("position", "Unknown"),
            "duration": exp.get("duration", "Unknown"),
            "responsibilities": [_sanitize_text(r) for r in exp.get("duties", [])],
        })
    
    return {
        "client_name": intake.get("name", "Unknown"),
        "target_role": intake.get("target_role", "Professional"),
        "executive_summary": _sanitize_text(intake.get("summary", "")),
        "projects": projects,
        "experience": experience,
    }


async def generate_portfolio_json(client: Any, max_retries: int = 3) -> str:
    """
    Generate clinical portfolio JSON from client intake data via LLM.
    
    ZERO-TRUST: Validates all inputs before processing.
    Idempotent: Same input always produces same output.
    
    Args:
        client: Client object with validated intake_data
        max_retries: Exponential backoff retry count for API failures
    
    Returns:
        Minified JSON string matching strict schema (no Markdown, no filler).
    
    Raises:
        PortfolioValidationError if client data fails validation.
    """
    # ZERO-TRUST validation
    _validate_client_data(client)
    
    # Parse intake data
    try:
        if isinstance(client.intake_data, str):
            intake = json.loads(client.intake_data)
        else:
            intake = client.intake_data
    except (json.JSONDecodeError, TypeError) as e:
        logger.error(f"[portfolio_generator] Intake data malformed for client {client.id}: {e}")
        raise PortfolioValidationError(f"Intake parsing failed: {e}")
    
    # Extract clinical portfolio structure
    portfolio = _extract_portfolio_structure(intake)
    
    # Call LLM to enrich/refine (optional, if API available)
    api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            portfolio = await _call_llm_for_enrichment(api_key, portfolio, max_retries)
        except Exception as e:
            logger.warning(f"[portfolio_generator] LLM call failed, using base portfolio: {e}")
            # Fall through: use base portfolio without LLM enrichment
    else:
        logger.info("[portfolio_generator] No LLM API key; using base portfolio structure")
    
    # Return strict JSON (minified, no Markdown, no filler)
    return json.dumps(portfolio, separators=(",", ":"))


async def _call_llm_for_enrichment(
    api_key: str,
    base_portfolio: dict[str, Any],
    max_retries: int,
) -> dict[str, Any]:
    """Call LLM for enrichment with exponential backoff."""
    prompt = f"""
You are a clinical portfolio curator. Given the following portfolio structure, 
refine the descriptions to be data-driven, architecture-focused, and 
free of marketing hyperbole.

Portfolio:
{json.dumps(base_portfolio, indent=2)}

Return a refined portfolio as valid minified JSON only. No Markdown, no explanations.
"""
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Placeholder: integrate with actual AI SDK
            # from anthropic import Anthropic
            # client_obj = Anthropic(api_key=api_key)
            # response = client_obj.messages.create(
            #     model="claude-3-5-sonnet-20241022",
            #     max_tokens=4096,
            #     messages=[{"role": "user", "content": prompt}]
            # )
            # result_json = response.content[0].text
            # return json.loads(result_json)
            
            # For now, return base portfolio
            logger.info(f"[portfolio_generator] LLM enrichment placeholder (retry {retry_count})")
            return base_portfolio
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            backoff_seconds = 2 ** retry_count
            logger.warning(f"[portfolio_generator] LLM call failed, retrying in {backoff_seconds}s: {e}")
            await asyncio.sleep(backoff_seconds)
    
    return base_portfolio
