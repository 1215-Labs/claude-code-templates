# Multi-Model Orchestration — Reference Overview

## Key Concepts

- **Opus stays clean**: Opus acts as the strategic orchestrator and never does exploration or implementation itself — it delegates to specialized models via forked terminals, preserving its context for user interaction and synthesis.
- **Context-based routing**: The primary decision driver is task type and context size. Exploration goes to OpenCode (multi-provider model access), implementation goes to Codex (SWE-bench leader), coordination stays in Opus.
- **Progressive disclosure outputs**: Forked agents write structured documents to `docs/exploration/` or `docs/implementation/`. Opus reads the executive summary first, then drills into details only as needed.
- **Flat-rate and free models**: OpenAI models via ChatGPT Pro are flat rate. GLM and Kimi models are free. No per-request quota concerns for exploration tasks.

## Decision Criteria

### When to Fork vs. Handle Directly

| Condition | Action |
|-----------|--------|
| Task requires 2-3 tool calls | Handle directly — forking overhead not worth it |
| Exploring unfamiliar/large codebase | Fork OpenCode (multi-provider model access) |
| Implementing a feature after exploration | Fork Codex (SWE-bench leader) |
| Context window is filling up | Consider forking to preserve Opus context |
| Task spans multiple independent subsystems | Fork multiple OpenCode instances in parallel |
| User needs tight back-and-forth during work | Handle directly — forking breaks the loop |
| Task requires full session context to understand | Handle directly |

### Model Selection Matrix

| I need to... | Fork to | Model | Output |
|--------------|---------|-------|--------|
| Explore large codebase | OpenCode | openai/gpt-5.2 via oracle agent | docs/exploration/ |
| Understand architecture | OpenCode | openai/gpt-5.2 via oracle agent | docs/exploration/ |
| Find patterns and conventions | OpenCode | openai/gpt-5.2 via oracle agent | docs/exploration/ |
| Implement a feature | Codex | gpt-5.2-codex | docs/implementation/ |
| Refactor code | Codex | gpt-5.2-codex | docs/implementation/ |
| Fix bugs | Codex | gpt-5.2-codex | docs/implementation/ |
| Fix CI failures | Codex | gpt-5.2-codex | (uses /gh-fix-ci skill) |
| Generate docs | Codex | gpt-5.1-codex-mini | (uses /doc skill) |
| Coordinate and decide | Stay in Opus | — | — |

### Context Size Thresholds

- **< 50k tokens**: Handle directly in Opus; forking overhead dominates.
- **50k–200k tokens**: Single OpenCode fork usually sufficient.
- **200k+ tokens**: OpenCode excels; potentially parallel forks for different subsystems.
- **Context getting full in Opus session**: Fork to preserve Opus for synthesis.

## Quick Reference

### Orchestration Patterns

| Pattern | When | Flow |
|---------|------|------|
| Explore-Then-Implement | Most common | OpenCode → Opus synthesis → Codex |
| Parallel Exploration | Feature spans multiple subsystems | Multiple OpenCode forks → Opus synthesis |
| Iterative Refinement | Implementation needs review loop | Codex → Opus review → Codex refine |

### Oh-My-OpenCode Agent Routing

| Agent | Model | Rate | Best For |
|-------|-------|------|----------|
| oracle | openai/gpt-5.2 | Flat rate | Analysis, reasoning |
| momus | openai/gpt-5.2 | Flat rate | Code review |
| hephaestus | openai/gpt-5.3-codex | Flat rate | Implementation |
| librarian | opencode/glm-4.7-free | Free | Docs, search |
| atlas | opencode/kimi-k2.5-free | Free | General tasks |

### Error Recovery Chain

1. Primary model fails with 429 → retry up to `--max-retries` times
2. Exhausted retries → fall back to next model in `--fallback-models` chain
3. `QUOTA_EXHAUSTED`: wait 60s, retry with a different agent or model
4. `MODEL_CAPACITY`: switch to a free-tier agent (librarian or atlas)
5. Never retry more than 3 times total from the orchestrator level

### Anti-Patterns to Avoid

- Don't fork for tasks completable in 2-3 tool calls
- Don't start a new fork without referencing previous fork outputs
- Don't forget to specify output locations in fork prompts
- Don't over-orchestrate — not every task needs explore-then-implement
