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


def main():
    """Main hook execution."""
    with timed_hook("session-init", decision="approve") as h:
        project_types = get_project_type()
        git_info = check_git_status()

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

        # Set additional hook data
        h.set(
            project_types=project_types,
            branch=git_info["branch"],
            has_claude_md=has_claude_md,
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
