# Repo Optimize Engine — Reference Overview

Supplementary reference for the `repo-optimize-engine` skill. Read SKILL.md for full instructions.

## What This Engine Does vs. Related Skills

| Skill | Purpose |
|-------|---------|
| `repo-optimize-engine` | Orchestration logic: mode detection, fork management, task graph, team spawn |
| `repo-equip-engine` | Templates and gap detection: component templates, applicability matrix, complexity scoring |
| `repo-audit-engine` | Alignment auditing: scores existing repos against docs-to-code rubric |

repo-optimize-engine imports logic from repo-equip-engine (do not duplicate). repo-audit-engine scores; repo-optimize-engine improves.

## Mode Detection Decision Tree

```
Target repo has .claude/ directory?
├── No  → greenfield
│         Full analysis + equip from scratch
│         Both OpenCode (needs) + Codex (quality) forks
│
└── Yes → Check MANIFEST.json for repo name
    ├── Found   → upgrade
    │             Diff against latest templates, patch stale components
    │             Codex quality fork focuses on freshness scoring
    │
    └── Not found → audit
                    Quality audit + best practices integration
                    Both forks run; emphasis on what's missing
```

**Validation before mode detection:**
1. Path must exist and be accessible
2. Target must not be the claude-code-templates repo itself (decline → suggest `/sync-reference`)
3. Target should have a `.git/` directory (warn if absent, do not block)

## Freshness Scoring Quick Reference

100-point scale applied to each existing `.claude/` component:

| Criterion | Points |
|-----------|--------|
| Current frontmatter schema | +10 |
| `related` fields present | +5 |
| Tools properly restricted | +10 |
| `$ARGUMENTS` usage correct | +5 |
| Prompt specificity (not vague) | +15 |
| Matches latest template | +15 |
| Has completion criteria | +10 |
| Error handling present | +10 |
| References context skill | +10 |
| Documentation quality | +10 |

Grade mapping: A (90-100), B (80-89), C (70-79), D (60-69), F (<60).

## Fork Configuration

| Fork | Model | Purpose |
|------|-------|---------|
| A | openai/gpt-5.2 via oracle agent | Needs analysis — 1M context reads the whole repo to identify gaps |
| B | gpt-5.2-codex | Quality audit — freshness scoring of existing .claude/ components |

Both forks run in parallel (different providers). Polling: every 15 seconds, 5-minute timeout.

Output: `docs/optimization/{REPO_NAME}-needs.md` and `docs/optimization/{REPO_NAME}-audit.md`.

## Fallback Chain

```
OpenCode fails (429/capacity/timeout) → Sonnet subagent via Task tool
Codex fails (API error/timeout)     → Sonnet subagent via Task tool
```

Note which fallback was used in the final report.

## Cross-Reference Priority Rules for Task Generation

| OpenCode (needs) | Codex (quality) | Task Priority |
|----------------|-----------------|---------------|
| "Repo needs X" | "X is stale/missing" | High — both agree |
| "Repo needs Y" | (no mention) | Medium — new addition |
| (no mention) | "Z has quality issues" | Medium — quality fix |
| (no mention) | (no mention) | Not a task — skip |

## Task Graph Dependency Rules

| Task | Teammate | Blocked By |
|------|----------|------------|
| T1: Create/update context skill | config-upgrader | Nothing |
| T2: Fix/add hooks | config-upgrader | Nothing |
| T3: Update MANIFEST + REGISTRY | config-upgrader | Nothing |
| T4: Create commands | command-builder | T1 |
| T5: Create/update workflows | command-builder | T1 |
| T6: Generate PRPs | command-builder | Nothing |
| T7: Update CLAUDE.md | docs-finalizer | T4, T5 |
| T8: Generate skill-priorities | docs-finalizer | T4, T5 |
| T9: Run validation suite | docs-finalizer | T7, T8 |

**Dynamic pruning:** Skip tasks with no findings. Minimum viable graph: T3 + T7 + T9.

## Three-Teammate Team Structure

| Teammate | Model | File Ownership |
|----------|-------|----------------|
| config-upgrader | Sonnet | `.claude/skills/{name}-context/`, `.claude/hooks/`, `MANIFEST.json`, `REGISTRY.md` |
| command-builder | Sonnet | `.claude/commands/{name}/`, `.claude/workflows/`, `PRPs/` |
| docs-finalizer | Sonnet | `{REPO_PATH}/CLAUDE.md`, `.claude/memory/skill-priorities.md` |

Lead (Opus) enters delegate mode after spawning. Lead does no implementation — only coordinates.

## Impact vs. Effort Classification

Each generated task is classified before queuing:

| Impact | Criteria |
|--------|----------|
| High | Daily workflow improvement — new commands, better CLAUDE.md, critical hooks |
| Medium | Occasional benefit — agent updates, workflow refinements |
| Low | Completeness — MANIFEST entries, REGISTRY rows, documentation polish |

**Effort** (from repo-equip-engine Complexity Scoring):
- Simple (score 1-3): build inline during team execution
- Complex (score 4+): generate a PRP document for later development
