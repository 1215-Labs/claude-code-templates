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


def check_reference_submodules():
    """Check all reference submodules for available updates.

    Scans the references/ directory for submodules and checks each for updates.
    Returns a dict with 'updates' (list of outdated) and 'up_to_date' (list of current).
    """
    gitmodules = Path(".gitmodules")
    references_dir = Path("references")

    if not gitmodules.exists() or not references_dir.exists():
        return None  # No references setup

    gitmodules_content = gitmodules.read_text()
    if "references/" not in gitmodules_content:
        return None  # No reference submodules

    updates = []
    up_to_date = []

    # Find all submodules in references/
    for submodule_path in references_dir.iterdir():
        if not submodule_path.is_dir():
            continue

        # Check if it's a git submodule (has .git file or directory)
        git_marker = submodule_path / ".git"
        if not git_marker.exists():
            continue

        name = submodule_path.name

        try:
            # Fetch latest from remote (quick operation)
            subprocess.run(
                ["git", "-C", str(submodule_path), "fetch", "origin"],
                capture_output=True,
                timeout=10
            )

            # Detect default branch
            default_branch_result = subprocess.run(
                ["git", "-C", str(submodule_path), "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if default_branch_result.returncode == 0:
                default_branch = default_branch_result.stdout.strip().replace("refs/remotes/origin/", "")
            else:
                default_branch = "main"

            # Get current commit (short)
            current = subprocess.run(
                ["git", "-C", str(submodule_path), "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                timeout=5
            )
            current_commit = current.stdout.strip() if current.returncode == 0 else "unknown"

            # Count commits behind
            behind = subprocess.run(
                ["git", "-C", str(submodule_path), "rev-list", "--count", f"HEAD..origin/{default_branch}"],
                capture_output=True,
                text=True,
                timeout=5
            )
            commits_behind = int(behind.stdout.strip()) if behind.returncode == 0 else 0

            if commits_behind > 0:
                updates.append({
                    "name": name,
                    "current": current_commit,
                    "behind": commits_behind
                })
            else:
                up_to_date.append(name)

        except Exception as e:
            log.warning("submodule_check_failed", submodule=name, error=str(e))
            continue

    if updates or up_to_date:
        return {"updates": updates, "up_to_date": up_to_date}
    return None


def main():
    """Main hook execution."""
    with timed_hook("session-init", decision="approve") as h:
        project_types = get_project_type()
        git_info = check_git_status()
        references_info = check_reference_submodules()

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

        # Check for reference submodule updates
        if references_info and references_info.get("updates"):
            updates = references_info["updates"]
            total_behind = sum(u["behind"] for u in updates)
            names = [u["name"] for u in updates]
            context_parts.append(
                f"📦 Reference updates available: {len(updates)} repos ({total_behind} total commits behind): "
                f"{', '.join(names)}. Ask user if they want to update."
            )

        # Set additional hook data
        h.set(
            project_types=project_types,
            branch=git_info["branch"],
            has_claude_md=has_claude_md,
            references_info=references_info,
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
