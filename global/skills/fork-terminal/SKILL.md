---
name: fork-terminal
description: Fork terminal to new window with Claude Code, Codex CLI, Gemini CLI, or raw commands.
version: 1.2.0
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

## Instructions

- Based on the user's request, follow the `Cookbook` to determine which tool to use.

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

## Output Conventions for Orchestration

When forking agentic tools for multi-model orchestration:

### File-Based Results

Forked agents write results to predictable locations:
```
docs/
├── exploration/           # Gemini outputs
│   └── {task-name}.md     # Comprehensive analysis (progressive disclosure format)
└── implementation/        # Codex outputs
    └── {task-name}-log.md # Implementation notes, files changed
```

### Prompt Structure for Orchestrated Forks

1. **Specify output location** in prompt (docs/exploration/ or docs/implementation/)
2. **Request structured output** using the appropriate format:
   - Exploration: Executive Summary, Critical Files, Findings, Recommendations
   - Implementation: Files Changed, Tests Added, Validation Results
3. **Include validation commands** for implementation tasks
4. **Reference output location** so orchestrator can read results

### Example Orchestration Prompt

```
Explore the authentication system in this codebase.
Write your findings to docs/exploration/auth-system.md using progressive disclosure format:
- Executive Summary (2-3 sentences)
- Quick Reference table
- Critical Files with line numbers
- Patterns & Conventions
- Recommendations for implementation
```

See also: `.claude/skills/multi-model-orchestration/SKILL.md` for complete orchestration patterns.
