"""Required client accounts — public-facing labels only."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClientPrerequisite:
    slug: str
    title: str
    why: str
    signup_url: str
    time_minutes: int
    required_for: frozenset[str]
    note: str = ""


_ALL = frozenset({"foundation", "launch", "accelerator"})

CLIENT_PREREQUISITES: tuple[ClientPrerequisite, ...] = (
    ClientPrerequisite(
        slug="github",
        title="GitHub account",
        why="Your portfolio is deployed under your GitHub profile — recruiters see your work directly.",
        signup_url="https://github.com/signup",
        time_minutes=5,
        required_for=_ALL,
    ),
    ClientPrerequisite(
        slug="github-education",
        title="GitHub Education + Student Developer Pack",
        why="Students: verify with your .edu email or enrollment proof to unlock the pack — domain credits, tools, and deployment perks.",
        signup_url="https://education.github.com/pack",
        time_minutes=15,
        required_for=_ALL,
        note="Not enrolled? Skip — we deploy to github.io. Already verified? Open GitHub → Settings → Education.",
    ),
    ClientPrerequisite(
        slug="student-me-domain",
        title="Free .me domain (students, after pack approval)",
        why=(
            "yourname.me is the link recruiters remember — one URL for resume, LinkedIn, and email. "
            "Students: often free for a year via GitHub Education + nc.me after pack approval."
        ),
        signup_url="https://nc.me/github/auth",
        time_minutes=10,
        required_for=_ALL,
        note="We connect DNS at handoff. No student perk? github.io works — .me is the professional upgrade.",
    ),
    ClientPrerequisite(
        slug="google",
        title="Google account (Gmail)",
        why="Delivery updates, shared review docs, and sign-in when needed during setup.",
        signup_url="https://accounts.google.com/signup",
        time_minutes=5,
        required_for=_ALL,
    ),
    ClientPrerequisite(
        slug="linkedin",
        title="LinkedIn profile",
        why="Required for Launch and Accelerator — resume and portfolio align with your public profile.",
        signup_url="https://www.linkedin.com/signup",
        time_minutes=10,
        required_for=frozenset({"launch", "accelerator"}),
    ),
    ClientPrerequisite(
        slug="custom-domain",
        title="Domain registrar account (Accelerator)",
        why="For a custom URL (e.g. yourname.dev). You register the domain; we provide DNS instructions.",
        signup_url="https://www.namecheap.com/",
        time_minutes=10,
        required_for=frozenset({"accelerator"}),
        note="Optional — say in intake if you prefer github.io only.",
    ),
)


def prerequisites_for_package(package_slug: str) -> list[ClientPrerequisite]:
    slug = package_slug.strip().lower()
    return [
        item
        for item in CLIENT_PREREQUISITES
        if not item.required_for or slug in item.required_for
    ]


def prerequisites_setup_minutes(package_slug: str) -> int:
    return sum(p.time_minutes for p in prerequisites_for_package(package_slug))
