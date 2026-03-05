# Repo Optimize Engine — Reference Overview

## Key Concepts

- **Three optimization modes**: Mode is auto-detected from repo state — `greenfield` (no `.claude/` directory, build from scratch), `upgrade` (repo is registered in MANIFEST, diff and patch stale components), `audit` (has `.claude/` but not registered, quality check and best practices).
- **Two-phase execution**: Phase 1 uses multi-model forks (Gemini for needs analysis, Codex for quality audit) to produce analysis docs. Phase 2 spawns a three-teammate agent team (config-upgrader, command-builder, docs-finalizer) to execute the upgrade task graph.
- **Freshness scoring drives prioritization**: Each existing `.claude/` component scores 0-100 on a rubric. Cross-referencing Gemini's needs analysis with Codex's quality audit determines task priority (both agree = High, one mentions = Medium, neither = skip).
- **Task graph has fixed dependency wiring**: T1 (context skill) unblocks T4/T5 (commands/workflows); T4+T5 unblock T7/T8 (CLAUDE.md, skill-priorities); T7+T8 unblock T9 (validation). The graph is dynamic — skip tasks for gaps that don't exist.

## Decision Criteria

### Mode Detection

| Repo State | Mode | Action |
|------------|------|--------|
| No `.claude/` directory | greenfield | Full analysis + equipment from scratch via repo-equip-engine |
| Has `.claude/` AND found in MANIFEST.json | upgrade | Diff against latest templates, patch stale components |
| Has `.claude/` but NOT in MANIFEST.json | audit | Quality audit, suggest improvements, integrate best practices |
| Path resolves to claude-code-templates itself | Decline | Suggest /sync-reference instead |

### Cross-Reference Priority Rules

| Gemini Says | Codex Says | Task Priority |
|-------------|-----------|---------------|
| "Repo needs X" | "X is stale/missing/weak" | High — both agree |
| "Repo needs Y" | (no mention) | Medium — new addition |
| (no mention) | "Z has quality issues" | Medium — quality fix |
| (no mention) | (no mention) | Skip — not a task |

### Impact vs. Effort for Task Ordering

| Impact | Criteria | Examples |
|--------|----------|---------|
| High | Daily workflow improvement | New commands, better CLAUDE.md, critical hooks |
| Medium | Occasional benefit | Agent updates, workflow refinements |
| Low | Completeness | MANIFEST entries, REGISTRY rows, docs polish |

Simple tasks (complexity 1-3): build inline. Complex tasks (4+): generate a PRP for later development.

## Quick Reference

### Freshness Scoring Rubric (100 points per component)

| Criterion | Points |
|-----------|--------|
| Current frontmatter schema | +10 |
| `related` fields present | +5 |
| Tools properly restricted | +10 |
| `$ARGUMENTS` usage correct | +5 |
| Prompt specificity | +15 |
| Matches latest template | +15 |
| Has completion criteria | +10 |
| Error handling present | +10 |
| References context skill | +10 |
| Documentation quality | +10 |

### Grade Mapping

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Matches latest patterns, production-ready |
| B | 80-89 | Minor gaps, solid overall |
| C | 70-79 | Functional but notable gaps |
| D | 60-69 | Significant issues, needs rework |
| F | < 60 | Fundamentally outdated or missing key elements |

### Task Graph Dependency Wiring

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

### Teammate File Ownership

| Teammate | Writes | Reads |
|----------|--------|-------|
| config-upgrader | .claude/skills/{REPO_NAME}-context/*, .claude/hooks/*, MANIFEST.json, .claude/REGISTRY.md | docs/optimization/*.md |
| command-builder | .claude/commands/{REPO_NAME}/*.md, .claude/workflows/*.md, PRPs/*.md | docs/optimization/*.md, context skill |
| docs-finalizer | {REPO_PATH}/CLAUDE.md, .claude/memory/skill-priorities.md | Everything |

### Multi-Model Fork Configuration

| Fork | Model | Purpose | Fallback |
|------|-------|---------|---------|
| A | gemini-3-pro-preview | Needs analysis (1M context) | Sonnet subagent |
| B | gpt-5.2-codex | Quality audit (SWE-bench leader) | Sonnet subagent |

Polling: every 15s, timeout 5 min. Both forks launch concurrently.
