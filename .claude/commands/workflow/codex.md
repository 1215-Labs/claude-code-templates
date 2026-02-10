---
name: codex
description: |
  Delegate tasks to OpenAI Codex CLI with monitoring and result summary.

  Usage: /codex <task description>

  Examples:
  /codex implement user profiles API
  /codex fix the failing GitHub Actions workflow
  /codex execute PRPs/distill-auth-middleware.md
  /codex security audit src/auth/
  /codex document the REST API
  /codex address review feedback on PR #42
  /codex write E2E tests for checkout
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

# Codex Delegator

**Task**: $ARGUMENTS

## Instructions

Read the agent definition at `.claude/agents/codex-delegator.md` and follow its complete instructions to:

1. **Classify** the task type from the user's request above
2. **Check prerequisites** (Codex CLI installed)
3. **Gather context** relevant to the task (files, PR info, CI status)
4. **Construct** a structured Codex prompt
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
  - "Validate in E2B sandbox?"
  - "Commit the changes?"
  - "View the full Codex output log?"

## Related

- `codex-delegator` agent — Full orchestration logic (read this first)
- `fork-terminal` skill — Terminal forking mechanics
- `agent-sandboxes` skill — E2B sandbox for test validation
- `/orchestrate` — Alternative for Gemini exploration + Codex implementation
