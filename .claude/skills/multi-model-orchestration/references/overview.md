# Multi-Model Orchestration — Reference Overview

Supplementary reference for the `multi-model-orchestration` skill. Read SKILL.md for full instructions.

## Decision Criteria: Fork vs. Handle Directly

Fork when ALL of the following are true:
1. The task cannot be completed in 2-3 tool calls
2. It involves either broad codebase exploration OR a concrete implementation task
3. Your context window is not already packed with essential state the forked agent needs

Handle directly when ANY of the following are true:
- Simple lookup, explanation, or single-file edit
- User needs immediate back-and-forth during execution
- Task requires your full session context to correctly interpret

## Model Selection Quick Reference

| Signal | Choose | Reason |
|--------|--------|--------|
| "How does X work?", unfamiliar codebase, large surface area | OpenCode | 1M context reads everything at once |
| Architecture analysis, complex patterns, design decisions | OpenCode | Deep reasoning + 1M context |
| "Implement X", "Fix bug Y", "Refactor Z" | Codex | SWE-bench leader for code changes |
| Coordinate, synthesize, talk to user | Stay Opus | Orchestration is your role |
| Docs, API docs generation | Codex (mini) | Lighter model, lower cost |

## Pattern Decision Tree

```
New request arrives
├── Needs codebase understanding first?
│   ├── Yes, large/unfamiliar area → Pattern 1: Explore-Then-Implement
│   │     Fork OpenCode → read summary → Fork Codex
│   └── Yes, multiple independent areas → Pattern 2: Parallel Exploration
│         Fork 2 OpenCode instances concurrently (stagger 30-60s) → synthesize
└── Ready to implement directly?
    ├── Yes, first attempt → Fork Codex
    └── Yes, iterative (needs review) → Pattern 3: Iterative Refinement
          Fork Codex → Opus reviews → Fork Codex again
```

## Key Constraints

**Concurrency limits (free OAuth):**
- Max 2 concurrent OpenCode forks
- Stagger parallel launches by 30-60 seconds
- Prefer `openai/gpt-5.2 via oracle agent` for parallel tasks (preview models have lower capacity)

**Context hygiene rules:**
- Always point forked agents to their output file (`docs/exploration/` or `docs/implementation/`)
- When reading results, read the Executive Summary first — only drill into Raw Findings if needed
- Always pass previous output file paths when chaining forks (Codex needs the OpenCode exploration doc)

## Error Recovery Decision Tree

```
Fork returns error_type in done.json
├── QUOTA_EXHAUSTED → wait 60s, retry with different auth mode or model
├── MODEL_CAPACITY  → switch to openai/gpt-5.2 via oracle agent (more available capacity)
└── Other error     → read output log tail; do NOT retry more than 3 times total
```

## Output File Conventions

| Fork | Output location | Format |
|------|-----------------|--------|
| OpenCode exploration | `docs/exploration/{topic}.md` | Progressive disclosure (Executive Summary first) |
| Codex implementation | `docs/implementation/{topic}-log.md` | Files Changed table + test results |

## Anti-Pattern Checklist

Before forking, confirm none of these apply:
- [ ] Task completable in under 3 tool calls (overhead not worth it)
- [ ] Task requires tight user interaction during execution
- [ ] About to start a 3rd+ recursive fork without synthesizing first (over-orchestration)
- [ ] Previous fork output not referenced in next fork prompt (losing context chain)
