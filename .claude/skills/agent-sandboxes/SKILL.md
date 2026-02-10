---
name: agent-sandboxes
description: |
  E2B sandbox CLI for isolated code execution in agent workflows.
  Use when agents need to execute untrusted code, test in clean environments,
  or prototype full-stack apps with public URLs.
  Examples: "run this in a sandbox", "test in isolation", "create a sandbox"
version: 1.0.0
category: sandbox
user-invocable: true
allowed-tools:
  - Bash(*)
related:
  agents: [test-automator, debugger, deployment-engineer]
  skills: [fork-terminal, agent-browser]
---

# Purpose

Manage E2B sandboxes for isolated code execution in agent workflows. Provides a CLI (`sbx`) for creating sandboxes, executing commands, managing files, and exposing public URLs.

## When to Use

- **Isolated code execution** - run untrusted or experimental code without local risk
- **Clean test environments** - test components in fresh environments with no local pollution
- **Full-stack prototyping** - scaffold apps with public URLs in minutes
- **Multi-agent sandboxes** - each agent tracks its own sandbox ID, no conflicts
- **"Best of N" pattern** - spin up N sandboxes with different models, compare results

## When NOT to Use

- **Simple local scripts** - no isolation needed, just run locally
- **Browser automation** - use `agent-browser` skill instead
- **Persistent infrastructure** - sandboxes auto-expire (max 24 hours)

## Prerequisites

1. **E2B API Key**: Set `E2B_API_KEY` environment variable (get from [e2b.dev](https://e2b.dev))
2. **uv**: Required to run the CLI (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

## Quick Start

```bash
# Navigate to the skill's CLI directory
cd .claude/skills/agent-sandboxes/sandbox_cli

# Install dependencies
uv sync

# Create a sandbox (10 min default timeout)
uv run sbx init

# Create with longer timeout and template
uv run sbx init --timeout 3600 --template fullstack-vue-fastapi-node22

# Execute a command
uv run sbx exec <SANDBOX_ID> "python3 --version"

# Execute with shell features (pipes, &&, redirections)
uv run sbx exec <SANDBOX_ID> "ls -la | grep py" --shell

# Upload a file
uv run sbx files upload <SANDBOX_ID> ./local-file.py /home/user/remote-file.py

# Download a file
uv run sbx files download <SANDBOX_ID> /home/user/output.txt ./output.txt

# Get public URL for a running service
uv run sbx sandbox get-host <SANDBOX_ID> --port 5173

# Kill the sandbox when done
uv run sbx sandbox kill <SANDBOX_ID>
```

## Cost Model

| Tier | vCPUs | RAM | Disk | Rate |
|------|-------|-----|------|------|
| Default | 2 | 512 MB | 1 GB | $0.13/hr |
| Lite | 1 | 256 MB | 512 MB | ~$0.07/hr |
| Standard | 4 | 1 GB | 5 GB | ~$0.26/hr |
| Max | 8 | 4 GB | 20 GB | ~$0.44/hr |

**Budget tip**: Use `--timeout` to auto-kill sandboxes. Default is 300s (5 min). Max is 86400s (24 hr).

## CLI Commands

| Command | Description |
|---------|-------------|
| `sbx init` | Create a new sandbox, print ID |
| `sbx exec <ID> "cmd"` | Execute command in sandbox |
| `sbx sandbox create` | Create sandbox with full options |
| `sbx sandbox kill <ID>` | Kill a sandbox |
| `sbx sandbox info <ID>` | Get sandbox info + metrics |
| `sbx sandbox status <ID>` | Check if sandbox is running |
| `sbx sandbox list` | List all running sandboxes |
| `sbx sandbox get-host <ID> -p PORT` | Get public URL for port |
| `sbx sandbox pause <ID>` | Pause sandbox (beta) |
| `sbx sandbox extend-lifetime <ID> SECS` | Add time to sandbox |
| `sbx files ls <ID> [PATH]` | List files |
| `sbx files read <ID> PATH` | Read file contents |
| `sbx files write <ID> PATH CONTENT` | Write to file |
| `sbx files edit <ID> PATH --old X --new Y` | Edit file |
| `sbx files upload <ID> LOCAL REMOTE` | Upload file |
| `sbx files download <ID> REMOTE LOCAL` | Download file |
| `sbx files upload-dir <ID> LOCAL REMOTE` | Upload directory |
| `sbx files download-dir <ID> REMOTE LOCAL` | Download directory |

## Known Quirks

These were discovered during hands-on testing (2026-02-09):

1. **uv/uvx not pre-installed in sandbox**: Install with `curl -LsSf https://astral.sh/uv/install.sh | sh` then symlink to PATH
2. **stderr swallowed on non-zero exit**: `sbx exec` shows "Aborted!" with no output. Workaround: redirect stderr to file and read it separately
3. **`--shell` required for compound commands**: `&&`, pipes, and redirections need `--shell` flag
4. **Auto-timeout**: Sandboxes auto-kill after timeout. Use `extend-lifetime` to add time

## Architecture

```
sandbox_cli/
├── pyproject.toml          # 4 deps: e2b, click, rich, python-dotenv
├── src/
│   ├── __init__.py
│   ├── main.py             # CLI entry point (no browser)
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── sandbox.py      # Lifecycle: create, kill, connect, info, etc.
│   │   ├── files.py        # All file operations
│   │   └── exec.py         # Command execution
│   └── modules/
│       ├── __init__.py
│       ├── sandbox.py      # Sandbox CRUD logic
│       ├── files.py        # File I/O logic
│       └── commands.py     # Exec logic
```

Extracted from `references/agent-sandbox-skill` with browser automation removed (use `agent-browser` skill instead).
