"""Run cs-os pytest when agent edits app/ or tests/ files."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def _edited_paths(payload: dict) -> list[str]:
    paths: list[str] = []
    for key in ("file_path", "path", "filePath"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            paths.append(value.replace("\\", "/"))

    edits = payload.get("edits")
    if isinstance(edits, list):
        for edit in edits:
            if isinstance(edit, dict):
                for key in ("file_path", "path", "filePath"):
                    value = edit.get(key)
                    if isinstance(value, str) and value:
                        paths.append(value.replace("\\", "/"))
    return paths


def _should_test(paths: list[str]) -> bool:
    return any(path.startswith("app/") or path.startswith("tests/") for path in paths)


def _python_executable(root: Path) -> str:
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    if venv_python.is_file():
        return str(venv_python)
    venv_python_unix = root / ".venv" / "bin" / "python"
    if venv_python_unix.is_file():
        return str(venv_python_unix)
    return sys.executable


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0

    paths = _edited_paths(payload)
    if not paths or not _should_test(paths):
        return 0

    root = Path.cwd()
    if not (root / "app").is_dir() or not (root / "tests").is_dir():
        return 0

    try:
        result = subprocess.run(
            [_python_executable(root), "-m", "pytest", "tests/", "-q", "--tb=line"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"additional_context": f"pytest hook failed: {exc}"}))
        return 0

    summary = (result.stdout or "").strip()
    errors = (result.stderr or "").strip()
    context = (
        f"pytest after edit ({', '.join(paths)}):\n"
        f"{summary}\n"
        f"{errors}\n"
        f"exit_code={result.returncode}"
    ).strip()
    print(json.dumps({"additional_context": context}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
