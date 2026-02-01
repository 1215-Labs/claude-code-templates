# Purpose

Create a new Codex CLI agent to execute the command.

## Variables

DEFAULT_MODEL: gpt-5.2-codex
HEAVY_MODEL: gpt-5.2-codex
BASE_MODEL: gpt-5.2-codex
FAST_MODEL: gpt-5.2-codex-mini

## Codex Strengths

- Long-context understanding with native compaction
- State-of-the-art on SWE-Bench Pro (agentic coding)
- Reliable tool calling
- Best for: Implementation, refactoring, code changes, bug fixes

## Instructions

- Before executing the command, run `codex --help` to understand the command and its options.
- Always use interactive mode (so leave off -p and use positional prompt if needed)
- For the -m (model) argument, use the DEFAULT_MODEL if not specified. If 'fast' is requested, use the FAST_MODEL. If 'heavy' is requested, use the HEAVY_MODEL.
- Always run with `--dangerously-bypass-approvals-and-sandbox`
