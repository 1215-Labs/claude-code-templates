#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Independent post-execution validator for Codex PRP results.

Verifies that Codex actually produced the expected output by checking
file existence, conventions compliance, and running test commands.
Does NOT trust Codex's self-reported results.

Usage:
    codex_prp_validator.py --result <result.json> --prp <prp.md> --repo <repo_dir>
    codex_prp_validator.py --result <result.json> --repo <repo_dir>
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


def check_file_exists(file_path: str, repo_dir: str) -> dict:
    """Check if a file exists (handle relative and absolute paths)."""
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(repo_dir) / path
    return {
        "name": "file_exists",
        "target": str(file_path),
        "passed": path.exists(),
        "notes": "" if path.exists() else f"File not found: {path}",
    }


def check_uv_shebang(file_path: str, repo_dir: str) -> dict:
    """Check if a Python file has the UV shebang."""
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(repo_dir) / path
    if not path.exists() or not str(path).endswith(".py"):
        return {"name": "uv_shebang", "target": str(file_path), "passed": True, "notes": "Skipped (not .py or missing)"}
    first_line = path.read_text().split("\n")[0]
    has_shebang = "uv run" in first_line
    return {
        "name": "uv_shebang",
        "target": str(file_path),
        "passed": has_shebang,
        "notes": "" if has_shebang else f"Expected UV shebang, got: {first_line}",
    }


def check_pep723(file_path: str, repo_dir: str) -> dict:
    """Check if a Python file has PEP 723 inline metadata."""
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(repo_dir) / path
    if not path.exists() or not str(path).endswith(".py"):
        return {"name": "pep723_block", "target": str(file_path), "passed": True, "notes": "Skipped"}
    content = path.read_text()
    has_block = "# /// script" in content
    return {
        "name": "pep723_block",
        "target": str(file_path),
        "passed": has_block,
        "notes": "" if has_block else "Missing PEP 723 '# /// script' block",
    }


def check_provenance(file_path: str, repo_dir: str) -> dict:
    """Check if file has a provenance header."""
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(repo_dir) / path
    if not path.exists():
        return {"name": "provenance_header", "target": str(file_path), "passed": False, "notes": "File missing"}
    content = path.read_text()
    has_provenance = "Adapted from:" in content
    return {
        "name": "provenance_header",
        "target": str(file_path),
        "passed": has_provenance,
        "notes": "" if has_provenance else "Missing 'Adapted from:' provenance header",
    }


def check_hooks_json(repo_dir: str, expected_hook_name: str | None = None) -> dict:
    """Check that hooks.json is valid JSON and optionally contains expected hook."""
    hooks_path = Path(repo_dir) / ".claude" / "hooks" / "hooks.json"
    if not hooks_path.exists():
        return {"name": "hooks_json_valid", "target": "hooks.json", "passed": False, "notes": "hooks.json not found"}
    try:
        data = json.loads(hooks_path.read_text())
        if expected_hook_name:
            # Search for the hook name in all hook entries
            found = False
            hooks_section = data.get("hooks", {})
            for event_hooks in hooks_section.values():
                if isinstance(event_hooks, list):
                    for entry in event_hooks:
                        hook_list = entry.get("hooks", [])
                        for hook in hook_list:
                            cmd = hook.get("command", "")
                            if expected_hook_name in cmd:
                                found = True
                                break
            return {
                "name": "hooks_json_entry",
                "target": expected_hook_name,
                "passed": found,
                "notes": "" if found else f"Hook '{expected_hook_name}' not found in hooks.json",
            }
        return {"name": "hooks_json_valid", "target": "hooks.json", "passed": True, "notes": ""}
    except json.JSONDecodeError as e:
        return {"name": "hooks_json_valid", "target": "hooks.json", "passed": False, "notes": f"Invalid JSON: {e}"}


def run_test_command(test_desc: str, command: str, repo_dir: str) -> dict:
    """Run a test command and check exit code."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "name": f"test: {test_desc}",
            "command": command,
            "passed": result.returncode in (0, 2),  # Both are valid for hooks
            "exit_code": result.returncode,
            "output": (result.stdout + result.stderr)[:500],
        }
    except subprocess.TimeoutExpired:
        return {"name": f"test: {test_desc}", "command": command, "passed": False, "exit_code": -1, "output": "Timeout"}
    except Exception as e:
        return {"name": f"test: {test_desc}", "command": command, "passed": False, "exit_code": -1, "output": str(e)}


def run_validate_docs(repo_dir: str) -> dict:
    """Run validate-docs.py if it exists."""
    script = Path(repo_dir) / "scripts" / "validate-docs.py"
    if not script.exists():
        return {"name": "validate_docs", "passed": True, "notes": "Script not found, skipped"}
    try:
        result = subprocess.run(
            ["python3", str(script)],
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=60,
        )
        return {
            "name": "validate_docs",
            "passed": result.returncode == 0,
            "exit_code": result.returncode,
            "output": (result.stdout + result.stderr)[:500],
        }
    except Exception as e:
        return {"name": "validate_docs", "passed": False, "output": str(e)}


def extract_test_commands_from_prp(prp_path: str) -> list[tuple[str, str]]:
    """Extract test commands from PRP Test Plan section."""
    content = Path(prp_path).read_text()
    tests = []
    in_test_plan = False
    current_desc = ""

    for line in content.split("\n"):
        if "## Test Plan" in line:
            in_test_plan = True
            continue
        if in_test_plan:
            if line.startswith("## "):
                break
            if line.startswith("# ") and not line.startswith("#!"):
                current_desc = line.lstrip("# ").strip()
            elif line.startswith("echo ") or line.startswith("python3 ") or line.startswith("uv run "):
                desc = current_desc or f"Command: {line[:60]}"
                tests.append((desc, line.strip()))
                current_desc = ""

    return tests


def extract_hook_name_from_prp(prp_path: str) -> str | None:
    """Extract the hook filename from PRP destination section."""
    content = Path(prp_path).read_text()
    match = re.search(r'\*\*File\*\*:\s*`([^`]+)`', content)
    if match:
        return Path(match.group(1)).name
    return None


def validate(result_path: str, prp_path: str | None, repo_dir: str) -> dict:
    """Run all validation checks and return structured report."""
    checks = []
    issues = []

    # Load Codex result
    codex_result = {}
    if Path(result_path).exists():
        try:
            codex_result = json.loads(Path(result_path).read_text())
        except json.JSONDecodeError:
            issues.append(f"Could not parse Codex result: {result_path}")

    # Check files created
    for f in codex_result.get("files_created", []):
        check = check_file_exists(f, repo_dir)
        checks.append(check)
        if not check["passed"]:
            issues.append(check["notes"])

    # Check UV shebangs on created .py files
    for f in codex_result.get("files_created", []):
        if f.endswith(".py"):
            check = check_uv_shebang(f, repo_dir)
            checks.append(check)
            if not check["passed"]:
                issues.append(check["notes"])

            check = check_pep723(f, repo_dir)
            checks.append(check)
            if not check["passed"]:
                issues.append(check["notes"])

            check = check_provenance(f, repo_dir)
            checks.append(check)
            if not check["passed"]:
                issues.append(check["notes"])

    # Check hooks.json if it was modified
    if codex_result.get("hooks_json_updated"):
        hook_name = None
        if prp_path:
            hook_name = extract_hook_name_from_prp(prp_path)
        check = check_hooks_json(repo_dir, hook_name)
        checks.append(check)
        if not check["passed"]:
            issues.append(check["notes"])

    # Run test commands from PRP
    if prp_path and Path(prp_path).exists():
        test_commands = extract_test_commands_from_prp(prp_path)
        for desc, cmd in test_commands:
            check = run_test_command(desc, cmd, repo_dir)
            checks.append(check)
            if not check["passed"]:
                issues.append(f"Test failed: {desc}")

    # Run validate-docs.py
    check = run_validate_docs(repo_dir)
    checks.append(check)
    if not check["passed"]:
        issues.append("validate-docs.py failed")

    # Determine overall status
    failed_count = sum(1 for c in checks if not c.get("passed", True))
    total_count = len(checks)

    if failed_count == 0:
        status = "pass"
        recommendation = "All checks passed. Ready for registry update."
    elif failed_count <= total_count // 3:
        status = "partial"
        recommendation = f"{failed_count}/{total_count} checks failed. Review issues before proceeding."
    else:
        status = "fail"
        recommendation = f"{failed_count}/{total_count} checks failed. Codex output needs correction."

    return {
        "validation_status": status,
        "checks_passed": total_count - failed_count,
        "checks_total": total_count,
        "checks": checks,
        "issues": issues,
        "recommendation": recommendation,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Codex PRP execution results")
    parser.add_argument("--result", required=True, help="Path to Codex result JSON")
    parser.add_argument("--prp", help="Path to original PRP file")
    parser.add_argument("--repo", required=True, help="Path to repository root")
    parser.add_argument("--json-output", help="Write JSON output to file instead of stdout")
    args = parser.parse_args()

    report = validate(args.result, args.prp, args.repo)

    output = json.dumps(report, indent=2)
    if args.json_output:
        Path(args.json_output).write_text(output)
        print(f"Validation report written to {args.json_output}")
    else:
        print(output)

    sys.exit(0 if report["validation_status"] == "pass" else 1)


if __name__ == "__main__":
    main()
