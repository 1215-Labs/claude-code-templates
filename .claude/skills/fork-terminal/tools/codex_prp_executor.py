#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Codex PRP Executor — Optimized fork wrapper for single-PRP execution.

Prepares the prompt, writes scoped AGENTS.md, runs Codex with optimized
flags (--full-auto, --ephemeral, --output-schema, -o), then runs
independent validation and writes a combined report.

Usage:
    codex_prp_executor.py <prp_path> [--model MODEL] [--timeout SECS] [--dry-run]

Output files (under /tmp/codex-prp-{name}-*):
    -prompt.txt     Generated prompt sent to Codex
    -result.json    Codex structured output (via -o flag)
    -output.log     Full terminal output (via tee)
    -report.json    Combined executor + validator report
    -done.json      Completion flag with metadata
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Resolve paths relative to this script
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_DIR = SKILL_DIR / "templates"

PROMPT_TEMPLATE = TEMPLATES_DIR / "codex-prp-prompt.md"
OUTPUT_SCHEMA = TEMPLATES_DIR / "codex-prp-output-schema.json"
AGENTS_TEMPLATE = TEMPLATES_DIR / "codex-prp-agents.md"
VALIDATOR_SCRIPT = SCRIPT_DIR / "codex_prp_validator.py"

CODEX_MODELS = [
    "gpt-5.3-codex",
    "gpt-5.2-codex",
    "gpt-5.1-codex-max",
]

DEFAULT_TIMEOUT = 600  # 10 minutes


def extract_prp_name(prp_path: str) -> str:
    """Extract a short name from PRP filename for temp file naming."""
    name = Path(prp_path).stem
    # Strip common prefixes
    for prefix in ("distill-", "prp-", "story_"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    return name


def extract_prp_metadata(prp_content: str) -> dict:
    """Extract metadata from PRP frontmatter-style headers."""
    metadata = {}

    source_match = re.search(r'\*\*Source\*\*:\s*`([^`]+)`', prp_content)
    if source_match:
        metadata["source"] = source_match.group(1)

    dest_match = re.search(r'\*\*File\*\*:\s*`([^`]+)`', prp_content)
    if dest_match:
        metadata["destination"] = dest_match.group(1)

    adapt_match = re.search(r'\*\*Adaptation\*\*:\s*(\S+)', prp_content)
    if adapt_match:
        metadata["adaptation"] = adapt_match.group(1)

    title_match = re.search(r'^# PRP:\s*(.+)$', prp_content, re.MULTILINE)
    if title_match:
        metadata["title"] = title_match.group(1).strip()

    return metadata


def build_prompt(prp_content: str) -> str:
    """Fill prompt template with PRP content."""
    template = PROMPT_TEMPLATE.read_text()
    return template.replace("{PRP_CONTENT}", prp_content)


def write_scoped_agents_md(prp_metadata: dict, repo_dir: str) -> Path | None:
    """Write a PRP-specific AGENTS.md to the target directory scope."""
    if not AGENTS_TEMPLATE.exists():
        return None

    dest = prp_metadata.get("destination", "")
    if not dest:
        return None

    # Determine scope directory (parent of destination file)
    dest_path = Path(repo_dir) / dest
    scope_dir = dest_path.parent
    agents_path = scope_dir / "AGENTS.md"

    # Don't overwrite existing AGENTS.md
    if agents_path.exists():
        return None

    template = AGENTS_TEMPLATE.read_text()
    content = template.replace("{PRP_NAME}", prp_metadata.get("title", "Unknown"))
    content = content.replace("{SOURCE_FILE_PATH}", prp_metadata.get("source", "N/A"))
    content = content.replace("{DESTINATION_PATH}", dest)
    content = content.replace("{ADAPTATION_TYPE}", prp_metadata.get("adaptation", "N/A"))

    scope_dir.mkdir(parents=True, exist_ok=True)
    agents_path.write_text(content)
    return agents_path


def build_codex_command(
    prompt_file: str,
    result_file: str,
    model: str,
    repo_dir: str,
) -> list[str]:
    """Build the codex exec command as a shell string."""
    schema_path = str(OUTPUT_SCHEMA)

    # Build the command pieces
    parts = [
        "codex", "exec",
        "--full-auto",
        "--skip-git-repo-check",
        "-m", model,
        "-o", result_file,
        "--output-schema", schema_path,
        "-C", repo_dir,
        "--add-dir", "/tmp",
    ]
    return parts


def run_codex_with_fallback(
    prompt_file: str,
    result_file: str,
    log_file: str,
    repo_dir: str,
    model: str | None,
    timeout: int,
) -> tuple[int, str]:
    """Run Codex with model fallback chain. Returns (exit_code, model_used)."""
    models = [model] if model else CODEX_MODELS.copy()

    prompt_content = Path(prompt_file).read_text()

    for i, m in enumerate(models):
        print(f"\n{'='*60}")
        print(f"Attempt {i+1}/{len(models)}: Codex with {m}")
        print(f"{'='*60}\n")

        cmd_parts = build_codex_command(prompt_file, result_file, m, repo_dir)

        # Build shell command with tee for logging
        # Pass prompt via stdin to avoid shell quoting issues
        shell_cmd = " ".join(f"'{p}'" if " " in p else p for p in cmd_parts)
        shell_cmd += f" - < '{prompt_file}'"
        shell_cmd += f" 2>&1 | tee -a '{log_file}'"

        try:
            result = subprocess.run(
                ["bash", "-c", shell_cmd],
                cwd=repo_dir,
                timeout=timeout,
            )
            if result.returncode == 0:
                print(f"\nCodex completed successfully with {m}")
                return 0, m
            else:
                print(f"\nCodex failed with {m} (exit code: {result.returncode})")
        except subprocess.TimeoutExpired:
            print(f"\nCodex timed out with {m} after {timeout}s")
        except FileNotFoundError:
            print("\nERROR: 'codex' command not found. Is Codex CLI installed?")
            return 1, m

        if i < len(models) - 1:
            print("Falling back to next model...")
            time.sleep(2)

    print("\nAll models failed.")
    return 1, models[-1]


def run_validation(result_file: str, prp_path: str, repo_dir: str, report_file: str) -> dict:
    """Run the independent validator."""
    if not VALIDATOR_SCRIPT.exists():
        return {"validation_status": "skipped", "notes": "Validator script not found"}

    cmd = [
        sys.executable, str(VALIDATOR_SCRIPT),
        "--result", result_file,
        "--prp", prp_path,
        "--repo", repo_dir,
        "--json-output", report_file,
    ]

    try:
        subprocess.run(cmd, timeout=120, capture_output=True)
        if Path(report_file).exists():
            return json.loads(Path(report_file).read_text())
    except Exception as e:
        return {"validation_status": "error", "notes": str(e)}

    return {"validation_status": "error", "notes": "Validator produced no output"}


def write_done_flag(
    done_file: str,
    exit_code: int,
    model_used: str,
    start_time: float,
    result_file: str,
    report_file: str,
    log_file: str,
):
    """Write completion flag with metadata."""
    duration = time.time() - start_time
    done = {
        "exit_code": exit_code,
        "model_used": model_used,
        "duration_seconds": round(duration, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "result_file": result_file,
        "report_file": report_file,
        "log_file": log_file,
    }
    Path(done_file).write_text(json.dumps(done, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Execute a PRP via Codex CLI with optimized flags and validation"
    )
    parser.add_argument("prp_path", help="Path to PRP file")
    parser.add_argument("--model", "-m", help="Codex model (default: fallback chain)")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    parser.add_argument("--repo", help="Repository root (default: cwd)")
    args = parser.parse_args()

    prp_path = Path(args.prp_path).resolve()
    repo_dir = args.repo or os.getcwd()

    if not prp_path.exists():
        print(f"ERROR: PRP not found: {prp_path}", file=sys.stderr)
        sys.exit(1)

    # Extract metadata
    prp_content = prp_path.read_text()
    prp_name = extract_prp_name(str(prp_path))
    prp_metadata = extract_prp_metadata(prp_content)

    # Set up file paths
    prefix = f"/tmp/codex-prp-{prp_name}"
    prompt_file = f"{prefix}-prompt.txt"
    result_file = f"{prefix}-result.json"
    log_file = f"{prefix}-output.log"
    report_file = f"{prefix}-report.json"
    done_file = f"{prefix}-done.json"

    # Build prompt
    prompt = build_prompt(prp_content)
    Path(prompt_file).write_text(prompt)
    print(f"Prompt written to {prompt_file} ({len(prompt)} chars)")

    # Write scoped AGENTS.md
    scoped_agents = write_scoped_agents_md(prp_metadata, repo_dir)
    if scoped_agents:
        print(f"Scoped AGENTS.md written to {scoped_agents}")

    # Build command for display
    model = args.model or CODEX_MODELS[0]
    cmd_parts = build_codex_command(prompt_file, result_file, model, repo_dir)
    print(f"\nCodex command:")
    print(f"  {' '.join(cmd_parts)} - < {prompt_file}")
    print(f"\nOutput files:")
    print(f"  Log:    {log_file}")
    print(f"  Result: {result_file}")
    print(f"  Report: {report_file}")
    print(f"  Done:   {done_file}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without executing.")
        # Cleanup scoped AGENTS.md
        if scoped_agents and scoped_agents.exists():
            scoped_agents.unlink()
        sys.exit(0)

    # Initialize log file
    Path(log_file).write_text(f"# Codex PRP Executor — {prp_name}\n# Started: {datetime.now().isoformat()}\n\n")

    start_time = time.time()

    # Run Codex
    exit_code, model_used = run_codex_with_fallback(
        prompt_file, result_file, log_file, repo_dir, args.model, args.timeout
    )

    # Run validation
    print(f"\n{'='*60}")
    print("Running independent validation...")
    print(f"{'='*60}\n")

    validation = run_validation(result_file, str(prp_path), repo_dir, report_file)

    # Write combined report
    combined = {
        "prp_name": prp_name,
        "prp_path": str(prp_path),
        "codex_exit_code": exit_code,
        "model_used": model_used,
        "validation": validation,
    }

    # Merge Codex result if available
    if Path(result_file).exists():
        try:
            codex_result = json.loads(Path(result_file).read_text())
            combined["codex_result"] = codex_result
        except json.JSONDecodeError:
            combined["codex_result_error"] = "Could not parse Codex output as JSON"

    Path(report_file).write_text(json.dumps(combined, indent=2))

    # Write done flag
    write_done_flag(done_file, exit_code, model_used, start_time, result_file, report_file, log_file)

    # Cleanup scoped AGENTS.md
    if scoped_agents and scoped_agents.exists():
        scoped_agents.unlink()
        print(f"Cleaned up scoped AGENTS.md: {scoped_agents}")

    # Summary
    v_status = validation.get("validation_status", "unknown")
    print(f"\n{'='*60}")
    print(f"COMPLETE: {prp_name}")
    print(f"  Codex exit: {exit_code}")
    print(f"  Model: {model_used}")
    print(f"  Validation: {v_status}")
    print(f"  Duration: {time.time() - start_time:.1f}s")
    print(f"  Report: {report_file}")
    print(f"  Done flag: {done_file}")
    print(f"{'='*60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
