#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
PreCompact guard: prevents repeated memory flushes within the same compaction cycle.

Checks if a session log was written in the last 60 seconds. If so, outputs a
systemMessage telling Claude to skip disk writes (but still preserve the summary).

Based on OpenClaw Pattern 2 (Pre-Compaction Memory Flush), bullet 3:
"Track that flush already happened this cycle (prevent repeat)"
"""

import json
import sys
import time
from pathlib import Path

FLUSH_COOLDOWN_SECONDS = 60

# Check both project and global session dirs
SESSION_DIRS = [
    Path(".claude") / "memory" / "sessions",
    Path.home() / ".claude" / "memory" / "sessions",
]


def recent_flush_exists() -> bool:
    """Check if any session log was modified within the cooldown window."""
    now = time.time()
    for sessions_dir in SESSION_DIRS:
        if not sessions_dir.exists():
            continue
        for md_file in sessions_dir.glob("*.md"):
            try:
                mtime = md_file.stat().st_mtime
                if now - mtime < FLUSH_COOLDOWN_SECONDS:
                    return True
            except OSError:
                continue
    return False


def main() -> int:
    if recent_flush_exists():
        result = {
            "decision": "approve",
            "systemMessage": "FLUSH_ALREADY_DONE — A memory flush was written less than 60 seconds ago. Skip disk writes to avoid duplicates, but still preserve critical context in your compaction summary.",
        }
        print(json.dumps(result))
    # If no recent flush, output nothing — let the prompt hook proceed normally
    return 0


if __name__ == "__main__":
    sys.exit(main())
