---
name: workflow:prime
description: |
  Quick context priming - alias for /quick-prime.

  Usage: /prime

  Use for: Fast project context when starting work
  See also: /quick-prime (same), /deep-prime (deeper), /onboarding (interactive)
user-invocable: true
related:
  commands: [/quick-prime, /deep-prime, /onboarding]
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Context Priming

This command provides quick context about the codebase. It's an alias for `/quick-prime`.

## What It Does

1. Reads `.claude/INDEX.md` if present (preferred — lightweight progressive disclosure)
2. Falls back to CLAUDE.md + README.md if no INDEX.md exists
3. Identifies tech stack and project structure
4. Summarizes key conventions and critical paths

## When to Use

- **Starting a new session** - get oriented quickly
- **Returning after a break** - refresh your memory
- **Before making changes** - understand conventions

## When NOT to Use

- **Need deep analysis** - use `/deep-prime "<area>" "<focus>"` instead
- **New to the project** - use `/onboarding` for interactive guidance
- **Debugging an issue** - use `/rca "<error>"` instead
