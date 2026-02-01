#!/usr/bin/env python3
"""
SessionStart hook for LSP initialization and project context setup.
Runs once at the beginning of each Claude Code session.

v2.1.0+ feature: Uses 'once: true' to execute only once per session.
"""

import json
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for utils import
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.logging import get_logger, timed_hook

log = get_logger("session-init")


def check_typescript_project():
    """Check if this is a TypeScript project."""
    return Path("tsconfig.json").exists()


def check_python_project():
    """Check if this is a Python project."""
    return Path("pyproject.toml").exists() or Path("setup.py").exists()


def check_node_project():
    """Check if this is a Node.js project."""
    return Path("package.json").exists()


def get_project_type():
    """Detect project type for LSP initialization hints."""
    types = []
    if check_typescript_project():
        types.append("typescript")
    if check_python_project():
        types.append("python")
    if check_node_project() and "typescript" not in types:
        types.append("javascript")
    return types or ["unknown"]


def check_git_status():
    """Get basic git status for context."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = result.stdout.strip() if result.returncode == 0 else "unknown"
        return {"branch": branch}
    except Exception as e:
        log.warning("git_status_failed", error=str(e))
        return {"branch": "unknown"}


def check_submodule_updates():
    """Check if claude-code submodule has updates available.

    Only runs in the claude-code-templates repo (where the submodule exists).
    """
    # Only check in repos that have the claude-code submodule configured
    gitmodules = Path(".gitmodules")
    if not gitmodules.exists() or "claude-code" not in gitmodules.read_text():
        return None  # Not a repo with claude-code submodule

    submodule_path = Path("claude-code")
    if not submodule_path.exists() or not (submodule_path / ".git").exists():
        return None  # Submodule not initialized

    try:
        # Fetch latest from remote (quick operation)
        subprocess.run(
            ["git", "-C", "claude-code", "fetch", "origin"],
            capture_output=True,
            timeout=10
        )

        # Get current version
        current = subprocess.run(
            ["git", "-C", "claude-code", "describe", "--tags", "--always"],
            capture_output=True,
            text=True,
            timeout=5
        )
        current_version = current.stdout.strip() if current.returncode == 0 else "unknown"

        # Get latest version on origin/main
        latest = subprocess.run(
            ["git", "-C", "claude-code", "describe", "--tags", "origin/main"],
            capture_output=True,
            text=True,
            timeout=5
        )
        latest_version = latest.stdout.strip() if latest.returncode == 0 else "unknown"

        # Count commits behind
        behind = subprocess.run(
            ["git", "-C", "claude-code", "rev-list", "--count", "HEAD..origin/main"],
            capture_output=True,
            text=True,
            timeout=5
        )
        commits_behind = int(behind.stdout.strip()) if behind.returncode == 0 else 0

        if commits_behind > 0:
            return {
                "current": current_version,
                "latest": latest_version,
                "behind": commits_behind
            }
        return None  # Up to date

    except Exception as e:
        log.warning("submodule_check_failed", error=str(e))
        return None


def main():
    """Main hook execution."""
    with timed_hook("session-init", decision="approve") as h:
        project_types = get_project_type()
        git_info = check_git_status()
        submodule_info = check_submodule_updates()

        # Build context message
        context_parts = []

        if project_types != ["unknown"]:
            context_parts.append(f"Project type(s): {', '.join(project_types)}")

        if git_info["branch"] != "unknown":
            context_parts.append(f"Current branch: {git_info['branch']}")

        # Check for CLAUDE.md
        has_claude_md = Path(".claude/CLAUDE.md").exists()
        if has_claude_md:
            context_parts.append("CLAUDE.md found - project has Claude Code configuration")

        # Check for submodule updates
        if submodule_info:
            context_parts.append(
                f"⚠️ claude-code submodule update available: {submodule_info['current']} → {submodule_info['latest']} "
                f"({submodule_info['behind']} commits behind). Run: git submodule update --remote claude-code"
            )

        # Set additional hook data
        h.set(
            project_types=project_types,
            branch=git_info["branch"],
            has_claude_md=has_claude_md,
            submodule_update=submodule_info,
        )

    # Output hook result
    result = {
        "decision": "approve",
        "systemMessage": " | ".join(context_parts) if context_parts else None
    }

    # Only output if we have context to share
    if result["systemMessage"]:
        print(json.dumps(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
