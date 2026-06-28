"""Block obviously destructive shell commands unless explicitly allowed."""
from __future__ import annotations

import json
import re
import sys

BLOCKED = re.compile(
    r"(git\s+push\s+--force|git\s+reset\s+--hard|rm\s+-rf|Remove-Item\s+.*-Recurse)",
    re.IGNORECASE,
)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"permission": "allow"}))
        return 0

    command = str(payload.get("command", ""))
    if BLOCKED.search(command):
        print(
            json.dumps(
                {
                    "permission": "ask",
                    "user_message": "This command can destroy remote or local history. Confirm before running.",
                    "agent_message": "Destructive command blocked pending user approval.",
                }
            )
        )
        return 0

    print(json.dumps({"permission": "allow"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
