# Purpose

Create a new Claude Code agent to execute the command.

## Variables

DEFAULT_MODEL: opus
HEAVY_MODEL: opus
BASE_MODEL: sonnet
FAST_MODEL: haiku

## Fallback Chain

If the primary model fails, try models in this order:
1. opus (default)
2. sonnet (fallback)
3. haiku (emergency fallback)

## Instructions

- Before executing the command, run `claude --help` to understand the command and its options.
- For the --model argument, use the DEFAULT_MODEL if not specified. If 'fast' is requested, use the FAST_MODEL. If 'heavy' is requested, use the HEAVY_MODEL.
- Always run with `--dangerously-skip-permissions`

## Mode: Non-Interactive (Default)

Use `-p` flag to pass the prompt directly for autonomous execution.

### Command Template

```bash
claude -p "PROMPT" --model MODEL --dangerously-skip-permissions
```

### Examples

**Basic execution:**
```bash
claude -p "analyze this codebase and summarize the architecture" --model opus --dangerously-skip-permissions
```

**Fast model for quick tasks:**
```bash
claude -p "PROMPT" --model haiku --dangerously-skip-permissions
```

## Mode: Interactive

Omit `-p` to open an interactive session for collaboration.

### Command Template

```bash
claude --model MODEL --dangerously-skip-permissions
```

### Examples

**Interactive session with opus:**
```bash
claude --model opus --dangerously-skip-permissions
```

**Interactive session with sonnet:**
```bash
claude --model sonnet --dangerously-skip-permissions
```
