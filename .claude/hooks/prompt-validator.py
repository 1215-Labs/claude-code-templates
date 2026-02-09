#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Adapted from: references/claude-code-hooks-mastery/.claude/hooks/user_prompt_submit.py on 2026-02-09
# <!-- Adapted from: references/claude-code-hooks-mastery/.claude/hooks/user_prompt_submit.py on 2026-02-09 -->

import json
import re
import sys
from datetime import datetime, timezone

MAX_PROMPT_CHARS = 50000
INJECTION_PATTERNS = [
    re.compile(r"\bignore\s+previous\s+instructions\b", re.IGNORECASE),
    re.compile(r"\bdisregard\s+all\s+prior\s+instructions\b", re.IGNORECASE),
    re.compile(r"\bsystem\s+prompt\b", re.IGNORECASE),
    re.compile(r"\bdeveloper\s+instructions\b", re.IGNORECASE),
]


def get_state_path(session_id: str) -> str:
    return f"/tmp/claude-prompt-state-{session_id}.json"


def load_state(session_id: str) -> dict:
    try:
        with open(get_state_path(session_id), "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, dict):
            return data
    except (FileNotFoundError, json.JSONDecodeError, TypeError):
        pass
    return {}


def save_state(session_id: str, state: dict) -> None:
    with open(get_state_path(session_id), "w", encoding="utf-8") as file:
        json.dump(state, file)


def parse_time(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def format_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, rem_seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {rem_seconds}s"
    hours, rem_minutes = divmod(minutes, 60)
    return f"{hours}h {rem_minutes}m"


def validate_prompt(prompt: str) -> tuple[bool, str | None]:
    if not prompt or prompt.strip() == "":
        return False, "Prompt blocked: prompt is empty or whitespace-only."
    if len(prompt) > MAX_PROMPT_CHARS:
        return (
            False,
            f"Prompt blocked: prompt exceeds {MAX_PROMPT_CHARS} characters (possible accidental paste).",
        )
    for pattern in INJECTION_PATTERNS:
        if pattern.search(prompt):
            return (
                False,
                "Prompt blocked: prompt appears to contain instruction-injection language.",
            )
    return True, None


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
        session_id = str(data.get("session_id", "unknown"))
        prompt = str(data.get("prompt", ""))

        is_valid, reason = validate_prompt(prompt)
        if not is_valid:
            print(reason, file=sys.stderr)
            sys.exit(2)

        now = datetime.now(timezone.utc)
        state = load_state(session_id)
        prompt_count = int(state.get("prompt_count", 0)) + 1
        started_at = parse_time(state.get("started_at")) or now

        updated_state = {
            "prompt_count": prompt_count,
            "started_at": started_at.isoformat(),
            "last_prompt_at": now.isoformat(),
        }
        save_state(session_id, updated_state)

        session_age_seconds = max(0, int((now - started_at).total_seconds()))
        print(
            f"Prompt #{prompt_count} in this session. Session duration: {format_duration(session_age_seconds)}."
        )
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
