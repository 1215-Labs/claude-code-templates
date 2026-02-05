---
name: fork-terminal
description: Fork terminal to new window with Claude Code, Codex CLI, Gemini CLI, or raw commands.
version: 2.0.0
category: terminal
context: fork
user-invocable: true
allowed-tools:
  - Bash(*)
  - Read
related:
  agents: [context-manager]
  workflows: [feature-development]
---

# Purpose

Fork a terminal session to a new terminal window using agentic coding tools or raw CLI commands.

## When to Use

- **Independent parallel tasks** - run a separate agent on a different task
- **Long-running operations** - start a process without blocking current session
- **Multi-model work** - use Gemini or Codex for specific tasks
- **Isolated environments** - fresh terminal for specific work

## When NOT to Use

- **Dependent operations** - if task B needs task A's output, use single session
- **Simple commands** - just run them directly, no need to fork
- **State sharing needed** - forked terminals don't share context automatically
- **Every command** - forking has startup overhead, use judiciously

Follow the `Instructions`, execute the `Workflow`, based on the `Cookbook`.

## Variables

ENABLE_RAW_CLI_COMMANDS: true
ENABLE_GEMINI_CLI: true
ENABLE_CODEX_CLI: true
ENABLE_CLAUDE_CODE: true
AGENTIC_CODING_TOOLS: claude-code, codex-cli, gemini-cli

## Features (v2.0.0)

### Environment Variable Propagation
API keys are automatically propagated to forked terminals:
- GEMINI_API_KEY
- OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_API_KEY
- NVIDIA_API_KEY
- FEATHERLESS_API_KEY

### Output Logging
Enable output logging to capture terminal output for debugging:
```bash
# Use --log flag to tee output to /tmp/fork_<tool>_<timestamp>.log
python3 fork_terminal.py --log --tool codex "codex exec ..."
```

Log files are stored at: `/tmp/fork_<tool>_YYYYMMDD_HHMMSS.log`

### Non-Interactive Execution
All cookbooks now use non-interactive modes:
- **Codex**: `exec --full-auto --skip-git-repo-check`
- **Gemini**: `-p` (prompt mode) with `--approval-mode yolo`
- **Claude Code**: `--dangerously-skip-permissions`

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which tool to use.
- All agentic tools run in non-interactive mode to avoid prompts

### Fork Summary User Prompts

- IF: The user requests a fork terminal with a summary. This ONLY works for our agentic coding tools `AGENTIC_CODING_TOOLS`. The tool MUST BE enabled as well.
- THEN:
  - Read, and REPLACE the `.claude/skills/fork-terminal/prompts/fork_summary_user_prompt.md` with the history of the conversation between you and the user so far.
  - Include the next users request in the `Next User Request` section.
  - This will be what you pass into the PROMPT parameter of the agentic coding tool.
  - IMPORTANT: To be clear, don't update the file directly, just read it, fill it out IN YOUR MEMORY and use it to craft a new prompt in the structure provided for the new fork agent.
  - Let's be super clear here, the fork_summary_user_prompt.md is a template for you to fill out IN YOUR MEMORY. Once you've filled it out, pass that prompt to the agentic coding tool.
  - XML Tags have been added to let you know exactly what you need to replace. You'll be replacing the <fill in the history here> and <fill in the next user request here> sections.
- EXAMPLES:
  - "fork terminal use claude code to <xyz> summarize work so far"
  - "spin up a new terminal request <xyz> using claude code include summary"
  - "create a new terminal to <xyz> with claude code with summary"

### Output Logging

- IF: The user requests logging or you want to debug a fork
- THEN: Add `--log --tool <toolname>` to the fork_terminal.py invocation
- EXAMPLE: `python3 fork_terminal.py --log --tool codex "codex exec ..."`
- CHECK LOGS: `tail -f /tmp/fork_codex_*.log`

## Workflow

1. Understand the user's request.
2. READ: `.claude/skills/fork-terminal/tools/fork_terminal.py` to understand our tooling.
3. Follow the `Cookbook` to determine which tool to use.
4. Execute the `.claude/skills/fork-terminal/tools/fork_terminal.py: fork_terminal(command: str)` tool.

## Cookbook

### Raw CLI Commands

- IF: The user requests a non-agentic coding tool AND `ENABLE_RAW_CLI_COMMANDS` is true.
- THEN: Read and execute: `.claude/skills/fork-terminal/cookbook/cli-command.md`
- EXAMPLES:
  - "Create a new terminal to <xyz> with ffmpeg"
  - "Create a new terminal to <xyz> with curl"
  - "Create a new terminal to <xyz> with python"

### Claude Code

- IF: The user requests a claude code agent to execute the command AND `ENABLE_CLAUDE_CODE` is true.
- THEN: Read and execute: `.claude/skills/fork-terminal/cookbook/claude-code.md`
- EXAMPLES:
  - "fork terminal use claude code to <xyz>"
  - "spin up a new terminal request <xyz> using claude code"
  - "create a new terminal to <xyz> with claude code"

### Codex CLI

- IF: The user requests a codex CLI agent to execute the command AND `ENABLE_CODEX_CLI` is true.
- THEN: Read and execute: `.claude/skills/fork-terminal/cookbook/codex-cli.md`
- EXAMPLES:
  - "fork terminal use codex to <xyz>"
  - "spin up a new terminal request <xyz> using codex"
  - "create a new terminal to <xyz> with codex"

### Gemini CLI

- IF: The user requests a gemini CLI agent to execute the command AND `ENABLE_GEMINI_CLI` is true.
- THEN: Read and execute: `.claude/skills/fork-terminal/cookbook/gemini-cli.md`
- EXAMPLES:
  - "fork terminal use gemini to <xyz>"
  - "spin up a new terminal request <xyz> with gemini"
  - "create a new terminal to <xyz> using gemini"

## Dependencies

### Check Dependencies
```bash
bash ~/.claude/skills/fork-terminal/tools/check_dependencies.sh
```

### Install Dependencies
```bash
# Check what's missing
bash ~/.claude/skills/fork-terminal/tools/install_dependencies.sh --check

# Install all via apt (requires sudo)
bash ~/.claude/skills/fork-terminal/tools/install_dependencies.sh --all

# Install via Homebrew (no sudo needed)
bash ~/.claude/skills/fork-terminal/tools/install_dependencies.sh --brew
```

### Required Tools
| Tool | Purpose | Install |
|------|---------|---------|
| python3 | Core scripts | `apt install python3` |
| bash | Shell scripts | Usually pre-installed |
| xterm | Terminal emulator | `apt install xterm` |

### Optional Tools
| Tool | Purpose | Install |
|------|---------|---------|
| xdotool | Window detection | `apt install xdotool` |
| scrot | Screenshots | `apt install scrot` |
| imagemagick | Image processing | `apt install imagemagick` or `brew install imagemagick` |
| tree | Directory visualization | `apt install tree` or `brew install tree` |
| jq | JSON processing | `apt install jq` or `brew install jq` |

### Agentic CLI Tools
| Tool | Purpose | Install |
|------|---------|---------|
| codex | OpenAI Codex CLI | `npm install -g @openai/codex` |
| gemini | Google Gemini CLI | `npm install -g @google/gemini-cli` |
| claude | Claude Code CLI | `npm install -g @anthropic-ai/claude-code` |

### Installed Codex Skills
Codex has these skills available. Reference them in forked prompts for specialized tasks:
`/doc`, `/gh-address-comments`, `/gh-fix-ci`, `/openai-docs`, `/pdf`, `/playwright`,
`/screenshot`, `/security-best-practices`, `/security-ownership-map`, `/security-threat-model`

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Terminal stalls on prompt | Ensure using non-interactive mode (see cookbooks) |
| API key not found | Check that key is set in parent environment |
| "Not inside trusted directory" | Use `--skip-git-repo-check` for Codex |
| IDE integration nudge | Use `-p` instead of `-i` for Gemini |
| Can't see terminal output | Use `--log` flag, check `/tmp/fork_*.log` |

### Checking Logs

```bash
# List recent log files
ls -la /tmp/fork_*.log

# Tail a specific log
tail -f /tmp/fork_codex_*.log

# Check for errors
grep -i error /tmp/fork_*.log
```
