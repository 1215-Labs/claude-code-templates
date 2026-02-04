#!/usr/bin/env -S uv run
"""Fork a new terminal window with a command.

Enhanced version with:
- Explicit API key propagation to forked terminals
- Output logging support
- Timestamp-based log files
"""

import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add .claude directory to path for utils import
_claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_dir))
try:
    from utils.logging import audit
except ImportError:
    # Fallback if utils not available (e.g., in test environment)
    def audit(event: str, **kwargs):
        pass

# API keys to propagate to forked terminals
API_KEYS_TO_PROPAGATE = [
    "GEMINI_API_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GOOGLE_API_KEY",
    "NVIDIA_API_KEY",
    "FEATHERLESS_API_KEY",
]


def _build_env_exports() -> str:
    """Build shell export commands for API keys that are set in the environment."""
    exports = []
    for key in API_KEYS_TO_PROPAGATE:
        value = os.environ.get(key)
        if value:
            # Escape any special characters in the value
            escaped_value = value.replace("'", "'\"'\"'")
            exports.append(f"export {key}='{escaped_value}'")
    return "; ".join(exports) + "; " if exports else ""


def _generate_log_filename(tool: str = "fork") -> str:
    """Generate a timestamp-based log filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"/tmp/fork_{tool}_{timestamp}.log"


def fork_terminal(command: str, log_output: bool = False, tool_name: str = "fork") -> str:
    """Open a new Terminal window and run the specified command.

    Args:
        command: The command to execute in the new terminal
        log_output: If True, tee output to a log file
        tool_name: Name of the tool for log file naming (e.g., 'codex', 'gemini')

    Returns:
        Status message indicating the terminal was launched
    """
    system = platform.system()
    cwd = os.getcwd()

    # Build environment export prefix for API keys
    env_prefix = _build_env_exports()

    # Build log suffix if logging is enabled
    log_file = None
    log_suffix = ""
    if log_output:
        log_file = _generate_log_filename(tool_name)
        log_suffix = f" 2>&1 | tee '{log_file}'"

    # Audit log the fork attempt
    audit("fork_terminal",
          command=command,
          cwd=cwd,
          platform=system,
          env_vars_propagated=bool(env_prefix),
          log_file=log_file)

    if system == "Darwin":  # macOS
        # Build shell command with env exports and optional logging
        shell_command = f"{env_prefix}cd '{cwd}' && {command}{log_suffix}"
        # Escape for AppleScript: backslashes first, then quotes
        escaped_shell_command = shell_command.replace("\\", "\\\\").replace('"', '\\"')

        try:
            result = subprocess.run(
                ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_shell_command}"'],
                capture_output=True,
                text=True,
            )
            output = f"stdout: {result.stdout.strip()}\nstderr: {result.stderr.strip()}\nreturn_code: {result.returncode}"
            if log_file:
                output += f"\nlog_file: {log_file}"
            return output
        except Exception as e:
            return f"Error: {str(e)}"

    elif system == "Windows":
        # Build command with env exports (Windows uses 'set' instead of 'export')
        env_sets = []
        for key in API_KEYS_TO_PROPAGATE:
            value = os.environ.get(key)
            if value:
                env_sets.append(f"set {key}={value}")
        env_prefix_win = " && ".join(env_sets) + " && " if env_sets else ""

        full_command = f'{env_prefix_win}cd /d "{cwd}" && {command}'
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", full_command], shell=True)
        return "Windows terminal launched"

    else:  # Linux
        # Build full command with env exports and optional logging
        full_command = f"{env_prefix}cd '{cwd}' && {command}{log_suffix}"

        # Supported terminal emulators in priority order
        terminals = [
            ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", f"{full_command}; exec bash"]),
            ("konsole", ["konsole", "-e", "bash", "-c", f"{full_command}; exec bash"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e", f"bash -c \"{full_command}; exec bash\""]),
            ("alacritty", ["alacritty", "-e", "bash", "-c", f"{full_command}; exec bash"]),
            ("kitty", ["kitty", "bash", "-c", f"{full_command}; exec bash"]),
            ("xterm", ["xterm", "-e", "bash", "-c", f"{full_command}; exec bash"]),
        ]

        for terminal_name, cmd_array in terminals:
            if shutil.which(terminal_name):
                subprocess.Popen(cmd_array)
                result = f"Linux terminal launched ({terminal_name})"
                if log_file:
                    result += f"\nlog_file: {log_file}"
                return result

        raise NotImplementedError(
            "No supported terminal emulator found. Install one of: gnome-terminal, konsole, xfce4-terminal, alacritty, kitty, xterm"
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fork a new terminal with a command")
    parser.add_argument("command", nargs="*", help="Command to execute")
    parser.add_argument("--log", "-l", action="store_true", help="Log output to file")
    parser.add_argument("--tool", "-t", default="fork", help="Tool name for log file")

    args = parser.parse_args()

    if args.command:
        output = fork_terminal(
            " ".join(args.command),
            log_output=args.log,
            tool_name=args.tool
        )
        print(output)
    else:
        parser.print_help()
