#!/usr/bin/env -S uv run
"""Fork a new terminal window with a command."""

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Add .claude directory to path for utils import
_claude_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(_claude_dir))
from utils.logging import audit


def fork_terminal(command: str) -> str:
    """Open a new Terminal window and run the specified command."""
    system = platform.system()
    cwd = os.getcwd()

    # Audit log the fork attempt
    audit("fork_terminal", command=command, cwd=cwd, platform=system)

    if system == "Darwin":  # macOS
        # Build shell command - use single quotes for cd to avoid escaping issues
        # Then escape everything for AppleScript
        shell_command = f"cd '{cwd}' && {command}"
        # Escape for AppleScript: backslashes first, then quotes
        escaped_shell_command = shell_command.replace("\\", "\\\\").replace('"', '\\"')

        try:
            result = subprocess.run(
                ["osascript", "-e", f'tell application "Terminal" to do script "{escaped_shell_command}"'],
                capture_output=True,
                text=True,
            )
            output = f"stdout: {result.stdout.strip()}\nstderr: {result.stderr.strip()}\nreturn_code: {result.returncode}"
            return output
        except Exception as e:
            return f"Error: {str(e)}"

    elif system == "Windows":
        # Use /d flag to change drives if necessary
        full_command = f'cd /d "{cwd}" && {command}'
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", full_command], shell=True)
        return "Windows terminal launched"

    else:  # Linux
        # Supported terminal emulators in priority order
        terminals = [
            ("gnome-terminal", ["gnome-terminal", "--", "bash", "-c", f"cd '{cwd}' && {command}; exec bash"]),
            ("konsole", ["konsole", "-e", "bash", "-c", f"cd '{cwd}' && {command}; exec bash"]),
            ("xfce4-terminal", ["xfce4-terminal", "-e", f"bash -c \"cd '{cwd}' && {command}; exec bash\""]),
            ("alacritty", ["alacritty", "-e", "bash", "-c", f"cd '{cwd}' && {command}; exec bash"]),
            ("kitty", ["kitty", "bash", "-c", f"cd '{cwd}' && {command}; exec bash"]),
            ("xterm", ["xterm", "-e", "bash", "-c", f"cd '{cwd}' && {command}; exec bash"]),
        ]

        for terminal_name, cmd_array in terminals:
            if shutil.which(terminal_name):
                subprocess.Popen(cmd_array)
                return f"Linux terminal launched ({terminal_name})"

        raise NotImplementedError(
            "No supported terminal emulator found. Install one of: gnome-terminal, konsole, xfce4-terminal, alacritty, kitty, xterm"
        )


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        output = fork_terminal(" ".join(sys.argv[1:]))
        print(output)
