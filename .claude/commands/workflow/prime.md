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
---

# Context Priming

This command provides quick context about the codebase. It's an alias for `/quick-prime`.

## What It Does

1. Reads README.md and CLAUDE.md
2. Identifies tech stack and project structure
3. Summarizes key conventions
4. Provides getting started guidance

## When to Use

- **Starting a new session** - get oriented quickly
- **Returning after a break** - refresh your memory
- **Before making changes** - understand conventions

## When NOT to Use

- **Need deep analysis** - use `/deep-prime "<area>" "<focus>"` instead
- **New to the project** - use `/onboarding` for interactive guidance
- **Debugging an issue** - use `/rca "<error>"` instead
