#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Codex Task Executor — Generic wrapper for non-PRP Codex task execution.

Runs Codex CLI with a pre-written prompt file, captures output via tee,
and writes a done.json completion flag for monitoring agents.

Unlike the PRP executor, this script:
- Does NOT use --output-schema (Codex writes freeform summary)
- Does NOT run a validator step
- Does NOT implement model fallback (caller handles retries)

Usage:
    codex_task_executor.py <prompt_path> -n <task_name> [-m MODEL] [-t SECS] [--dry-run]

Output files (under /tmp/codex-task-{name}-*):
    -output.log     Full terminal output (via tee)
    -summary.md     Codex's self-reported summary (written by Codex)
    -done.json      Completion flag with metadata
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "gpt-5.3-codex"
DEFAULT_TIMEOUT = 600  # 10 minutes


def sanitize_slug(name: str) -> str:
    """Sanitize a task name into a filesystem-safe slug."""
    slug = name.lower().strip()
    # Replace non-alphanumeric with hyphens
    slug = "".join(c if c.isalnum() else "-" for c in slug)
    # Collapse multiple hyphens and trim
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:50]


def build_codex_command(
    model: str,
    repo_dir: str,
) -> list[str]:
    """Build the codex exec command parts."""
    return [
        "codex", "exec",
        "--full-auto",
        "--skip-git-repo-check",
        "-m", model,
        "-C", repo_dir,
        "--add-dir", "/tmp",
    ]


def write_done_flag(
    done_file: str,
    exit_code: int,
    model: str,
    start_time: float,
    summary_file: str,
    log_file: str,
    task_name: str,
):
    """Write completion flag with metadata."""
    duration = time.time() - start_time
    done = {
        "exit_code": exit_code,
        "model_used": model,
        "duration_seconds": round(duration, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary_file": summary_file,
        "log_file": log_file,
        "task_name": task_name,
    }
    Path(done_file).write_text(json.dumps(done, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Execute a task via Codex CLI with output capture"
    )
    parser.add_argument("prompt_path", help="Path to prompt file")
    parser.add_argument("--task-name", "-n", required=True, help="Task name slug for output naming")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Codex model (default: {DEFAULT_MODEL})")
    parser.add_argument("--repo", "-C", help="Repository root (default: cwd)")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    prompt_path = Path(args.prompt_path).resolve()
    repo_dir = args.repo or os.getcwd()
    slug = sanitize_slug(args.task_name)

    if not prompt_path.exists():
        print(f"ERROR: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    # Set up output file paths
    prefix = f"/tmp/codex-task-{slug}"
    log_file = f"{prefix}-output.log"
    summary_file = f"{prefix}-summary.md"
    done_file = f"{prefix}-done.json"

    # Build command
    cmd_parts = build_codex_command(args.model, repo_dir)

    print(f"Task: {args.task_name}")
    print(f"Slug: {slug}")
    print(f"Model: {args.model}")
    print(f"Prompt: {prompt_path} ({prompt_path.stat().st_size} bytes)")
    print(f"\nCodex command:")
    print(f"  {' '.join(cmd_parts)} - < {prompt_path}")
    print(f"\nOutput files:")
    print(f"  Log:     {log_file}")
    print(f"  Summary: {summary_file}")
    print(f"  Done:    {done_file}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without executing.")
        sys.exit(0)

    # Clean stale output files from previous runs to prevent collisions
    for stale in [done_file, summary_file]:
        Path(stale).unlink(missing_ok=True)

    # Initialize log file
    Path(log_file).write_text(
        f"# Codex Task Executor — {args.task_name}\n"
        f"# Started: {datetime.now().isoformat()}\n"
        f"# Model: {args.model}\n\n"
    )

    start_time = time.time()

    # Build shell command: pipe prompt via stdin, tee output
    # pipefail ensures we get Codex's exit code, not tee's (always 0)
    shell_cmd = "set -o pipefail; "
    shell_cmd += " ".join(f"'{p}'" if " " in p else p for p in cmd_parts)
    shell_cmd += f" - < '{prompt_path}'"
    shell_cmd += f" 2>&1 | tee -a '{log_file}'"

    print(f"\n{'=' * 60}")
    print(f"Starting Codex with {args.model}")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(
            ["bash", "-c", shell_cmd],
            cwd=repo_dir,
            timeout=args.timeout,
        )
        exit_code = result.returncode
        if exit_code == 0:
            print(f"\nCodex completed successfully")
        else:
            print(f"\nCodex exited with code {exit_code}")
    except subprocess.TimeoutExpired:
        print(f"\nCodex timed out after {args.timeout}s")
        exit_code = 124  # Standard timeout exit code
    except FileNotFoundError:
        print("\nERROR: 'codex' command not found. Is Codex CLI installed?")
        print("Install with: npm install -g @openai/codex")
        exit_code = 127

    # Write done flag
    write_done_flag(done_file, exit_code, args.model, start_time, summary_file, log_file, slug)

    # Summary
    duration = time.time() - start_time
    summary_exists = Path(summary_file).exists()

    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {args.task_name}")
    print(f"  Exit code: {exit_code}")
    print(f"  Model: {args.model}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Summary: {'written' if summary_exists else 'NOT written (check log)'}")
    print(f"  Done flag: {done_file}")
    print(f"{'=' * 60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
