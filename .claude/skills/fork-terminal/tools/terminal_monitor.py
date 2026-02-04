#!/usr/bin/env python3
"""Terminal monitor for fork-terminal skill.

This is an OPTIONAL feature that requires additional dependencies:
    sudo apt install -y xdotool scrot imagemagick

The monitor can:
- List active terminal windows
- Take screenshots of terminals
- Check for known error patterns in terminal output
- Detect idle/stalled terminals
"""

import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Known error patterns to detect
ERROR_PATTERNS = [
    r"GEMINI_API_KEY\s+not\s+set",
    r"OPENAI_API_KEY\s+not\s+set",
    r"not inside trusted directory",
    r"Authentication failed",
    r"Rate limit exceeded",
    r"Connection refused",
    r"Timeout",
    r"Error:\s+\S+",
    r"FATAL:",
    r"panic:",
]


def check_dependencies() -> Tuple[bool, List[str]]:
    """Check if required tools are available."""
    missing = []
    tools = ["xdotool", "scrot"]

    for tool in tools:
        if not shutil.which(tool):
            missing.append(tool)

    return len(missing) == 0, missing


def get_terminal_windows() -> List[dict]:
    """Get list of terminal windows with their IDs and titles."""
    if not shutil.which("xdotool"):
        return []

    try:
        # Search for common terminal emulators
        terminals = []
        for term_class in ["xterm", "gnome-terminal", "konsole", "alacritty", "kitty"]:
            result = subprocess.run(
                ["xdotool", "search", "--class", term_class],
                capture_output=True,
                text=True,
                timeout=5
            )
            for window_id in result.stdout.strip().split("\n"):
                if window_id:
                    # Get window title
                    title_result = subprocess.run(
                        ["xdotool", "getwindowname", window_id],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    terminals.append({
                        "id": window_id,
                        "class": term_class,
                        "title": title_result.stdout.strip()
                    })
        return terminals
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return []


def take_screenshot(window_id: Optional[str] = None, output_path: Optional[str] = None) -> Optional[str]:
    """Take a screenshot of a specific window or the entire screen.

    Args:
        window_id: X11 window ID (if None, captures entire screen)
        output_path: Path to save screenshot (auto-generated if None)

    Returns:
        Path to screenshot or None on failure

    Note:
        In WSL2, focused window capture (-u) may fail. Falls back to
        full screen capture which is more reliable for unattended use.
    """
    if not shutil.which("scrot"):
        print("Error: scrot not installed")
        return None

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = f"_{window_id}" if window_id else "_screen"
        output_path = f"/tmp/terminal{suffix}_{timestamp}.png"

    try:
        if window_id and shutil.which("xdotool"):
            # Try to focus and capture specific window
            subprocess.run(
                ["xdotool", "windowactivate", "--sync", window_id],
                capture_output=True,
                timeout=5
            )
            result = subprocess.run(
                ["scrot", "-u", output_path],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and os.path.exists(output_path):
                return output_path
            # Fall through to full screen capture on failure

        # Full screen capture (more reliable in WSL2)
        result = subprocess.run(
            ["scrot", output_path],
            capture_output=True,
            timeout=10
        )

        if os.path.exists(output_path):
            return output_path

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError) as e:
        print(f"Error taking screenshot: {e}")

    return None


def check_log_for_errors(log_path: str) -> List[Tuple[str, str]]:
    """Check a log file for known error patterns.

    Args:
        log_path: Path to log file

    Returns:
        List of (pattern, matching_line) tuples
    """
    errors = []

    if not os.path.exists(log_path):
        return errors

    try:
        with open(log_path, "r") as f:
            content = f.read()

        for pattern in ERROR_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # Get the full line containing the match
                start = content.rfind("\n", 0, match.start()) + 1
                end = content.find("\n", match.end())
                if end == -1:
                    end = len(content)
                line = content[start:end].strip()
                errors.append((pattern, line))
    except Exception as e:
        print(f"Error reading log: {e}")

    return errors


def get_recent_logs(pattern: str = "fork_*.log", directory: str = "/tmp") -> List[str]:
    """Get list of recent fork log files.

    Args:
        pattern: Glob pattern for log files
        directory: Directory to search

    Returns:
        List of log file paths, sorted by modification time
    """
    from glob import glob

    log_files = glob(os.path.join(directory, pattern))
    # Sort by modification time, newest first
    log_files.sort(key=os.path.getmtime, reverse=True)
    return log_files


def monitor_status() -> dict:
    """Get overall monitoring status.

    Returns:
        dict with:
        - dependencies_ok: bool
        - missing_deps: list of missing tools
        - terminal_count: number of detected terminals
        - terminals: list of terminal info
        - recent_logs: list of recent log files
        - errors_found: list of (log_file, errors) tuples
    """
    deps_ok, missing = check_dependencies()

    status = {
        "dependencies_ok": deps_ok,
        "missing_deps": missing,
        "terminal_count": 0,
        "terminals": [],
        "recent_logs": [],
        "errors_found": []
    }

    if deps_ok:
        terminals = get_terminal_windows()
        status["terminal_count"] = len(terminals)
        status["terminals"] = terminals

    # Check logs regardless of deps
    logs = get_recent_logs()[:10]  # Last 10 logs
    status["recent_logs"] = logs

    for log_file in logs[:5]:  # Check 5 most recent
        errors = check_log_for_errors(log_file)
        if errors:
            status["errors_found"].append({
                "log": log_file,
                "errors": errors
            })

    return status


def print_status():
    """Print human-readable monitoring status."""
    status = monitor_status()

    print("=" * 50)
    print("Fork-Terminal Monitor Status")
    print("=" * 50)
    print()

    # Dependencies
    if status["dependencies_ok"]:
        print("Dependencies: OK")
    else:
        print(f"Dependencies: MISSING - {', '.join(status['missing_deps'])}")
        print("  Install with: sudo apt install -y xdotool scrot imagemagick")
    print()

    # Terminals
    print(f"Terminal Windows: {status['terminal_count']}")
    for term in status["terminals"]:
        print(f"  [{term['id']}] {term['class']}: {term['title']}")
    print()

    # Recent logs
    print(f"Recent Logs: {len(status['recent_logs'])}")
    for log in status["recent_logs"][:5]:
        mtime = datetime.fromtimestamp(os.path.getmtime(log))
        print(f"  {os.path.basename(log)} ({mtime.strftime('%H:%M:%S')})")
    print()

    # Errors
    if status["errors_found"]:
        print("Errors Found:")
        for entry in status["errors_found"]:
            print(f"  {os.path.basename(entry['log'])}:")
            for pattern, line in entry["errors"][:3]:  # Show first 3
                print(f"    - {line[:60]}...")
    else:
        print("Errors Found: None")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fork-terminal monitor")
    parser.add_argument("--status", action="store_true", help="Show monitoring status")
    parser.add_argument("--screenshot", metavar="WINDOW_ID", help="Take screenshot of window")
    parser.add_argument("--check-log", metavar="LOG_FILE", help="Check log file for errors")
    parser.add_argument("--list-terminals", action="store_true", help="List terminal windows")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    if args.json:
        import json
        print(json.dumps(monitor_status(), indent=2))
    elif args.status:
        print_status()
    elif args.screenshot:
        path = take_screenshot(args.screenshot)
        if path:
            print(f"Screenshot saved: {path}")
        else:
            print("Failed to take screenshot")
            sys.exit(1)
    elif args.check_log:
        errors = check_log_for_errors(args.check_log)
        if errors:
            for pattern, line in errors:
                print(f"[{pattern}] {line}")
        else:
            print("No errors found")
    elif args.list_terminals:
        terminals = get_terminal_windows()
        for term in terminals:
            print(f"{term['id']}\t{term['class']}\t{term['title']}")
    else:
        print_status()
