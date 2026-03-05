# Repo Optimize Engine — Example Walkthrough

## Scenario

A developer's `mac-manage` project has had a `.claude/` directory for 6 months. It was initially set up with an early version of the templates, but the templates repo has evolved significantly since. The hooks are outdated, the context skill is missing `related` fields, and there's no `skill-priorities.md`. The developer runs `/repo-optimize` to bring it up to the current standard.

## Trigger

> User: `/repo-optimize "/home/user/projects/mac-manage"`

## Step-by-Step

### Step 1: Mode Detection

The engine checks the target repo:
- `.claude/` directory exists → yes
- `mac-manage` found in templates `MANIFEST.json` → yes

**Mode: upgrade** — diff against latest templates, patch stale components.

Validation passes: path exists, is not claude-code-templates itself, has a `.git/` directory.

### Step 2: Multi-Model Fork Launch

Two forks launch concurrently:

**Fork A — Gemini Pro (Needs Analysis):**
Reads the entire `mac-manage` codebase (1M context) alongside the current templates. Produces `docs/optimization/mac-manage-needs.md`:

> "mac-manage has no workflow commands — only slash commands. Users frequently run multi-step sequences (discover → diff → restore) that would benefit from a workflow chain. The context skill is missing and the 4 existing commands don't cross-reference each other."

**Fork B — Codex (Quality Audit):**
Audits each `.claude/` component against the freshness rubric. Produces `docs/optimization/mac-manage-audit.md`:

Key scores:
| Component | Score | Grade | Issues |
|-----------|-------|-------|--------|
| hooks.json | 52/100 | F | Pre-commit hook uses old `python3` command, not `uv run`; missing PostToolUse hook |
| mac-discover.md | 74/100 | C | Missing `related` fields; no completion criteria |
| mac-diff.md | 71/100 | C | Missing `related` fields; vague completion criteria |
| mac-restore.md | 68/100 | D | Missing error handling section; no `related` fields |
| mac-status.md | 75/100 | C | Minor: prompt is overly generic |
| mac-manage-context/SKILL.md | 61/100 | D | Missing `version` field; no `related` references |

### Step 3: Opus Synthesizes — Phase 2 Planning

Opus applies cross-reference priority rules:

| Gemini Says | Codex Says | Priority |
|-------------|-----------|----------|
| "Needs workflow commands" | "Commands lack cross-references" | HIGH — both confirm workflow gap |
| "Context skill needs improvement" | "Context skill: Grade D" | HIGH — both confirm |
| (no mention) | "hooks.json: Grade F" | MEDIUM — quality fix |
| (no mention) | "mac-restore missing error handling" | MEDIUM — quality fix |

### Step 4: Task Graph Generated

Opus generates the dynamic task graph:

```
T1: Update mac-manage-context skill (blocked by nothing)
  → Add version field, related references, update to latest template
  Owner: config-upgrader

T2: Fix hooks.json (blocked by nothing)
  → Migrate pre-commit hook to uv run, add PostToolUse hook for LSP
  Owner: config-upgrader

T3: Update MANIFEST + REGISTRY (blocked by nothing)
  Owner: config-upgrader

T4: Add related fields to 4 commands (blocked by T1)
  → mac-discover, mac-diff, mac-restore, mac-status
  Owner: command-builder

T5: Create discover→diff→restore workflow chain (blocked by T1)
  Owner: command-builder

T6: Update CLAUDE.md (blocked by T4, T5)
  → Document new workflow, update component table
  Owner: docs-finalizer

T7: Generate skill-priorities.md (blocked by T4, T5)
  Owner: docs-finalizer

T8: Run validation suite (blocked by T6, T7)
  Owner: docs-finalizer
```

T6 from the template (PRPs) is skipped — no complex gaps requiring standalone PRP documents.

### Step 5: Spawn Team

Opus spawns three teammates with file ownership enforced in spawn prompts:

- **config-upgrader** (Sonnet): owns context skill, hooks.json, MANIFEST.json, REGISTRY.md
- **command-builder** (Sonnet): owns .claude/commands/mac-manage/*.md, .claude/workflows/*.md
- **docs-finalizer** (Sonnet): owns CLAUDE.md, .claude/memory/skill-priorities.md (read-only on all else)

Opus enters delegate mode (Shift+Tab).

### Step 6: Parallel Execution

**config-upgrader** completes T1, T2, T3 concurrently:
- Context skill: added `version: 1.0.0`, `related` fields, updated prompt specificity → score now 91/100 (A)
- hooks.json: migrated to `uv run`, added PostToolUse LSP hook → score now 88/100 (B)
- MANIFEST + REGISTRY updated with new workflow

T4 and T5 unblock for **command-builder**:
- Adds `related` fields to all 4 commands
- Creates `mac-discovery-workflow.md` chaining discover→diff→restore with decision points

**docs-finalizer** starts T6 and T7 after command-builder finishes:
- Updates CLAUDE.md component table, adds workflow section
- Generates `skill-priorities.md` with tier assignments

T8: validation suite runs — all checks pass.

### Step 7: Final Report

Opus synthesizes the before/after summary:

```
REPO OPTIMIZE COMPLETE: mac-manage
Mode: upgrade

BEFORE vs AFTER:
  hooks.json:          52 (F) → 88 (B)
  mac-manage-context:  61 (D) → 91 (A)
  mac-discover:        74 (C) → 87 (B)
  mac-diff:            71 (C) → 85 (B)
  mac-restore:         68 (D) → 84 (B)
  mac-status:          75 (C) → 86 (B)

NEW COMPONENTS:
  + .claude/workflows/mac-discovery-workflow.md
  + .claude/memory/skill-priorities.md

VALIDATION: All checks passed

Estimated improvement: from fragmented commands to a cohesive workflow with
current hooks, cross-referenced components, and a context skill at grade A.
```

## Output

**What the user gets:**
- A fully upgraded `.claude/` directory aligned with current template standards
- Before/after freshness scores for every component
- A new workflow chain (discover→diff→restore) they didn't have to design manually
- All changes made in parallel by three teammates — total wall-clock time ~8 minutes
- A validation suite confirms consistency before the session ends

**Files created/modified:**
- `.claude/skills/mac-manage-context/SKILL.md` — updated to Grade A
- `.claude/hooks/hooks.json` — migrated to uv run, added PostToolUse
- `.claude/commands/mac-manage/*.md` — all 4 updated with related fields
- `.claude/workflows/mac-discovery-workflow.md` — new workflow chain
- `.claude/memory/skill-priorities.md` — new tier assignments
- `CLAUDE.md` — updated component table and workflow documentation
- `MANIFEST.json` + `.claude/REGISTRY.md` — updated registrations
