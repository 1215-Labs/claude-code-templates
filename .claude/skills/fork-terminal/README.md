# Fork Terminal

Fork terminal sessions to new windows with various CLI agents or raw commands.

---

## Purpose

Enables spawning new terminal windows with Claude Code, Codex CLI, Gemini CLI, or raw CLI commands, optionally including conversation context summaries.

## Activates On

- Fork terminal
- New terminal window
- Spawn CLI agent
- Claude Code in new terminal
- Codex CLI
- Gemini CLI

## File Count

7 files across 4 directories

## Core Capabilities

### Agent Forking
Launch Claude Code, Codex CLI, or Gemini CLI in a new terminal with optional context.

### Raw Command Execution
Fork a terminal with any CLI command (ffmpeg, curl, python, etc.).

### Context Summarization
Optionally pass conversation summary to the new agent for continuity.

## Supported Agents

| Agent | Flag | Description |
|-------|------|-------------|
| Claude Code | ENABLE_CLAUDE_CODE | Anthropic's CLI |
| Codex CLI | ENABLE_CODEX_CLI | OpenAI's Codex |
| Gemini CLI | ENABLE_GEMINI_CLI | Google's Gemini |
| Raw Commands | ENABLE_RAW_CLI_COMMANDS | Any CLI tool |

## Platform Support

- **macOS**: Uses AppleScript with Terminal.app
- **Windows**: Uses cmd.exe with start command
- **Linux**: Supports gnome-terminal, konsole, xfce4-terminal, alacritty, kitty, xterm

## Directory Structure

```
fork-terminal/
├── SKILL.md           # Main skill instructions
├── README.md          # This file
├── cookbook/          # Agent-specific instructions
│   ├── claude-code.md
│   ├── codex-cli.md
│   ├── gemini-cli.md
│   └── cli-command.md
├── prompts/           # Prompt templates
│   └── fork_summary_user_prompt.md
└── tools/             # Implementation
    └── fork_terminal.py
```

## Related Components

- **Agents**: context-manager
- **Workflows**: feature-development

---

**Part of**: claude-code-templates
