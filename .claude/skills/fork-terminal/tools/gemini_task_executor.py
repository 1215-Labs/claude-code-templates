#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
Gemini Task Executor — Generic wrapper for Gemini CLI task execution.

Runs Gemini CLI with a pre-written prompt file, captures structured JSON output,
and writes a done.json completion flag for monitoring agents.

Features:
- Structured JSON output parsing with backward-scan for mixed output
- Error classification (QUOTA_EXHAUSTED, MODEL_CAPACITY, AUTH_FAILED, etc.)
- Retry with model fallback chain on 429 errors
- Auth mode support: oauth (default), api-key, vertex-ai
- Stale file cleanup to prevent collisions on retry

Usage:
    gemini_task_executor.py <prompt_path> -n <task_name> [-m MODEL] [-t SECS]
        [-I DIR]... [--auth-mode MODE] [--fallback-models M1,M2]
        [--retry-delay SECS] [--max-retries N] [--dry-run]

Output files (under /tmp/gemini-task-{name}-*):
    -output.log       Full terminal output (via tee)
    -response.json    Parsed JSON response (response, stats, error)
    -done.json        Completion flag with metadata (includes error_type)
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
DEFAULT_FALLBACK_MODELS = "gemini-2.5-flash"
DEFAULT_RETRY_DELAY = 15
DEFAULT_MAX_RETRIES = 2


def sanitize_slug(name: str) -> str:
    """Sanitize a task name into a filesystem-safe slug."""
    slug = name.lower().strip()
    slug = "".join(c if c.isalnum() else "-" for c in slug)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")[:50]


def classify_error(output: str, exit_code: int) -> str | None:
    """Classify the error type from Gemini CLI output and exit code."""
    if exit_code == 0:
        return None
    if exit_code == 124:
        return "TIMEOUT"
    if exit_code == 127:
        return "CLI_NOT_FOUND"

    output_lower = output.lower()
    if "429" in output or "resource_exhausted" in output_lower:
        if "model_capacity_exhausted" in output_lower:
            return "MODEL_CAPACITY"
        return "QUOTA_EXHAUSTED"
    if "authentication" in output_lower or "api key" in output_lower or "unauthorized" in output_lower:
        return "AUTH_FAILED"
    if "permission" in output_lower or "forbidden" in output_lower:
        return "PERMISSION_DENIED"

    return "UNKNOWN"


def build_auth_env(auth_mode: str) -> str:
    """Build environment variable exports for the chosen auth mode.

    Returns a shell prefix string (e.g., "export KEY=val && ").
    """
    if auth_mode == "api-key":
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if not api_key:
            print("WARNING: --auth-mode api-key but GEMINI_API_KEY not set", file=sys.stderr)
            return ""
        # Unset OAuth-related vars to force API key routing
        return (
            f"unset GOOGLE_APPLICATION_CREDENTIALS 2>/dev/null; "
            f"export GEMINI_API_KEY='{api_key}' && "
        )
    elif auth_mode == "vertex-ai":
        project = os.environ.get("GOOGLE_CLOUD_PROJECT", "")
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
        api_key = os.environ.get("GOOGLE_API_KEY", "")
        parts = ["export GOOGLE_GENAI_USE_VERTEXAI=true"]
        if project:
            parts.append(f"export GOOGLE_CLOUD_PROJECT='{project}'")
        if location:
            parts.append(f"export GOOGLE_CLOUD_LOCATION='{location}'")
        if api_key:
            parts.append(f"export GOOGLE_API_KEY='{api_key}'")
        return " && ".join(parts) + " && "
    else:  # oauth (default)
        api_key = os.environ.get("GEMINI_API_KEY", "")
        if api_key:
            return f"export GEMINI_API_KEY='{api_key}' && "
        return ""


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
    error_type: str | None = None,
    auth_mode: str = "oauth",
    retries_used: int = 0,
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
        "error_type": error_type,
        "auth_mode": auth_mode,
        "retries_used": retries_used,
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
    parser.add_argument("--auth-mode", choices=["oauth", "api-key", "vertex-ai"], default="oauth", help="Authentication mode (default: oauth)")
    parser.add_argument("--fallback-models", default=DEFAULT_FALLBACK_MODELS, help=f"Comma-separated fallback models on 429 (default: {DEFAULT_FALLBACK_MODELS})")
    parser.add_argument("--retry-delay", type=int, default=DEFAULT_RETRY_DELAY, help=f"Seconds between retries (default: {DEFAULT_RETRY_DELAY})")
    parser.add_argument("--max-retries", type=int, default=DEFAULT_MAX_RETRIES, help=f"Max retry attempts per model (default: {DEFAULT_MAX_RETRIES})")
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

    print(f"Task: {args.task_name}")
    print(f"Slug: {slug}")
    print(f"Model: {args.model}")
    print(f"Auth mode: {args.auth_mode}")
    print(f"Fallback models: {args.fallback_models}")
    print(f"Prompt: {prompt_path} ({prompt_path.stat().st_size} bytes)")
    if args.include_dirs:
        print(f"Include dirs: {', '.join(args.include_dirs)}")
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

    # Build model chain: primary model + fallback models
    model_chain = [args.model]
    if args.fallback_models:
        model_chain.extend(m.strip() for m in args.fallback_models.split(",") if m.strip())

    # Auth environment prefix
    auth_prefix = build_auth_env(args.auth_mode)

    exit_code = 1
    token_stats = None
    error_type = None
    model_used = args.model
    retries_used = 0

    for model_idx, current_model in enumerate(model_chain):
        for attempt in range(args.max_retries + 1):
            # Rebuild command for current model
            gemini_cmd = build_gemini_command(
                current_model, str(prompt_path), args.include_dirs or None
            )
            shell_cmd = f"set -o pipefail; {auth_prefix}{gemini_cmd} 2>&1 | tee -a '{log_file}'"

            attempt_label = f"model={current_model}, attempt {attempt + 1}/{args.max_retries + 1}"
            print(f"\n{'=' * 60}")
            print(f"Starting Gemini ({attempt_label})")
            print(f"{'=' * 60}\n")

            try:
                result = subprocess.run(
                    ["bash", "-c", shell_cmd],
                    cwd=repo_dir,
                    timeout=args.timeout,
                )
                exit_code = result.returncode
            except subprocess.TimeoutExpired:
                print(f"\nGemini timed out after {args.timeout}s")
                exit_code = 124
            except FileNotFoundError:
                print("\nERROR: 'gemini' command not found. Is Gemini CLI installed?")
                print("Install with: npm install -g @google/gemini-cli")
                exit_code = 127

            # Read output and classify error
            raw_output = Path(log_file).read_text() if Path(log_file).exists() else ""
            error_type = classify_error(raw_output, exit_code)
            model_used = current_model

            if exit_code == 0:
                print(f"\nGemini completed successfully")
                break  # Success — exit retry loop

            print(f"\nGemini exited with code {exit_code} (error_type={error_type})")
            retries_used += 1

            # Only retry on quota/capacity errors
            if error_type not in ("QUOTA_EXHAUSTED", "MODEL_CAPACITY"):
                break  # Non-retryable error

            # Don't sleep after last attempt of this model
            if attempt < args.max_retries:
                print(f"  Retrying in {args.retry_delay}s...")
                time.sleep(args.retry_delay)

        if exit_code == 0:
            break  # Success — exit model chain loop

        # If we exhausted retries for this model, try the next one
        if model_idx < len(model_chain) - 1:
            next_model = model_chain[model_idx + 1]
            print(f"\n  Falling back from {current_model} to {next_model}")

    # Parse JSON response from output log
    try:
        raw_output = Path(log_file).read_text() if Path(log_file).exists() else ""
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
        done_file, exit_code, model_used, start_time,
        response_file, log_file, slug, token_stats,
        error_type=error_type,
        auth_mode=args.auth_mode,
        retries_used=retries_used,
    )

    # Summary
    duration = time.time() - start_time
    response_exists = Path(response_file).exists()

    print(f"\n{'=' * 60}")
    print(f"COMPLETE: {args.task_name}")
    print(f"  Exit code: {exit_code}")
    print(f"  Model requested: {args.model}")
    print(f"  Model used: {model_used}")
    print(f"  Auth mode: {args.auth_mode}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Retries: {retries_used}")
    if error_type:
        print(f"  Error type: {error_type}")
    print(f"  Response: {'parsed' if response_exists else 'NOT parsed (check log)'}")
    if token_stats:
        print(f"  Tokens: {token_stats.get('prompt', '?')} in / {token_stats.get('candidates', '?')} out")
    print(f"  Done flag: {done_file}")
    print(f"{'=' * 60}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
