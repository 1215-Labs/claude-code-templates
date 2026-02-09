#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Adapted from: references/claude-code-hooks-mastery on 2026-02-09

import json
import sys
from pathlib import Path

HOOK_NAME = "notification-status-line"


def state_path(session_id: str) -> Path:
    return Path(f"/tmp/claude-{HOOK_NAME}-{session_id}.json")


def load_input() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    return json.loads(raw)


def main() -> None:
    try:
        data = load_input()
        session_id = str(data.get("session_id", "unknown"))
        tool_name = str(data.get("tool_name", "Notification"))
        tool_input = data.get("tool_input", {})

        state = {
            "tool_name": tool_name,
            "tool_input": tool_input,
        }
        state_path(session_id).write_text(json.dumps(state), encoding="utf-8")

        event = str(data.get("event", "notification"))
        message = str(data.get("message", "hook ran"))
        print(f"[{event}] {message}")
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
