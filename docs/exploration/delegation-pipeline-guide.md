# Multi-Model Delegation Pipeline Guide

**Last updated:** February 10, 2026
**Source:** DEC-004 (ecosystem merge), DEC-005 (auth gate fix)

## 1. Pipeline Overview

The delegation pipeline uses Claude (Sonnet) as an orchestrator that delegates work to external CLI agents:

1. **User** requests a task via `/codex` or `/gemini` slash command (or a parent agent invokes the delegator)
2. **Sonnet orchestrator** classifies the task, gathers context, and writes a prompt file to `/tmp/`
3. **Fork**: Orchestrator calls `fork_terminal.py` which launches the executor script in a detached xterm
4. **Executor script** (`codex_task_executor.py` or `gemini_task_executor.py`) invokes the CLI, captures output via `tee`, and writes `done.json` on completion
5. **Orchestrator polls** `done.json` every 15 seconds until completion or timeout
6. **Report**: Orchestrator reads results and reports back

Two-phase pattern: **Codex implements** (writes code), **Gemini validates** (reads and reviews). Each runs as an independent forked process.

## 2. Authentication

Both Codex and Gemini authenticate via OAuth. **Never gate on environment variables.**

| CLI | Auth Method | Env Var to IGNORE |
|-----|-------------|-------------------|
| Codex | GPT+ OAuth | `OPENAI_API_KEY` |
| Gemini | Google OAuth | `GEMINI_API_KEY` |

If a delegator agent checks for an API key and finds it missing, the Sonnet orchestrator will go off-script -- it may bypass the executor script entirely and run bare CLI commands without critical flags. Auth errors from the CLI itself surface in `output.log` at runtime; that is the correct detection point.

## 3. Critical Flags

| CLI | Flag | Purpose | Without It |
|-----|------|---------|------------|
| Codex | `--full-auto` | Write access + auto-approve all tool calls | Read-only sandbox, no file writes |
| Codex | `--skip-git-repo-check` | Bypass "not inside trusted directory" error | Command fails in non-trusted repos |
| Codex | `exec` subcommand | Non-interactive execution | Interactive session, hangs in forked terminal |
| Gemini | `--approval-mode yolo` | Auto-approve all tool calls | Interactive approval prompts, hangs |
| Gemini | `--output-format json` | Structured JSON response with stats | Freeform text output only |
| Gemini | `-p "$(cat prompt.txt)"` | Pass prompt via stdin from file | Must type prompt interactively |

## 4. Model Selection

| CLI | Default Model | Fast Model | Notes |
|-----|--------------|------------|-------|
| Codex | `gpt-5.3-codex` | `gpt-5.1-codex-mini` | Stable, no capacity issues observed |
| Gemini | `auto` | `gemini-2.5-flash` | `auto` routes between Pro and Flash by complexity |

Do NOT hardcode `gemini-3-pro-preview` -- it may return 429/RESOURCE_EXHAUSTED. Use `--model auto` as the safe default. If `auto` also fails (both Pro and Flash exhausted), retry after a delay or fall back to a different pipeline.

## 5. Failure Modes and Fixes

| Issue | Root Cause | Fix | Prevention |
|-------|-----------|-----|------------|
| **API key gate (Codex)** | `codex-delegator.md` Step 2 checked `OPENAI_API_KEY`, told Sonnet to abort if missing. Sonnet improvised bare `codex exec` without `--full-auto`, causing read-only sandbox. | Removed API key check from delegator agent. Added note: "Do NOT check for API keys." | Never gate delegator agents on env vars for OAuth-authenticated CLIs. |
| **API key gate (Gemini)** | `gemini-delegator.md` had identical `GEMINI_API_KEY` gate. Same risk of off-script behavior. | Same removal and documentation. | Same principle as above. |
| **Model capacity (429)** | `gemini-3-pro-preview` returned RESOURCE_EXHAUSTED. Gemini CLI retried 3 times, all failed. | Changed default model to `auto`. Added fallback guidance to delegator agent. | Default to `auto` for Gemini. Only use specific models when the user explicitly requests it. |
| **Executor not executable** | `codex_task_executor.py` and `gemini_task_executor.py` lacked `+x` permission. `uv run` with shebang requires executable bit. | `chmod +x` on both scripts. | Always set executable bit when creating Python scripts with UV shebangs (`#!/usr/bin/env -S uv run --script`). |

## 6. Monitoring

Poll `done.json` every 15 seconds, max 40 iterations (~10 minutes):

```
Iteration 1-3:   cat /tmp/{tool}-task-{slug}-done.json 2>/dev/null
Iteration 4:     Also read last 20 lines of output.log (progress check)
Iteration 5-7:   cat done.json only
Iteration 8:     Progress check again
...repeat...
Iteration 40:    Timeout — read last 50 lines of output.log, report failure
```

**Output file locations:**

| File | Codex | Gemini |
|------|-------|--------|
| Done flag | `/tmp/codex-task-{slug}-done.json` | `/tmp/gemini-task-{slug}-done.json` |
| Output log | `/tmp/codex-task-{slug}-output.log` | `/tmp/gemini-task-{slug}-output.log` |
| Results | `/tmp/codex-task-{slug}-summary.md` | `/tmp/gemini-task-{slug}-response.json` |

**Exit codes in done.json:** 0 = success, 124 = timeout, 127 = CLI not found.

## 7. Pre-flight Checklist

Before running the delegation pipeline:

1. [ ] CLI installed: `which codex` and/or `which gemini` returns a path
2. [ ] Executor scripts are executable: `ls -la .claude/skills/fork-terminal/tools/*_task_executor.py`
3. [ ] Prompt file written and non-empty: `wc -c /tmp/*-task-{slug}-prompt.txt`
4. [ ] No stale done.json: `rm -f /tmp/*-task-{slug}-done.json`
5. [ ] Model is `auto` for Gemini (not a specific model unless explicitly requested)
6. [ ] Codex command includes `--full-auto` and `--skip-git-repo-check`
7. [ ] Gemini command includes `--approval-mode yolo`
8. [ ] Working directory is the repo root (executor scripts use `cwd`)
9. [ ] Output directory exists: `mkdir -p docs/exploration/`
