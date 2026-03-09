---
name: opencode
description: |
  Delegate tasks to OpenCode CLI (multi-provider model access) with monitoring and result summary.

  Usage: /opencode <task description>

  Examples:
  /opencode implement pagination for the users API
  /opencode review the auth module for security issues
  /opencode analyze the database schema
  /opencode document the REST API
  /opencode research caching strategies
argument-hint: <task description>
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Write
  - Bash(*)
  - Glob
  - Grep
  - Skill
---

# OpenCode Delegator

**Task**: $ARGUMENTS

## Instructions

Read the agent definition at `.claude/agents/opencode-delegator.md` and follow its complete instructions to:

1. **Classify** the task type from the user's request above
2. **Check prerequisites** (OpenCode CLI installed)
3. **Gather context** relevant to the task (files, conventions)
4. **Construct** a structured OpenCode prompt
5. **Fork** execution to a new terminal via `fork_terminal.py`
6. **Monitor** for completion (poll done.json every 15 seconds)
7. **Summarize** results back to the user

If `$ARGUMENTS` is empty, display the help menu from the agent definition.

## Interactive Mode

Since this is a slash command invocation, enable interactive behaviors:

- **Progress updates**: Report status every ~60 seconds during monitoring
- **Clarification**: If the task description is ambiguous, ask the user before forking
- **Follow-up offers**: After reporting results, suggest next actions:
  - "Run `/code-review` on the changes?"
  - "Commit the changes?"
  - "View the full OpenCode output log?"

## Related

- `opencode-delegator` agent — Full orchestration logic (read this first)
- `fork-terminal` skill — Terminal forking mechanics
- `/orchestrate` — Alternative for OpenCode exploration + Codex implementation
- `/codex` — Delegate implementation tasks to Codex CLI
