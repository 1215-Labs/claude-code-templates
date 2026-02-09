#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
# Adapted from: references/claude-code-hooks-mastery/.claude/status_lines/status_line_v6.py on 2026-02-09
# <!-- Adapted from: references/claude-code-hooks-mastery/.claude/status_lines/status_line_v6.py on 2026-02-09 -->
"""Notification status line hook for context-window usage.

Input: JSON on stdin from Claude Code Notification hook with fields:
- session_id: string
- model.display_name: string
- context_window.used_percentage: float (0-100)
- context_window.context_window_size: int

Output: ANSI-colored status line on stdout.
Exit code: always 0 (graceful no-block behavior even on errors).
"""

import json
import os
import sys

CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
BRIGHT_RED = "\033[91m"
DIM = "\033[90m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
RESET = "\033[0m"

DEFAULT_BAR_WIDTH = 15


def get_usage_color(percentage: float) -> str:
    """Return usage color for a given percentage."""
    if percentage < 50:
        return GREEN
    if percentage < 75:
        return YELLOW
    if percentage < 90:
        return RED
    return BRIGHT_RED


def clamp_percentage(value: object) -> float:
    """Convert to float and clamp into [0, 100]."""
    try:
        percentage = float(value)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(100.0, percentage))


def create_progress_bar(percentage: float, width: int) -> str:
    """Create a colorized progress bar with configurable width."""
    safe_width = max(1, width)
    filled = int((percentage / 100.0) * safe_width)
    empty = safe_width - filled
    color = get_usage_color(percentage)
    return f"[{color}{'#' * filled}{DIM}{'-' * empty}{RESET}]"


def format_tokens(tokens: int) -> str:
    """Format token counts as plain, k, or M."""
    if tokens < 1_000:
        return str(tokens)
    if tokens < 1_000_000:
        return f"{tokens / 1_000:.1f}k"
    return f"{tokens / 1_000_000:.2f}M"


def get_bar_width() -> int:
    """Read configurable progress bar width from environment."""
    raw = os.getenv("STATUS_LINE_BAR_WIDTH", str(DEFAULT_BAR_WIDTH))
    try:
        return max(1, int(raw))
    except ValueError:
        return DEFAULT_BAR_WIDTH


def generate_status_line(data: dict) -> str:
    """Generate the formatted Notification status line string."""
    model_name = str(data.get("model", {}).get("display_name", "Claude"))
    session_id = str(data.get("session_id", "--------") or "--------")

    context_data = data.get("context_window", {})
    used_percentage = clamp_percentage(context_data.get("used_percentage", 0.0))

    try:
        context_window_size = int(context_data.get("context_window_size", 200_000) or 200_000)
    except (TypeError, ValueError):
        context_window_size = 200_000

    remaining_tokens = max(0, int(context_window_size * ((100.0 - used_percentage) / 100.0)))

    progress_bar = create_progress_bar(used_percentage, get_bar_width())
    usage_color = get_usage_color(used_percentage)
    left_str = format_tokens(remaining_tokens)

    parts = [
        f"{CYAN}[{model_name}]{RESET}",
        f"{MAGENTA}#{RESET} {progress_bar}",
        f"{usage_color}{used_percentage:.1f}%{RESET} used",
        f"{BLUE}~{left_str} left{RESET}",
        f"{DIM}{session_id}{RESET}",
    ]
    return " | ".join(parts)


def main() -> None:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        print(generate_status_line(payload))
        sys.exit(0)
    except json.JSONDecodeError:
        print(f"{RED}[Claude] # Error: Invalid JSON{RESET}")
        sys.exit(0)
    except Exception as exc:
        print(f"{RED}[Claude] # Error: {exc}{RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
