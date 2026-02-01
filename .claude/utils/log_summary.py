"""
Log summary generator for Claude Code hooks.

Analyzes logs and produces actionable insights.
Can be run standalone or called from SessionEnd hook.
"""

import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


def parse_logs(log_file: Path, since_minutes: int = 60) -> list[dict[str, Any]]:
    """Parse log entries from the last N minutes."""
    if not log_file.exists():
        return []

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=since_minutes)
    entries = []

    with open(log_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                ts = datetime.fromisoformat(entry.get("ts", ""))
                if ts >= cutoff:
                    entries.append(entry)
            except (json.JSONDecodeError, ValueError):
                continue

    return entries


def analyze_hooks(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Analyze hook execution patterns."""
    hooks = [e for e in entries if e.get("logger") == "claude.hooks"]

    if not hooks:
        return {"count": 0}

    # Group by hook name
    by_name: dict[str, list[dict]] = defaultdict(list)
    for h in hooks:
        # Extract hook name from "hook:name" format
        msg = h.get("msg", "")
        name = msg.replace("hook:", "") if msg.startswith("hook:") else msg
        by_name[name].append(h)

    # Calculate stats per hook
    stats = {}
    for name, hook_entries in by_name.items():
        durations = [h.get("duration_ms", 0) for h in hook_entries if "duration_ms" in h]
        decisions = [h.get("decision") for h in hook_entries]

        stats[name] = {
            "count": len(hook_entries),
            "avg_ms": round(sum(durations) / len(durations), 2) if durations else None,
            "max_ms": max(durations) if durations else None,
            "approvals": decisions.count("approve"),
            "blocks": decisions.count("block"),
        }

    return {
        "count": len(hooks),
        "by_hook": stats,
    }


def analyze_errors(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Find errors and warnings."""
    errors = [e for e in entries if e.get("level") in ("ERROR", "WARNING")]

    if not errors:
        return {"count": 0}

    # Group by logger
    by_logger: dict[str, list[str]] = defaultdict(list)
    for e in errors:
        logger = e.get("logger", "unknown")
        msg = e.get("msg", "")
        by_logger[logger].append(msg)

    return {
        "count": len(errors),
        "by_logger": {k: list(set(v)) for k, v in by_logger.items()},  # unique messages
    }


def analyze_audit(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize audit trail."""
    audits = [e for e in entries if e.get("logger") == "claude.audit"]

    if not audits:
        return {"count": 0}

    actions = [a.get("msg") for a in audits]
    return {
        "count": len(audits),
        "actions": list(set(actions)),
    }


def generate_summary(since_minutes: int = 60) -> dict[str, Any]:
    """Generate a complete summary of recent log activity."""
    log_file = Path.home() / ".claude" / "logs" / "hooks.log"
    entries = parse_logs(log_file, since_minutes)

    return {
        "period_minutes": since_minutes,
        "total_entries": len(entries),
        "hooks": analyze_hooks(entries),
        "errors": analyze_errors(entries),
        "audit": analyze_audit(entries),
    }


def format_summary(summary: dict[str, Any]) -> str:
    """Format summary for human reading."""
    lines = []
    lines.append(f"=== Log Summary (last {summary['period_minutes']}min) ===")
    lines.append(f"Total entries: {summary['total_entries']}")

    # Hooks
    hooks = summary["hooks"]
    if hooks["count"] > 0:
        lines.append(f"\nHooks executed: {hooks['count']}")
        for name, stats in hooks.get("by_hook", {}).items():
            timing = f" ({stats['avg_ms']}ms avg)" if stats.get("avg_ms") else ""
            blocks = f" [{stats['blocks']} blocked]" if stats.get("blocks") else ""
            lines.append(f"  - {name}: {stats['count']}x{timing}{blocks}")

    # Errors
    errors = summary["errors"]
    if errors["count"] > 0:
        lines.append(f"\nErrors/Warnings: {errors['count']}")
        for logger, msgs in errors.get("by_logger", {}).items():
            lines.append(f"  - {logger}: {', '.join(msgs[:3])}")

    # Audit
    audit = summary["audit"]
    if audit["count"] > 0:
        lines.append(f"\nAudit actions: {audit['count']}")
        for action in audit.get("actions", [])[:5]:
            lines.append(f"  - {action}")

    if summary["total_entries"] == 0:
        lines.append("\nNo log entries in this period.")

    return "\n".join(lines)


def main():
    """CLI entry point."""
    # Default to last 60 minutes, or parse from args
    minutes = 60
    if len(sys.argv) > 1:
        try:
            minutes = int(sys.argv[1])
        except ValueError:
            pass

    summary = generate_summary(minutes)
    print(format_summary(summary))

    # Exit with error code if there were errors
    return 1 if summary["errors"]["count"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
