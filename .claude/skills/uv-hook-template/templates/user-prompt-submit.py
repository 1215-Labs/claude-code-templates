#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Adapted from: references/claude-code-hooks-mastery on 2026-02-09

import json
import sys
from pathlib import Path

HOOK_NAME = "user-prompt-submit"
MAX_PROMPT_CHARS = 20000


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
        tool_name = str(data.get("tool_name", "UserPromptSubmit"))
        tool_input = data.get("tool_input", {})

        prompt = str(data.get("prompt", ""))
        state = {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "prompt_length": len(prompt),
        }
        state_path(session_id).write_text(json.dumps(state), encoding="utf-8")

        if not prompt.strip():
            print("Prompt blocked: empty prompt.", file=sys.stderr)
            sys.exit(2)

        if len(prompt) > MAX_PROMPT_CHARS:
            print(
                f"Prompt blocked: exceeds {MAX_PROMPT_CHARS} characters.",
                file=sys.stderr,
            )
            sys.exit(2)

        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
