#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Adapted from: references/claude-code-hooks-mastery/.claude/hooks/pre_tool_use.py on 2026-02-09
"""
Dangerous command and .env access blocker for Claude Code PreToolUse hooks.

Reads tool input from stdin JSON, blocks dangerous rm commands and .env access,
tracks shown warnings per session to avoid duplicate blocking, and exits with
code 2 on first occurrence per pattern or 0 on repeat/no match.

Input: JSON on stdin with keys: session_id, tool_name, tool_input
Output: Warning message on stdout (if blocked)
Exit codes: 0 = allow, 2 = block
"""

import json
import re
import sys


def get_state_path(session_id: str) -> str:
    return f"/tmp/claude-dangerous-command-blocker-{session_id}.json"


def load_state(session_id: str) -> set[str]:
    path = get_state_path(session_id)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("warned", []))
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError):
        return set()


def save_state(session_id: str, warned: set[str]) -> None:
    path = get_state_path(session_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"warned": sorted(warned)}, f)


def is_dangerous_rm_command(command: str) -> bool:
    normalized = " ".join(command.lower().split())

    patterns = [
        r"\brm\s+.*-[a-z]*r[a-z]*f",
        r"\brm\s+.*-[a-z]*f[a-z]*r",
        r"\brm\s+--recursive\s+--force",
        r"\brm\s+--force\s+--recursive",
        r"\brm\s+-r\s+.*-f",
        r"\brm\s+-f\s+.*-r",
    ]

    if any(re.search(pattern, normalized) for pattern in patterns):
        dangerous_paths = [
            r"/",
            r"/\*",
            r"~",
            r"~/",
            r"\$home",
            r"\.\.",
            r"\*",
            r"\.",
            r"\.\s*$",
        ]
        return any(re.search(path, normalized) for path in dangerous_paths)

    return False


def is_env_file_access(tool_name: str, tool_input: dict) -> bool:
    if tool_name in {"Read", "Edit", "MultiEdit", "Write"}:
        file_path = tool_input.get("file_path", "")
        return ".env" in file_path and not file_path.endswith(".env.sample")

    if tool_name == "Bash":
        command = tool_input.get("command", "")
        env_patterns = [
            r"\b\.env\b(?!\.sample)",
            r"cat\s+.*\.env\b(?!\.sample)",
            r"echo\s+.*>\s*\.env\b(?!\.sample)",
            r"touch\s+.*\.env\b(?!\.sample)",
            r"cp\s+.*\.env\b(?!\.sample)",
            r"mv\s+.*\.env\b(?!\.sample)",
        ]
        return any(re.search(pattern, command) for pattern in env_patterns)

    return False


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
        session_id = data.get("session_id", "unknown")
        tool_name = data.get("tool_name", "")
        tool_input = data.get("tool_input", {})
        warned = load_state(session_id)

        violations = []
        if is_env_file_access(tool_name, tool_input):
            violations.append(
                (
                    "env_access",
                    "BLOCKED: Access to .env files containing sensitive data is prohibited\n"
                    "Use .env.sample for template files instead",
                )
            )

        if tool_name == "Bash":
            command = tool_input.get("command", "")
            if is_dangerous_rm_command(command):
                violations.append(
                    ("dangerous_rm", "BLOCKED: Dangerous rm command detected and prevented")
                )

        new_violations = [v for v in violations if v[0] not in warned]
        if not new_violations:
            sys.exit(0)

        for violation_id, _ in new_violations:
            warned.add(violation_id)
        save_state(session_id, warned)

        print("\n".join(msg for _, msg in new_violations))
        sys.exit(2)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
