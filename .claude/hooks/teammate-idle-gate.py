#!/usr/bin/env python3
"""
TeammateIdle hook — quality gate when a teammate is about to go idle.

Checks for uncommitted changes and unclaimed pending tasks before allowing
a teammate to stop working. Follows the same stdin JSON / exit code pattern
as security-check.py.

Input: JSON on stdin with keys: session_id, teammate_name, etc.
Output: Feedback message on stdout (if teammate should keep working)
Exit codes: 0 = allow idle, 2 = block (teammate should keep working)
"""

import json
import subprocess
import sys


def run_git(args: list[str], timeout: int = 10) -> str:
    """Run a git command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def check_uncommitted_changes() -> str | None:
    """Return feedback if there are uncommitted changes, else None."""
    status = run_git(["status", "--porcelain"])
    if not status:
        return None

    changed_count = len(status.splitlines())
    return (
        f"You have {changed_count} uncommitted change(s). "
        "Please commit or stash your work before going idle."
    )


def check_pending_tasks() -> str | None:
    """Return feedback if there are unclaimed pending tasks, else None."""
    # Task list is managed by Claude Code internally via the shared task system.
    # We check for pending tasks by looking at the task list file if it exists.
    # This is a best-effort check — if the task system isn't file-based or
    # the path doesn't exist, we skip this check gracefully.
    try:
        import glob
        import os

        teams_dir = os.path.expanduser("~/.claude/teams")
        if not os.path.isdir(teams_dir):
            return None

        # Look for any task files with pending status
        for task_dir in glob.glob(os.path.join(teams_dir, "*/tasks")):
            for task_file in glob.glob(os.path.join(task_dir, "*.json")):
                try:
                    with open(task_file) as f:
                        task = json.load(f)
                    if task.get("status") == "pending" and not task.get("owner"):
                        return (
                            "There are unclaimed pending tasks in the task list. "
                            "Check for available work before going idle."
                        )
                except (json.JSONDecodeError, KeyError, OSError):
                    continue
    except Exception:
        pass

    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Defensive: allow idle on parse errors
        sys.exit(0)

    feedback = []

    # Check 1: Uncommitted changes
    msg = check_uncommitted_changes()
    if msg:
        feedback.append(msg)

    # Check 2: Unclaimed pending tasks
    msg = check_pending_tasks()
    if msg:
        feedback.append(msg)

    if not feedback:
        sys.exit(0)

    print("TEAMMATE IDLE GATE — action needed before going idle:\n")
    for item in feedback:
        print(f"  * {item}")
    print("\nPlease address these items before stopping.")
    sys.exit(2)


if __name__ == "__main__":
    main()
