---
name: repo-optimize-engine
description: Scoring rubrics, freshness criteria, mode detection, task graph generation, and team templates for multi-model repo optimization
version: 1.0.0
category: orchestration
user-invocable: false
related:
  commands: [workflow/repo-optimize]
  skills: [repo-equip-engine, multi-model-orchestration, agent-teams, fork-terminal]
---

# Repo Optimize Engine

Shared logic referenced by `/repo-optimize`. Do NOT invoke directly.

Reference the `repo-equip-engine` skill for Component Applicability Matrix, Gap Detection Heuristics, Complexity Scoring, and all Templates (context skill, command, CLAUDE.md section, skill priorities, MANIFEST entries).

## Mode Detection

Determine optimization mode based on target repo state:

```
Has .claude/ directory?
├── No  → MODE = greenfield  (full analysis + equipment from scratch)
├── Yes → Check MANIFEST.json in templates repo for repo name
│   ├── Found   → MODE = upgrade  (diff against latest templates, patch stale components)
│   └── Not found → MODE = audit  (quality audit, suggest improvements, integrate best practices)
```

### Validation Checks (before mode detection)

1. **Path exists**: Target directory must be accessible
2. **Not this repo**: If path resolves to claude-code-templates, decline — suggest `/sync-reference` instead
3. **Is a git repo**: Check for `.git/` directory (warn if absent, don't block)

### Working Variables

| Variable | Source |
|----------|--------|
| `REPO_PATH` | Absolute path to target repo |
| `REPO_NAME` | Directory basename (e.g., `cbass`, `mac-manage`) |
| `FOCUS_HINT` | Second argument from user (optional, may be empty) |
| `TEMPLATES_REPO` | Path to this claude-code-templates repo |
| `MODE` | `greenfield`, `upgrade`, or `audit` |

## Freshness Scoring Rubric

Score each existing `.claude/` component on a 100-point scale. Used by the Codex quality audit fork.

| Criterion | Points | What It Checks |
|-----------|--------|----------------|
| Current frontmatter schema | +10 | Uses latest YAML fields (name, description, related, etc.) |
| `related` fields present | +5 | Cross-references other components |
| Tools properly restricted | +10 | Not over-permissioned, uses allowed-tools |
| `$ARGUMENTS` usage correct | +5 | Commands accept and parse input properly |
| Prompt specificity | +15 | Specific instructions vs generic/vague |
| Matches latest template | +15 | Structural alignment with current repo-equip-engine templates |
| Has completion criteria | +10 | Defines what "done" looks like |
| Error handling present | +10 | Handles edge cases, validates input |
| References context skill | +10 | Uses shared knowledge base when applicable |
| Documentation quality | +10 | Clear, concise, actionable instructions |
| **Total** | **/100** | |

### Grade Mapping

| Grade | Score Range | Meaning |
|-------|------------|---------|
| A | 90-100 | Excellent — matches latest patterns, production-ready |
| B | 80-89 | Good — minor gaps, solid overall |
| C | 70-79 | Adequate — functional but notable gaps |
| D | 60-69 | Poor — significant issues, needs rework |
| F | < 60 | Critical — fundamentally outdated or missing key elements |

## Impact Scoring

Rate each proposed upgrade task by how much it improves the developer's Claude Code experience:

| Impact | Criteria | Examples |
|--------|----------|---------|
| **High** | Daily workflow improvement | New commands, better CLAUDE.md, critical hooks |
| **Medium** | Occasional benefit | Agent updates, workflow refinements, hook additions |
| **Low** | Completeness | MANIFEST entries, REGISTRY rows, documentation polish |

### Effort Scoring

Reference the `repo-equip-engine` Complexity Scoring:

- **Simple** (score 1-3): Build inline during Phase 3 team execution
- **Complex** (score 4+): Generate a PRP document for later development

### Category Assignment

Each task is assigned to exactly one teammate:

| Category | Teammate | What It Covers |
|----------|----------|----------------|
| `config` | `config-upgrader` | Context skills, hooks, MANIFEST.json, REGISTRY.md |
| `command` | `command-builder` | Commands, workflows, PRPs |
| `docs` | `docs-finalizer` | CLAUDE.md, skill-priorities.md, validation |

## Task Graph Generation Rules

### Dependency Conventions

| Task | Teammate | Blocked By | Rationale |
|------|----------|------------|-----------|
| T1: Create/update context skill | config-upgrader | Nothing | Foundation — everything may reference it |
| T2: Fix/add hooks | config-upgrader | Nothing | Independent of other components |
| T3: Update MANIFEST + REGISTRY | config-upgrader | Nothing | Can register components before they exist |
| T4: Create commands | command-builder | T1 | Commands reference the context skill |
| T5: Create/update workflows | command-builder | T1 | Workflows may chain commands |
| T6: Generate PRPs | command-builder | Nothing | PRPs are standalone documents |
| T7: Update CLAUDE.md | docs-finalizer | T4, T5 | Needs final command/workflow list to document |
| T8: Generate skill-priorities | docs-finalizer | T4, T5 | Needs final component list for tier assignment |
| T9: Run validation suite | docs-finalizer | T7, T8 | Validates everything is consistent |

### Task Graph Shape

```
config-upgrader (starts immediately):
  T1 ──────┐
  T2       │ unblocks T4, T5
  T3       │
           │
command-builder:
  T6 (no block — starts immediately)
  T4 ◄─────┘
  T5 ◄─────┘──────┐
                   │ unblocks T7, T8
docs-finalizer:    │
  T7 ◄────────────┘
  T8 ◄────────────┘
  T9 (blocked by T7, T8)
```

### Dynamic Task Generation

The task graph above is the **template**. During Phase 2 synthesis, Opus generates the actual tasks based on analysis findings:

- If no context skill needed → skip T1, remove T4/T5 blockers
- If no hooks needed → skip T2
- If no commands needed → skip T4, adjust T7/T8 blockers
- If no complex gaps → skip T6
- Minimum viable graph: T3 (MANIFEST) + T7 (CLAUDE.md) + T9 (validation)

## Team Configuration

### Teammate Roles

| Teammate | Model | Display Mode |
|----------|-------|-------------|
| `config-upgrader` | Sonnet | in-process (WSL2 default) |
| `command-builder` | Sonnet | in-process |
| `docs-finalizer` | Sonnet | in-process |

### File Ownership Boundaries

Enforced via spawn prompts to prevent conflicts:

**config-upgrader:**
```
WRITE: .claude/skills/{REPO_NAME}-context/*, .claude/hooks/*, MANIFEST.json, .claude/REGISTRY.md
READ:  docs/optimization/*.md, .claude/skills/repo-optimize-engine/*, .claude/skills/repo-equip-engine/*
```

**command-builder:**
```
WRITE: .claude/commands/{REPO_NAME}/*.md, .claude/workflows/*.md, PRPs/*.md
READ:  docs/optimization/*.md, .claude/skills/{REPO_NAME}-context/*, .claude/skills/repo-equip-engine/*
```

**docs-finalizer:**
```
WRITE: {REPO_PATH}/CLAUDE.md, {REPO_PATH}/.claude/memory/skill-priorities.md
READ:  Everything (needs to see what the other teammates built)
```

### Opus Lead Behavior

- Enter delegate mode (Shift+Tab) after spawning teammates
- Do no implementation work — only coordinate
- Monitor task list for completions and blockage resolution
- Handle teammate questions or conflicts
- Synthesize final summary after T9 (validation) completes

## Multi-Model Orchestration

### Fork Configuration

| Fork | Model | CLI Tool | Purpose |
|------|-------|----------|---------|
| A | gemini-3-pro-preview | gemini | Needs analysis (1M context) |
| B | gpt-5.2-codex | codex | Quality audit (SWE-bench leader) |

### Polling

- Interval: 15 seconds
- Timeout: 5 minutes (20 iterations)
- Check: both `docs/optimization/{REPO_NAME}-needs.md` and `docs/optimization/{REPO_NAME}-audit.md` exist

### Fallback Chain

```
Gemini fails (429/capacity/timeout) → Sonnet subagent via Task tool
Codex fails (API error/timeout)     → Sonnet subagent via Task tool
```

Note which fallback was used in the final report so the user knows which models contributed.

## Cross-Reference Priority Rules

Used during Phase 2 synthesis to prioritize upgrade tasks:

| Gemini Says | Codex Says | Priority |
|-------------|-----------|----------|
| "Repo needs X" | "X is stale/missing/weak" | **High** — both perspectives agree |
| "Repo needs Y" | (no mention) | **Medium** — new addition |
| (no mention) | "Z has quality issues" | **Medium** — quality fix |
| (no mention) | (no mention) | Not a task — skip |

## Relationship to repo-equip-engine

**Imported from repo-equip-engine** (do not duplicate):
- Component Applicability Matrix (universal, tech-conditional, domain-specific)
- Gap Detection Heuristics (CLI wrapper, context skill, workflow command signals)
- Complexity Scoring (simple 1-3 vs complex 4+)
- All Templates (context skill, command, skill priorities, MANIFEST entries, CLAUDE.md section)
- Re-Run Detection logic

**Added by repo-optimize-engine** (new):
- Multi-model orchestration logic (fork management, polling, fallbacks)
- Freshness scoring rubric (100-point scale)
- Impact scoring rules
- Task graph generation with dependency wiring
- Team spawn templates per role (config-upgrader, command-builder, docs-finalizer)
- Before/after scoring for reruns
- Cross-reference priority rules
