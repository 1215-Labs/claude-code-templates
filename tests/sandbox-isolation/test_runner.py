#!/usr/bin/env python3
"""
Sandbox Isolation Test Runner for claude-code-templates components.

Tests 5 components (18 tests total):
  1. ruff-validator hook — 5 functional tests
  2. ty-validator hook — 5 functional tests
  3. meta-agent config — 2 structural tests
  4. team-builder config — 2 structural tests
  5. team-validator config — 3 structural tests
  6. hooks.json cross-validation — 1 test

Runs INSIDE an E2B sandbox. Upload this + fixtures + subjects, then execute.

Usage: python3 test_runner.py
Output: /home/user/tests/results/report.json and report.md
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

TESTS_DIR = Path("/home/user/tests")
FIXTURES_DIR = TESTS_DIR / "fixtures"
HOOKS_DIR = TESTS_DIR / "hooks"
AGENTS_DIR = TESTS_DIR / "agents"
RESULTS_DIR = TESTS_DIR / "results"

results: list[dict] = []


def run_test(name: str, component: str, func):
    """Run a single test and capture result."""
    try:
        passed, detail = func()
        results.append({
            "name": name,
            "component": component,
            "status": "PASS" if passed else "FAIL",
            "detail": detail,
        })
        icon = "PASS" if passed else "FAIL"
        print(f"  [{icon}] {component}: {name}")
        if not passed:
            print(f"         -> {detail[:120]}")
    except Exception as e:
        results.append({
            "name": name,
            "component": component,
            "status": "ERROR",
            "detail": str(e),
        })
        print(f"  [ERR ] {component}: {name}")
        print(f"         -> {e}")


def run_hook(hook_path: Path, stdin_json: dict) -> tuple[str, str, int]:
    """Run a hook script with JSON on stdin, return (stdout, stderr, returncode)."""
    proc = subprocess.run(
        ["python3", str(hook_path)],
        input=json.dumps(stdin_json),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return proc.stdout.strip(), proc.stderr, proc.returncode


def parse_hook_output(stdout: str) -> dict:
    """Parse hook JSON output, return dict."""
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"_raw": stdout}


def parse_frontmatter(md_path: Path) -> tuple[dict, str]:
    """Parse YAML frontmatter from a markdown file. Returns (frontmatter_dict, full_content)."""
    content = md_path.read_text()
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        raise ValueError(f"No YAML frontmatter found in {md_path}")
    return yaml.safe_load(match.group(1)), content


# ============================================================
# HOOK TESTS: ruff-validator
# ============================================================


def test_ruff_good_python():
    """ruff-validator should ALLOW a clean Python file."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "good_python.py")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ruff-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = "decision" not in output
    return passed, f"rc={rc}, output={output}"


def test_ruff_bad_lint():
    """ruff-validator should BLOCK a file with lint errors."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "bad_lint.py")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ruff-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = output.get("decision") == "block"
    return passed, f"rc={rc}, output={output}"


def test_ruff_non_python():
    """ruff-validator should SKIP (allow) non-.py files."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "not_python.txt")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ruff-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = "decision" not in output
    return passed, f"rc={rc}, output={output}"


def test_ruff_empty_stdin():
    """ruff-validator should handle empty stdin gracefully."""
    proc = subprocess.run(
        ["python3", str(HOOKS_DIR / "ruff-validator.py")],
        input="",
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = parse_hook_output(proc.stdout.strip())
    # Empty stdin -> no file_path -> no .py -> skip
    passed = "decision" not in output
    return passed, f"rc={proc.returncode}, output={output}"


def test_ruff_missing_uvx():
    """ruff-validator should gracefully skip if uvx is not on PATH."""
    env = os.environ.copy()
    env["PATH"] = "/usr/bin:/bin"  # Exclude uvx location
    proc = subprocess.run(
        ["python3", str(HOOKS_DIR / "ruff-validator.py")],
        input=json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": str(FIXTURES_DIR / "good_python.py")},
        }),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    output = parse_hook_output(proc.stdout.strip())
    # FileNotFoundError -> print({}) -> allow
    passed = "decision" not in output
    return passed, f"rc={proc.returncode}, output={output}"


# ============================================================
# HOOK TESTS: ty-validator
# ============================================================


def test_ty_good_python():
    """ty-validator should ALLOW a type-correct Python file."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "good_python.py")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ty-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = "decision" not in output
    return passed, f"rc={rc}, output={output}"


def test_ty_bad_types():
    """ty-validator should BLOCK a file with type errors."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "bad_types.py")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ty-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = output.get("decision") == "block"
    return passed, f"rc={rc}, output={output}"


def test_ty_non_python():
    """ty-validator should SKIP non-.py files."""
    stdin = {
        "tool_name": "Write",
        "tool_input": {"file_path": str(FIXTURES_DIR / "not_python.txt")},
    }
    stdout, stderr, rc = run_hook(HOOKS_DIR / "ty-validator.py", stdin)
    output = parse_hook_output(stdout)
    passed = "decision" not in output
    return passed, f"rc={rc}, output={output}"


def test_ty_empty_stdin():
    """ty-validator should handle empty stdin gracefully."""
    proc = subprocess.run(
        ["python3", str(HOOKS_DIR / "ty-validator.py")],
        input="",
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = parse_hook_output(proc.stdout.strip())
    passed = "decision" not in output
    return passed, f"rc={proc.returncode}, output={output}"


def test_ty_missing_uvx():
    """ty-validator should gracefully skip if uvx is not on PATH."""
    env = os.environ.copy()
    env["PATH"] = "/usr/bin:/bin"
    proc = subprocess.run(
        ["python3", str(HOOKS_DIR / "ty-validator.py")],
        input=json.dumps({
            "tool_name": "Write",
            "tool_input": {"file_path": str(FIXTURES_DIR / "good_python.py")},
        }),
        capture_output=True,
        text=True,
        timeout=30,
        env=env,
    )
    output = parse_hook_output(proc.stdout.strip())
    passed = "decision" not in output
    return passed, f"rc={proc.returncode}, output={output}"


# ============================================================
# AGENT TESTS: structural validation
# ============================================================

REQUIRED_FM_FIELDS = ["name", "description", "model", "color", "tools", "category", "related"]
VALID_MODELS = {"haiku", "sonnet", "opus"}
VALID_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}


def validate_frontmatter(
    md_path: Path,
    expected_tools: list[str] | None = None,
    forbidden_tools: list[str] | None = None,
    expected_model: str | None = None,
    expected_color: str | None = None,
) -> tuple[bool, str]:
    """Validate agent YAML frontmatter against schema."""
    fm, _ = parse_frontmatter(md_path)
    issues: list[str] = []

    for field in REQUIRED_FM_FIELDS:
        if field not in fm:
            issues.append(f"missing field: {field}")

    if fm.get("model") not in VALID_MODELS:
        issues.append(f"invalid model: {fm.get('model')}")
    elif expected_model and fm.get("model") != expected_model:
        issues.append(f"model is '{fm.get('model')}', expected '{expected_model}'")

    if fm.get("color") not in VALID_COLORS:
        issues.append(f"invalid color: {fm.get('color')}")
    elif expected_color and fm.get("color") != expected_color:
        issues.append(f"color is '{fm.get('color')}', expected '{expected_color}'")

    tools = fm.get("tools", [])
    if not isinstance(tools, list):
        issues.append(f"tools should be list, got {type(tools).__name__}")
    else:
        if expected_tools:
            for et in expected_tools:
                if et not in tools:
                    issues.append(f"expected tool missing: {et}")
        if forbidden_tools:
            for ft in forbidden_tools:
                if ft in tools:
                    issues.append(f"forbidden tool present: {ft}")

    name_field = fm.get("name", "")
    filename = md_path.stem
    if name_field != filename:
        issues.append(f"name '{name_field}' != filename '{filename}'")

    desc = str(fm.get("description", "")).strip()
    if len(desc) < 20:
        issues.append(f"description too short ({len(desc)} chars)")

    if not isinstance(fm.get("related"), dict):
        issues.append("related should be a dict")

    return len(issues) == 0, "; ".join(issues) if issues else "all checks passed"


def validate_body_sections(
    md_path: Path,
    required_sections: list[str],
) -> tuple[bool, str]:
    """Validate agent markdown body has required sections."""
    _, content = parse_frontmatter(md_path)
    issues: list[str] = []

    # Get body after frontmatter
    body_match = re.search(r"^---\s*\n.*?\n---\s*\n(.*)$", content, re.DOTALL)
    if not body_match:
        return False, "could not extract body"
    body = body_match.group(1).strip()

    if len(body) < 200:
        issues.append(f"body too short ({len(body)} chars)")

    for section in required_sections:
        # Match both # Section and ## Section
        pattern = r"^#{1,3}\s+" + re.escape(section)
        if not re.search(pattern, body, re.MULTILINE):
            issues.append(f"missing section: {section}")

    return len(issues) == 0, "; ".join(issues) if issues else "all checks passed"


# ============================================================
# CROSS-VALIDATION: hooks.json
# ============================================================


def test_hooks_json_consistency():
    """Verify ruff/ty validators registered in hooks.json with correct matchers."""
    hooks_data = json.loads((HOOKS_DIR / "hooks.json").read_text())
    issues: list[str] = []

    post_hooks = hooks_data.get("hooks", {}).get("PostToolUse", [])

    ruff_found = False
    ty_found = False
    for group in post_hooks:
        matcher = group.get("matcher", "")
        for hook in group.get("hooks", []):
            cmd = hook.get("command", "")
            if "ruff-validator" in cmd:
                ruff_found = True
                if matcher != "Write|Edit":
                    issues.append(f"ruff matcher='{matcher}', expected 'Write|Edit'")
            if "ty-validator" in cmd:
                ty_found = True
                if matcher != "Write|Edit":
                    issues.append(f"ty matcher='{matcher}', expected 'Write|Edit'")

    if not ruff_found:
        issues.append("ruff-validator not in PostToolUse")
    if not ty_found:
        issues.append("ty-validator not in PostToolUse")

    return len(issues) == 0, "; ".join(issues) if issues else "both registered with Write|Edit matcher"


# ============================================================
# MAIN
# ============================================================


def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("SANDBOX ISOLATION TEST RUNNER")
    print("=" * 60)

    # --- ruff-validator ---
    print("\n--- ruff-validator (5 tests) ---")
    run_test("clean file -> allow", "ruff-validator", test_ruff_good_python)
    run_test("lint errors -> block", "ruff-validator", test_ruff_bad_lint)
    run_test("non-.py -> skip", "ruff-validator", test_ruff_non_python)
    run_test("empty stdin -> allow", "ruff-validator", test_ruff_empty_stdin)
    run_test("missing uvx -> graceful", "ruff-validator", test_ruff_missing_uvx)

    # --- ty-validator ---
    print("\n--- ty-validator (5 tests) ---")
    run_test("clean file -> allow", "ty-validator", test_ty_good_python)
    run_test("type errors -> block", "ty-validator", test_ty_bad_types)
    run_test("non-.py -> skip", "ty-validator", test_ty_non_python)
    run_test("empty stdin -> allow", "ty-validator", test_ty_empty_stdin)
    run_test("missing uvx -> graceful", "ty-validator", test_ty_missing_uvx)

    # --- meta-agent ---
    print("\n--- meta-agent (2 tests) ---")
    run_test(
        "frontmatter schema",
        "meta-agent",
        lambda: validate_frontmatter(
            AGENTS_DIR / "meta-agent.md",
            expected_tools=["Write", "Read", "Glob", "Grep", "WebFetch"],
            expected_model="opus",
            expected_color="cyan",
        ),
    )
    run_test(
        "body sections",
        "meta-agent",
        lambda: validate_body_sections(
            AGENTS_DIR / "meta-agent.md",
            ["Purpose", "Instructions", "Output Format"],
        ),
    )

    # --- team-builder ---
    print("\n--- team-builder (2 tests) ---")
    run_test(
        "frontmatter schema",
        "team-builder",
        lambda: validate_frontmatter(
            AGENTS_DIR / "team-builder.md",
            expected_tools=[
                "Read", "Write", "Edit", "Glob", "Grep", "Bash",
                "TaskGet", "TaskUpdate", "TaskList", "SendMessage",
            ],
            expected_model="opus",
            expected_color="cyan",
        ),
    )
    run_test(
        "body sections",
        "team-builder",
        lambda: validate_body_sections(
            AGENTS_DIR / "team-builder.md",
            ["Purpose", "Instructions", "Workflow", "Report"],
        ),
    )

    # --- team-validator ---
    print("\n--- team-validator (3 tests) ---")
    run_test(
        "frontmatter schema",
        "team-validator",
        lambda: validate_frontmatter(
            AGENTS_DIR / "team-validator.md",
            expected_tools=[
                "Read", "Glob", "Grep", "Bash",
                "TaskGet", "TaskUpdate", "TaskList", "SendMessage",
            ],
            expected_model="opus",
            expected_color="yellow",
        ),
    )
    run_test(
        "body sections",
        "team-validator",
        lambda: validate_body_sections(
            AGENTS_DIR / "team-validator.md",
            ["Purpose", "Instructions", "Workflow", "Report"],
        ),
    )
    run_test(
        "no write/edit tools (read-only)",
        "team-validator",
        lambda: validate_frontmatter(
            AGENTS_DIR / "team-validator.md",
            forbidden_tools=["Write", "Edit"],
        ),
    )

    # --- hooks.json ---
    print("\n--- hooks.json cross-validation (1 test) ---")
    run_test("ruff/ty registered correctly", "hooks.json", test_hooks_json_consistency)

    # ============================================================
    # Generate reports
    # ============================================================
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["status"] == "ERROR")
    pass_rate = f"{passed / total * 100:.1f}%" if total else "N/A"

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": "E2B sandbox (fullstack-vue-fastapi-node22)",
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": pass_rate,
        },
        "results": results,
    }

    # JSON report
    (RESULTS_DIR / "report.json").write_text(json.dumps(report, indent=2))

    # Markdown report
    md = [
        "# Sandbox Isolation Test Report",
        "",
        f"**Date:** {report['timestamp']}",
        f"**Environment:** {report['environment']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Tests | {total} |",
        f"| Passed | {passed} |",
        f"| Failed | {failed} |",
        f"| Errors | {errors} |",
        f"| Pass Rate | {pass_rate} |",
        "",
        "## Results by Component",
        "",
    ]

    components: dict[str, list[dict]] = {}
    for r in results:
        components.setdefault(r["component"], []).append(r)

    for comp, tests in components.items():
        md.append(f"### {comp}")
        md.append("")
        md.append("| Test | Status | Detail |")
        md.append("|------|--------|--------|")
        for t in tests:
            detail = t["detail"][:80].replace("|", "\\|")
            md.append(f"| {t['name']} | {t['status']} | {detail} |")
        md.append("")

    (RESULTS_DIR / "report.md").write_text("\n".join(md))

    # Final console summary
    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed}/{total} passed ({pass_rate})")
    print(f"{'=' * 60}")
    print(f"Reports: {RESULTS_DIR / 'report.json'} | {RESULTS_DIR / 'report.md'}")

    sys.exit(0 if failed == 0 and errors == 0 else 1)


if __name__ == "__main__":
    main()
