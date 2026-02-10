# Getting Started with Agent Sandboxes

Practical quick-start based on real-world testing (2026-02-09).

## Prerequisites

1. Set your E2B API key:
   ```bash
   export E2B_API_KEY="your-key-here"
   ```

2. Navigate to the CLI directory and install:
   ```bash
   cd .claude/skills/agent-sandboxes/sandbox_cli
   uv sync
   ```

## Basic Workflow

### 1. Create a Sandbox

```bash
# Quick start (10 min timeout)
uv run sbx init

# Long session with template
uv run sbx init --timeout 3600 --template fullstack-vue-fastapi-node22 --name my-test
```

Save the sandbox ID from the output.

### 2. Execute Commands

```bash
# Simple command
uv run sbx exec <SANDBOX_ID> "python3 --version"

# Compound commands (MUST use --shell)
uv run sbx exec <SANDBOX_ID> "apt-get update && apt-get install -y curl" --shell

# As root
uv run sbx exec <SANDBOX_ID> "apt-get install -y jq" --root
```

### 3. Install uv in Sandbox

uv/uvx are NOT pre-installed. Install them:

```bash
uv run sbx exec <SANDBOX_ID> "curl -LsSf https://astral.sh/uv/install.sh | sh" --shell
uv run sbx exec <SANDBOX_ID> "ln -sf /root/.local/bin/uv /usr/local/bin/uv && ln -sf /root/.local/bin/uvx /usr/local/bin/uvx" --shell
uv run sbx exec <SANDBOX_ID> "uv --version"
```

### 4. Upload and Execute Files

```bash
# Upload a script
uv run sbx files upload <SANDBOX_ID> ./my_script.py /home/user/my_script.py

# Execute it
uv run sbx exec <SANDBOX_ID> "python3 /home/user/my_script.py"

# Download results
uv run sbx files download <SANDBOX_ID> /home/user/output.txt ./output.txt
```

### 5. Upload/Download Directories

```bash
# Upload a project directory (auto-excludes .venv, node_modules, .git, etc.)
uv run sbx files upload-dir <SANDBOX_ID> ./my-project /home/user/my-project

# Download results
uv run sbx files download-dir <SANDBOX_ID> /home/user/my-project/results ./results
```

### 6. Get Public URL

```bash
# Start a server in the sandbox
uv run sbx exec <SANDBOX_ID> "cd /home/user/app && python3 -m http.server 8000" --background

# Get the public URL
uv run sbx sandbox get-host <SANDBOX_ID> --port 8000
```

### 7. Clean Up

```bash
uv run sbx sandbox kill <SANDBOX_ID>
```

## Known Quirks

### stderr is swallowed on failures

When a command fails, `sbx exec` shows "Aborted!" with no output. Workaround:

```bash
# Redirect stderr to a file, then read it
uv run sbx exec <SANDBOX_ID> "python3 bad_script.py > /tmp/out.txt 2>&1; echo EXIT_CODE=\$?" --shell
uv run sbx files read <SANDBOX_ID> /tmp/out.txt
```

### Compound commands need --shell

```bash
# This FAILS silently:
uv run sbx exec <SANDBOX_ID> "cd /tmp && ls"

# This WORKS:
uv run sbx exec <SANDBOX_ID> "cd /tmp && ls" --shell
```

### Extend sandbox lifetime

```bash
# Add 1 hour (3600 seconds)
uv run sbx sandbox extend-lifetime <SANDBOX_ID> 3600
```

## Cost Control

- Default timeout: 300s (5 min) - set higher with `--timeout`
- Maximum lifetime: 86400s (24 hr)
- Always kill sandboxes when done: `uv run sbx sandbox kill <ID>`
- Check running sandboxes: `uv run sbx sandbox list`
