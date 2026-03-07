# Repo Optimize Engine — Worked Example

## Scenario

The user runs: `/repo-optimize "/home/user/projects/cbass"`

The target is a Python CLI tool. It has a `.claude/` directory but is not in MANIFEST.json — so it was equipped previously using an older version of the templates but is not tracked.

## Step 1: Validation and Mode Detection

```bash
ls /home/user/projects/cbass
# → src/ tests/ pyproject.toml .claude/ .git/ README.md

ls /home/user/projects/cbass/.claude/
# → CLAUDE.md commands/ skills/ hooks.json

# Check MANIFEST.json for 'cbass'
grep -r "cbass" /home/mdc159/projects/claude-code-templates/MANIFEST.json
# → no match
```

Mode: **audit** (has `.claude/` but not in MANIFEST — existing install, not tracked).

Working variables:
- `REPO_PATH` = `/home/user/projects/cbass`
- `REPO_NAME` = `cbass`
- `FOCUS_HINT` = (none provided)
- `MODE` = `audit`

## Step 2: Create Output Directory

```bash
mkdir -p /home/user/projects/cbass/docs/optimization
```

## Step 3: Launch Forks A and B Concurrently

**Fork A — OpenCode (Needs Analysis):**

Task: Read the entire cbass repo with 1M context. Identify gaps in `.claude/` components vs. current best practices. What commands, agents, or workflows are missing that would benefit this Python CLI project? Output: `docs/optimization/cbass-needs.md`.

**Fork B — Codex (Quality Audit):**

Task: Score each existing `.claude/` component against the freshness rubric (100-point scale). Flag stale frontmatter, missing related fields, vague prompts, missing completion criteria. Output: `docs/optimization/cbass-audit.md`.

Both launch simultaneously.

## Step 4: Poll for Completion

Check every 15 seconds:
```
[~3 min] docs/optimization/cbass-needs.md appears
[~3.5 min] docs/optimization/cbass-audit.md appears
```

## Step 5: Synthesize Findings (Phase 2)

**OpenCode (needs) findings:**
- No context skill for cbass domain knowledge
- No `/test` command (runs `pytest` but no command shortcut)
- Missing hooks for type checking (mypy not configured)
- No workflow for the bug investigation pattern
- CLAUDE.md is 180 lines and getting dense

**Codex (quality) findings:**
- `cbass-debug` command: score 55/100 (F) — prompt is vague, no completion criteria, outdated frontmatter schema
- `hooks.json` PostToolUse hook: score 70/100 (C) — works but no error handling
- `.claude/CLAUDE.md`: score 60/100 (D) — missing related-commands section, no quick-start table

Cross-reference: Both OpenCode and Codex flag the missing context skill and weak CLAUDE.md. Priority: High.

## Step 6: Generate Task Graph

Dynamic task graph based on findings:

| Task | Teammate | Blocked By | Priority | Effort |
|------|----------|------------|----------|--------|
| T1: Create cbass-context skill | config-upgrader | Nothing | High | Simple |
| T2: Fix PostToolUse hook error handling | config-upgrader | Nothing | Medium | Simple |
| T3: Update MANIFEST + REGISTRY | config-upgrader | Nothing | Low | Simple |
| T4: Create /test command | command-builder | T1 | High | Simple |
| T4b: Rewrite /cbass-debug command | command-builder | T1 | High | Simple |
| T5: Create bug-investigation workflow | command-builder | T1 | Medium | Simple |
| T7: Rewrite CLAUDE.md | docs-finalizer | T4, T4b, T5 | High | Simple |
| T8: Generate skill-priorities | docs-finalizer | T4, T4b, T5 | Medium | Simple |
| T9: Run validation suite | docs-finalizer | T7, T8 | — | Simple |

T6 (PRPs) skipped — no complex tasks identified.

## Step 7: Spawn the Three-Teammate Team

**Spawn config-upgrader (Sonnet):**
```
You are the config-upgrader for cbass repo optimization.

WRITE: /home/user/projects/cbass/.claude/skills/cbass-context/*, 
       /home/user/projects/cbass/.claude/hooks.json, 
       /home/user/projects/cbass/MANIFEST.json,
       /home/user/projects/cbass/.claude/REGISTRY.md
READ:  docs/optimization/*.md, .claude/skills/repo-equip-engine/*

Tasks:
T1: Create cbass-context skill using the context skill template from repo-equip-engine
T2: Add try/catch error handling to hooks.json PostToolUse hook
T3: Add cbass entry to MANIFEST.json and REGISTRY.md
```

**Spawn command-builder (Sonnet):**
```
You are the command-builder for cbass repo optimization.
BLOCKED on T4, T4b, T5 until config-upgrader completes T1.

WRITE: /home/user/projects/cbass/.claude/commands/cbass/*.md,
       /home/user/projects/cbass/.claude/workflows/*.md
READ:  docs/optimization/*.md, .claude/skills/cbass-context/*

Tasks:
T4: Create /test command that runs pytest with output formatting
T4b: Rewrite /cbass-debug command with specific prompts and completion criteria
T5: Create bug-investigation workflow following .claude/workflows/bug-investigation.md pattern
```

**Spawn docs-finalizer (Sonnet):**
```
You are the docs-finalizer for cbass repo optimization.
BLOCKED on T7, T8 until command-builder completes T4, T4b, T5.

WRITE: /home/user/projects/cbass/CLAUDE.md,
       /home/user/projects/cbass/.claude/memory/skill-priorities.md
READ:  Everything — you need the full picture of what teammates built

Tasks:
T7: Rewrite CLAUDE.md with quick-start table, related-commands section, keep under 200 lines
T8: Generate skill-priorities.md listing all components by tier
T9: Run validation suite (python3 scripts/validate-manifest.py)
```

Enable delegate mode (Shift+Tab) immediately after spawning.

## Step 8: Monitor and Coordinate

```
[~5 min] config-upgrader: T1, T2, T3 complete
[~5 min] command-builder: unblocked, starts T4, T4b, T5
[~9 min] command-builder: all tasks complete
[~9 min] docs-finalizer: unblocked, starts T7, T8
[~12 min] docs-finalizer: T7, T8 complete
[~13 min] docs-finalizer: T9 (validation) — 0 errors
```

## Step 9: Synthesize Final Summary

```
Optimization complete: cbass (audit mode)

Freshness before: 55-70/100 (D-C range)
Estimated freshness after: 80-90/100 (B-A range)

Changes made:
- Created cbass-context skill (domain knowledge base)
- Rewrote /cbass-debug command (55 → 88/100)
- Added /test command
- Created bug-investigation workflow
- Improved hooks.json error handling
- Rewrote CLAUDE.md (dense 180 lines → clean 140 lines with quick-start table)
- Added cbass to MANIFEST.json and REGISTRY.md
- Generated skill-priorities.md

Validation: 0 errors
```

## Timeline

| Phase | Duration |
|-------|----------|
| Validation + mode detection | ~30 sec |
| Forks A + B concurrent | ~3-4 min |
| Synthesis + task graph | ~1 min |
| Spawn team + execute | ~8 min |
| Validation + summary | ~1 min |
| **Total** | **~14-15 min** |
