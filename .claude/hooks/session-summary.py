#!/usr/bin/env python3
"""
SessionEnd hook - displays a brief summary of session activity.

Shows hook execution stats, any errors, and audit trail highlights.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.log_summary import generate_summary


def main():
    """Generate and output session summary."""
    # Analyze last 120 minutes (typical session length)
    summary = generate_summary(since_minutes=120)

    # Only output if there's something meaningful to report
    if summary["total_entries"] == 0:
        return 0

    # Build a concise summary message
    parts = []

    # Hook stats
    hooks = summary["hooks"]
    if hooks["count"] > 0:
        hook_info = []
        for name, stats in hooks.get("by_hook", {}).items():
            if stats.get("avg_ms"):
                hook_info.append(f"{name}:{stats['avg_ms']}ms")
        if hook_info:
            parts.append(f"Hooks: {', '.join(hook_info)}")

    # Errors (important to surface)
    errors = summary["errors"]
    if errors["count"] > 0:
        parts.append(f"Errors: {errors['count']}")

    # Audit count
    audit = summary["audit"]
    if audit["count"] > 0:
        parts.append(f"Audited: {audit['count']} actions")

    if parts:
        result = {
            "decision": "approve",
            "systemMessage": f"Session stats: {' | '.join(parts)}"
        }
        print(json.dumps(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
