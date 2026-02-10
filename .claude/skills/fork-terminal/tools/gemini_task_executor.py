#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Gemini Task Executor — Generic wrapper for Gemini CLI task execution.

Runs Gemini CLI with a pre-written prompt file, captures structured JSON output,
and writes a done.json completion flag for monitoring agents.

Key differences from the Codex task executor:
- Uses --output-format json for structured response + stats
- Parses JSON to write -response.json (not freeform summary)
- Default model is 'auto' (Gemini auto-routes between Pro and Flash)
- Supports --include-directories for multi-directory exploration
- Relies on Gemini's built-in fallback handler (no manual fallback chain)

Usage:
    gemini_task_executor.py <prompt_path> -n <task_name> [-m MODEL] [-t SECS] [-I DIR]... [--dry-run]

Output files (under /tmp/gemini-task-{name}-*):
    -output.log       Full terminal output (via tee)
    -response.json    Parsed JSON response (response, stats, error)
    -done.json        Completion flag with metadata
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MODEL = "auto"
DEFAULT_TIMEOUT = 600  # 10 minutes


def sanitize_slug(name: str) -> str:
    """Sanitize a task name into a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = "".join(c if c.isalnum() else "-" for c in slug)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:50]


def build_gemini_command(
    model: str,
    prompt_path: str,
    include_dirs: list[str] | None = None,
) -> str:
    """Build the gemini CLI shell command string."""
    parts = [
        "gemini",
        f'-p "$(cat \'{prompt_path}\')"',
        f"--model {model}",
        "--approval-mode yolo",
        "--output-format json",
    ]
    if include_dirs:
        dirs_csv = ",".join(include_dirs)
        parts.append(f"--include-directories {dirs_csv}")
    return " ".join(parts)


def parse_gemini_json(output: str) -> dict | None:
    """Extract the JSON response from Gemini's --output-format json output.

    Gemini may emit non-JSON output (progress, tool calls) before the final
    JSON block. We scan backwards for the last complete JSON object.
    """
    # Try parsing the entire output first (clean case)
    stripped = output.strip()
    if stripped.startswith("{"):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # Scan backwards for last JSON block
    last_brace = stripped.rfind("}")
    if last_brace == -1:
        return None

    # Try increasingly larger substrings ending at the last brace
    for i in range(last_brace, -1, -1):
        if stripped[i] == "{":
            candidate = stripped[i : last_brace + 1]
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict) and "response" in parsed:
                    return parsed
            except json.JSONDecodeError:
                continue

    return None


def write_done_flag(
    done_file: str,
    exit_code: int,
    model: str,
    start_time: float,
    response_file: str,
    log_file: str,
    task_name: str,
    token_stats: dict | None = None,
):
    """Write completion flag with metadata."""
    duration = time.time() - start_time
    done = {
        "exit_code": exit_code,
        "model_used": model,
        "duration_seconds": round(duration, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "response_file": response_file,
        "log_file": log_file,
        "task_name": task_name,
    }
    if token_stats:
        done["tokens"] = token_stats
    Path(done_file).write_text(json.dumps(done, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Execute a task via Gemini CLI with structured JSON output"
    )
    parser.add_argument("prompt_path", help="Path to prompt file")
    parser.add_argument("--task-name", "-n", required=True, help="Task name slug for output naming")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"Gemini model or alias (default: {DEFAULT_MODEL})")
    parser.add_argument("--repo", "-C", help="Repository root (default: cwd)")
    parser.add_argument("--timeout", "-t", type=int, default=DEFAULT_TIMEOUT, help="Timeout in seconds")
    parser.add_argument("--include-dirs", "-I", action="append", default=[], help="Additional directories (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    prompt_path = Path(args.prompt_path).resolve()
    repo_dir = args.repo or os.getcwd()
    slug = sanitize_slug(args.task_name)

    if not prompt_path.exists():
        print(f"ERROR: Prompt file not found: {prompt_path}", file=sys.stderr)
        sys.exit(1)

    # Set up output file paths
    prefix = f"/tmp/gemini-task-{slug}"
    log_file = f"{prefix}-output.log"
    response_file = f"{prefix}-response.json"
    done_file = f"{prefix}-done.json"

    # Build command
    gemini_cmd = build_gemini_command(
        args.model, str(prompt_path), args.include_dirs or None
    )

    print(f"Task: {args.task_name}")
    print(f"Slug: {slug}")
    print(f"Model: {args.model}")
    print(f"Prompt: {prompt_path} ({prompt_path.stat().st_size} bytes)")
    if args.include_dirs:
        print(f"Include dirs: {', '.join(args.include_dirs)}")
    print(f"\nGemini command:")
    print(f"  {gemini_cmd}")
    print(f"\nOutput files:")
    print(f"  Log:      {log_file}")
    print(f"  Response: {response_file}")
    print(f"  Done:     {done_file}")

    if args.dry_run:
        print("\n[DRY RUN] Exiting without executing.")
        sys.exit(0)

    # Clean stale output files from previous runs to prevent collisions
    for stale in [done_file, response_file]:
        Path(stale).unlink(missing_ok=True)

    # Initialize log file
    Path(log_file).write_text(
        f"# Gemini Task Executor — {args.task_name}\n"
        f"# Started: {datetime.now().isoformat()}\n"
        f"# Model: {args.model}\n\n"
    )

    start_time = time.time()

    # Build full shell command with API key export and tee
    # pipefail ensures we get Gemini's exit code, not tee's (always 0)
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
    env_export = f"export GEMINI_API_KEY='{gemini_api_key}' && " if gemini_api_key else ""
    shell_cmd = f"set -o pipefail; {env_export}{gemini_cmd} 2>&1 | tee -a '{log_file}'"

    print(f"\n{'=' * 60}")
    print(f"Starting Gemini with {args.model}")
    print(f"{'=' * 60}\n")

    try:
        result = subprocess.run(
            ["bash", "-c", shell_cmd],
            cwd=repo_dir,
            timeout=args.timeout,
        )
        exit_code = result.returncode
        if exit_code == 0:
            print(f"\nGemini completed successfully")
        else:
            print(f"\nGemini exited with code {exit_code}")
    except subprocess.TimeoutExpired:
        print(f"\nGemini timed out after {args.timeout}s")
        exit_code = 124
    except FileNotFoundError:
        print("\nERROR: 'gemini' command not found. Is Gemini CLI installed?")
        print("Install with: npm install -g @google/gemini-cli")
        exit_code = 127

    # Parse JSON response from output log
    token_stats = None
    try:
        raw_output = Path(log_file).read_text()
        parsed = parse_gemini_json(raw_output)
        if parsed:
            Path(response_file).write_text(json.dumps(parsed, indent=2))
            # Extract token stats if available
            stats = parsed.get("stats", {})
            if stats:
                models = stats.get("models", {})
                for model_name, model_stats in models.items():
                    tokens = model_stats.get("tokens", {})
                    if tokens:
                        token_stats = {
                            "model": model_name,
                            "prompt": tokens.get("prompt", 0),
                            "candidates": tokens.get("candidates", 0),
                            "total": tokens.get("total", 0),
                            "cached": tokens.get("cached", 0),
                        }
                        break  # Use first model's stats
            print(f"  Response JSON parsed and written to {response_file}")
        else:
            print(f"  WARNING: Could not parse JSON from Gemini output")
    except Exception as e:
        print(f"  WARNING: Error parsing output: {e}")

    # Write done flag
    write_done_flag(
        done_file, exit_code, args.model, start_time,
        response_file, log_file, slug, token_stats
    )

    # Summary
    duration = time.time() - start_time
    response_exists = Path(response_file).exists()

    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {args.task_name}")
    print(f"  Exit code: {exit_code}")
    print(f"  Model: {args.model}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Response: {'parsed' if response_exists else 'NOT parsed (check log)'}")
    if token_stats:
        print(f"  Tokens: {token_stats.get('prompt', '?')} in / {token_stats.get('candidates', '?')} out")
    print(f"  Done flag: {done_file}")
    print(f"{'=' * 60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
