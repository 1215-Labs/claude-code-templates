#!/usr/bin/env python3
"""
TaskCompleted hook — validate task quality before marking complete.

Runs build/lint checks (if available) and verifies no uncommitted changes
for code tasks. Follows the same stdin JSON / exit code pattern as
security-check.py.

Input: JSON on stdin with keys: session_id, task_id, task_title, etc.
Output: Feedback message on stdout (if task should not be marked complete)
Exit codes: 0 = allow completion, 2 = block (quality check failed)
"""

import json
import os
import subprocess
import sys


def run_command(args: list[str], timeout: int = 45) -> tuple[int, str]:
    """Run a command and return (exit_code, combined_output)."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = (result.stdout + "\n" + result.stderr).strip()
        return result.returncode, output
    except subprocess.TimeoutExpired:
        return -1, "Command timed out"
    except (FileNotFoundError, OSError) as e:
        return -1, str(e)


def detect_project_type() -> dict:
    """Detect project type and available build/lint commands."""
    project = {"type": "unknown", "build_cmd": None, "lint_cmd": None}

    if os.path.isfile("package.json"):
        try:
            with open("package.json") as f:
                pkg = json.load(f)
            scripts = pkg.get("scripts", {})
            project["type"] = "node"
            if "build" in scripts:
                project["build_cmd"] = ["npm", "run", "build"]
            if "lint" in scripts:
                project["lint_cmd"] = ["npm", "run", "lint"]
            elif "check" in scripts:
                project["lint_cmd"] = ["npm", "run", "check"]
        except (json.JSONDecodeError, OSError):
            pass
    elif os.path.isfile("pyproject.toml"):
        project["type"] = "python"
        # Check for common Python lint tools
        for tool in ["ruff", "flake8", "mypy"]:
            code, _ = run_command(["which", tool], timeout=5)
            if code == 0:
                project["lint_cmd"] = [tool, "check", "."]
                break
    elif os.path.isfile("Cargo.toml"):
        project["type"] = "rust"
        project["build_cmd"] = ["cargo", "check"]
        project["lint_cmd"] = ["cargo", "clippy"]
    elif os.path.isfile("go.mod"):
        project["type"] = "go"
        project["build_cmd"] = ["go", "build", "./..."]
        project["lint_cmd"] = ["go", "vet", "./..."]

    return project


def check_build(project: dict) -> str | None:
    """Run build command if available. Return feedback on failure."""
    if not project["build_cmd"]:
        return None

    code, output = run_command(project["build_cmd"])
    if code == -1 and "timed out" in output:
        # Timeout-safe: allow completion rather than blocking
        return None
    if code != 0:
        # Truncate output to keep feedback readable
        lines = output.splitlines()
        if len(lines) > 20:
            output = "\n".join(lines[:20]) + f"\n... ({len(lines) - 20} more lines)"
        return (
            f"Build failed ({' '.join(project['build_cmd'])}):\n"
            f"{output}\n\n"
            "Fix build errors before marking this task complete."
        )
    return None


def check_lint(project: dict) -> str | None:
    """Run lint command if available. Return feedback on failure."""
    if not project["lint_cmd"]:
        return None

    code, output = run_command(project["lint_cmd"])
    if code == -1 and "timed out" in output:
        return None
    if code != 0:
        lines = output.splitlines()
        if len(lines) > 20:
            output = "\n".join(lines[:20]) + f"\n... ({len(lines) - 20} more lines)"
        return (
            f"Lint check failed ({' '.join(project['lint_cmd'])}):\n"
            f"{output}\n\n"
            "Fix lint issues before marking this task complete."
        )
    return None


def check_uncommitted_changes() -> str | None:
    """Return feedback if there are uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        status = result.stdout.strip()
        if status:
            changed_count = len(status.splitlines())
            return (
                f"You have {changed_count} uncommitted change(s). "
                "Commit your work before marking this task complete."
            )
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        # Defensive: allow completion on parse errors
        sys.exit(0)

    feedback = []

    # Detect project and run checks
    project = detect_project_type()

    # Check 1: Build
    msg = check_build(project)
    if msg:
        feedback.append(msg)

    # Check 2: Lint (only if build passed)
    if not feedback:
        msg = check_lint(project)
        if msg:
            feedback.append(msg)

    # Check 3: Uncommitted changes
    msg = check_uncommitted_changes()
    if msg:
        feedback.append(msg)

    if not feedback:
        sys.exit(0)

    print("TASK COMPLETION GATE — quality check failed:\n")
    for item in feedback:
        print(f"  {item}")
    print("\nAddress these issues before marking the task complete.")
    sys.exit(2)


if __name__ == "__main__":
    main()
