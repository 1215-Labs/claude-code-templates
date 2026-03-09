# Purpose

Create a new OpenCode CLI agent to execute the command.

## Variables

DEFAULT_MODEL: openai/gpt-5.3-codex
HEAVY_MODEL: openai/gpt-5.3-codex
BASE_MODEL: openai/gpt-5.2
FREE_MODEL: opencode/glm-5-free
CHEAP_MODEL: opencode/kimi-k2.5

## OpenCode Strengths

- Multi-provider model access (OpenAI, GLM, Kimi, Antigravity)
- oh-my-opencode agent harness (pre-configured model+variant+permissions)
- Cost-conscious: flat-rate OpenAI models via ChatGPT Pro, free GLM/Kimi tiers
- Best for: Implementation, code review, analysis, documentation

## COST RULE

**NEVER use `opencode/claude-*` models** — they are API-billed and incur Anthropic costs.
For Claude tasks, fork to Toad (Claude Code on Max Plan) instead.

The `opencode_task_executor.py` enforces this by blocking these models at startup.

## Available Models

| Model ID | Tier | Best For |
|---|---|---|
| `openai/gpt-5.3-codex` | Flat rate | Implementation, coding |
| `openai/gpt-5.2` | Flat rate | Analysis, reasoning, review |
| `opencode/gpt-5` | Included | General tasks |
| `opencode/gpt-5-nano` | Included | Simple/fast tasks |
| `opencode/glm-5-free` | Free | Implementation fallback |
| `opencode/glm-4.7-free` | Free | Docs, search |
| `opencode/kimi-k2.5` | Cheap | General fallback |
| `opencode/kimi-k2.5-free` | Free | Simple tasks |
| `google/antigravity-gemini-3-pro` | Free proxy | Deep reasoning |
| `google/antigravity-gemini-3-flash` | Free proxy | Quick analysis, multimodal |

### Model Selection Guide

| Task | Model | Why |
|------|-------|-----|
| Implementation (default) | `openai/gpt-5.3-codex` | Best coding, flat rate |
| Analysis / review | `openai/gpt-5.2` | Strong reasoning, flat rate |
| Docs / search | `opencode/glm-4.7-free` | Good enough, free |
| Fallback (any) | `opencode/glm-5-free` | Free, capable |
| Cheapest | `opencode/kimi-k2.5-free` | Lowest cost |

## Oh-My-OpenCode Agents

Agents pre-configure model, variant, and permissions. Use `--agent` instead of `-m`:

| Agent | Model | Best For |
|-------|-------|----------|
| `hephaestus` | `openai/gpt-5.3-codex` | Implementation, coding (flat rate) |
| `oracle` | `openai/gpt-5.2` | Analysis, reasoning (flat rate) |
| `momus` | `openai/gpt-5.2` | Code review, critique (flat rate) |
| `librarian` | `opencode/glm-4.7-free` | Lookup, search (free) |
| `atlas` | `opencode/kimi-k2.5-free` | General tasks (free) |
| `multimodal-looker` | `google/antigravity-gemini-3-flash` | Vision, multimodal (free) |

### Agents to AVOID (Anthropic-billed)

Do NOT use: `sisyphus`, `prometheus`, `metis`, `explore` — these are configured with Anthropic models.

## Instructions

- Use DEFAULT_MODEL if not specified. If 'free' or 'cheap' is requested, use FREE_MODEL or CHEAP_MODEL.
- Prefer oh-my-opencode agents over raw model IDs when the task maps to a known agent role.

## Mode: Non-Interactive (Default)

Use `opencode run` for autonomous execution.

### Command Template

```bash
opencode run "PROMPT" -m MODEL --format default
```

### With oh-my-opencode agent

```bash
opencode run "PROMPT" --agent AGENT_NAME --format default
```

### Examples

**Basic implementation:**
```bash
opencode run "implement pagination for the users API endpoint" -m openai/gpt-5.3-codex --format default
```

**With oh-my-opencode agent:**
```bash
opencode run "implement pagination for the users API endpoint" --agent hephaestus --format default
```

**Code review with momus agent:**
```bash
opencode run "review src/auth/ for security issues" --agent momus --format default
```

**Free-tier documentation:**
```bash
opencode run "document the REST API" --agent librarian --format default
```

**With working directory:**
```bash
opencode run "PROMPT" -m openai/gpt-5.3-codex --format default --dir /path/to/repo
```

## Mode: Interactive

Use `opencode` without `run` for interactive sessions:

### Command Template

```bash
opencode
```

Then select model/agent interactively within the TUI.

## Fallback Chain

The `opencode_task_executor.py` supports automatic fallback via `--fallback-models`:

```
Primary model (e.g., openai/gpt-5.3-codex) → retry up to --max-retries times
  ↓ still failing (rate limit / quota)
Fallback model (e.g., opencode/glm-5-free) → retry up to --max-retries times
  ↓ still failing
Report structured error in done.json
```

### Recommended fallback chains

| Use Case | Primary | Fallback | Flag |
|---|---|---|---|
| Implementation | `openai/gpt-5.3-codex` | `opencode/glm-5-free` | `--fallback-models opencode/glm-5-free` |
| Analysis | `openai/gpt-5.2` | `opencode/kimi-k2.5` | `--fallback-models opencode/kimi-k2.5` |
| Free-only | `opencode/glm-5-free` | `opencode/kimi-k2.5-free` | `--fallback-models opencode/kimi-k2.5-free` |

## Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "opencode not found" | `npm install -g opencode-ai` |
| Rate limited | Executor retries with fallback models automatically |
| Anthropic model blocked | Use Toad (Claude Code) for Claude tasks |
| Auth failed | Run `opencode` interactively to authenticate |
| Task timeout | Increase timeout, simplify prompt, or split into subtasks |

## Deprecated Patterns

Do NOT use these:
- `opencode/claude-*` models — API-billed, always blocked
- Running `opencode run` directly in a Bash tool call — always fork via `fork_terminal.py`
