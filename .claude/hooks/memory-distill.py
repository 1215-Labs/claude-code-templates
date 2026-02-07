#!/usr/bin/env python3
"""
SessionEnd hook: ensures a session log stub exists.

The real distillation happens in the Stop prompt hook (while Claude
still has conversation context). This script is a lightweight fallback
that creates a stub if the Stop hook didn't write one.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging import get_logger, timed_hook

log = get_logger("memory-distill")


def _session_id() -> str:
    """Generate a short session ID from env or timestamp."""
    import os
    # Claude Code sets CLAUDE_SESSION_ID in some contexts
    sid = os.environ.get("CLAUDE_SESSION_ID", "")
    if sid:
        return sid[:8]
    # Fallback: use timestamp-based ID
    return datetime.now(timezone.utc).strftime("%H%M%S")


def main():
    """Create session log stub if one doesn't exist for today."""
    with timed_hook("memory-distill", decision="approve") as h:
        sessions_dir = Path(".claude") / "memory" / "sessions"

        if not sessions_dir.exists():
            # Memory system not initialized - skip silently
            h.set(skipped=True, reason="no_sessions_dir")
            return 0

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        sid = _session_id()
        session_file = sessions_dir / f"{today}_{sid}.md"

        # Check if any session log was already written today
        todays_logs = list(sessions_dir.glob(f"{today}_*.md"))
        if todays_logs:
            # Stop hook already wrote a session log
            h.set(skipped=True, reason="session_log_exists", count=len(todays_logs))
            return 0

        # Write minimal stub
        stub = f"""# Session {today}

## Summary

Session ended without distillation. Use `/memory "status"` to check memory health.

## Date

{today}
"""
        try:
            session_file.write_text(stub, encoding="utf-8")
            h.set(wrote_stub=True, path=str(session_file))
            log.info("stub_created", path=str(session_file))
        except OSError as e:
            log.warning("stub_failed", error=str(e))

    return 0


if __name__ == "__main__":
    sys.exit(main())
