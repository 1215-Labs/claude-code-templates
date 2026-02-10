---
name: gemini
description: |
  Delegate exploration/analysis tasks to Google Gemini CLI with monitoring and result summary.

  Usage: /gemini <task description>

  Examples:
  /gemini explore the authentication system
  /gemini analyze the database schema
  /gemini review src/auth/ for security issues
  /gemini document the REST API
  /gemini research pagination strategies
  /gemini plan the PostgreSQL migration
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

# Gemini Delegator

**Task**: $ARGUMENTS

## Instructions

Read the agent definition at `.claude/agents/gemini-delegator.md` and follow its complete instructions to:

1. **Classify** the task type from the user's request above
2. **Check prerequisites** (Gemini CLI installed)
3. **Gather context** relevant to the task (files, directories, PR info)
4. **Construct** a structured Gemini prompt
5. **Fork** execution to a new terminal via `fork_terminal.py`
6. **Monitor** for completion (poll done.json every 15 seconds)
7. **Summarize** results back to the user

If `$ARGUMENTS` is empty, display the help menu from the agent definition.

## Interactive Mode

Since this is a slash command invocation, enable interactive behaviors:

- **Progress updates**: Report status every ~60 seconds during monitoring
- **Clarification**: If the task description is ambiguous, ask the user before forking
- **Follow-up offers**: After reporting results, suggest next actions:
  - "Delegate implementation to Codex? (`/codex`)"
  - "Explore another area? (`/gemini`)"
  - "View the full Gemini response?"
  - "Deep-dive into a specific finding?"

## Related

- `gemini-delegator` agent — Full orchestration logic (read this first)
- `fork-terminal` skill — Terminal forking mechanics
- `multi-model-orchestration` skill — Gemini/Codex orchestration patterns
- `/codex` — Implementation delegation (after Gemini exploration)
- `/orchestrate` — Combined explore-then-implement workflow
