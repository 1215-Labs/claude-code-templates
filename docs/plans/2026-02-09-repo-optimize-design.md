# Design: `/repo-optimize` — Multi-Model Repo Optimization with Agent Teams

**Date**: 2026-02-09
**Status**: Approved design, ready for implementation
**Author**: Mike + Claude Opus

## Overview

`/repo-optimize` is a three-phase workflow that uses multi-model analysis (Gemini Pro + Codex), Opus synthesis with user approval, and a 3-agent team for parallel execution. It analyzes a target repo's Claude Code setup, identifies gaps and stale components, and executes an upgrade plan with dependency-aware parallel processing.

**Relationship to `/repo-equip`**: Lives alongside it. `/repo-equip` remains the quick single-agent setup for initial equipment. `/repo-optimize` is the deep multi-model + team upgrade path for thorough analysis and optimization.

## Flowchart

### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           /repo-optimize "<path>"                           │
└─────────────────┬───────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────┐
│  PHASE 0: Validate & Detect │
│  ┌────────────────────────┐ │
│  │ Has .claude/ ?          │ │
│  │ ├─ No → GREENFIELD     │ │
│  │ ├─ Yes + in MANIFEST   │ │
│  │ │   → UPGRADE          │ │
│  │ └─ Yes + not in        │ │
│  │     MANIFEST → AUDIT   │ │
│  └────────────────────────┘ │
└─────────────┬───────────────┘
              │
              ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 1: Multi-Model Analysis (~2-3 min)                │
│                                                          │
│  ┌─────────────────────┐   ┌──────────────────────────┐  │
│  │   GEMINI PRO         │   │   CODEX                   │  │
│  │   (fork-terminal)    │   │   (fork-terminal)         │  │
│  │                      │   │                           │  │
│  │  "What does this     │   │  "How good is what's     │  │
│  │   repo NEED?"        │   │   already HERE?"          │  │
│  │                      │   │                           │  │
│  │  • Architecture      │   │  • Component inventory   │  │
│  │  • Tech stack        │   │  • Freshness scores      │  │
│  │  • Workflows         │   │  • Coverage gaps         │  │
│  │  • Domain concepts   │   │  • Quality issues        │  │
│  │  • Pain points       │   │  • Hook effectiveness    │  │
│  │  • CLI surface       │   │  • CLAUDE.md quality     │  │
│  │         │            │   │         │                │  │
│  │         ▼            │   │         ▼                │  │
│  │  {repo}-needs.md     │   │  {repo}-audit.md         │  │
│  └─────────────────────┘   └──────────────────────────┘  │
│            │                          │                   │
│            └────────────┬─────────────┘                   │
│                         ▼                                 │
│                 Opus polls for                             │
│                 both output files                          │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 2: Opus Synthesis (~1 min)                        │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Cross-Reference                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │  │
│  │  │ Gemini   │  │  Codex   │  │    Overlap =     │  │  │
│  │  │ says     │∩ │  says    │ =│  HIGH PRIORITY   │  │  │
│  │  │ "need X" │  │ "X weak" │  │  upgrades        │  │  │
│  │  └──────────┘  └──────────┘  └──────────────────┘  │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Score & Categorize Each Task                       │  │
│  │  • Impact: high / medium / low                      │  │
│  │  • Effort: simple (1-3) / complex (4+)              │  │
│  │  • Owner: config / command / docs                   │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Build Task Graph with Dependencies                 │  │
│  │                                                     │  │
│  │  config-upgrader    command-builder   docs-finalizer │  │
│  │  [T1] context skill [T4] commands    [T7] CLAUDE.md │  │
│  │  [T2] hooks         [T5] workflows   [T8] priorities│  │
│  │  [T3] MANIFEST      [T6] PRPs        [T9] validate │  │
│  │       │                  │                  │        │  │
│  │       │   blockedBy T1   │    blockedBy     │        │  │
│  │       └──────────────────┘    T4, T5        │        │  │
│  │                               └─────────────┘        │  │
│  └────────────────────────────────────────────────────┘  │
│                         │                                 │
│                         ▼                                 │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Present Plan to User                               │  │
│  │  ┌──────────┐ ┌──────────────┐ ┌────────────────┐  │  │
│  │  │ Proceed  │ │ Modify plan  │ │ Skip PRPs      │  │  │
│  │  └────┬─────┘ └──────┬───────┘ └───────┬────────┘  │  │
│  │       │              │                  │           │  │
│  │       │         User edits         Prune complex   │  │
│  │       │         tasks/priorities   gap tasks        │  │
│  │       │              │                  │           │  │
│  │       └──────────────┴──────────────────┘           │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────┘
                      │ User approves
                      ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: Agent Team Execution (~3-5 min)                │
│                                                          │
│  Opus spawns team, seeds tasks, enters delegate mode     │
│                                                          │
│  TIME ──────────────────────────────────────────────►    │
│                                                          │
│  config-upgrader (Sonnet)                                │
│  ║══════════════════════║                                │
│  ║ T1: context skill    ║─── T1 done ──┐                │
│  ║ T2: hooks            ║              │                │
│  ║ T3: MANIFEST+REG     ║              │  unblocks      │
│  ║══════════════════════║              │  T4, T5        │
│                                        │                 │
│  command-builder (Sonnet)              │                 │
│  ║════════════╦═════════════════════╗  │                │
│  ║ T6: PRPs   ║ T4: commands ◄──────╬──┘                │
│  ║ (no block) ║ T5: workflows       ║── T4,T5 done ─┐  │
│  ║════════════╩═════════════════════╝               │  │
│                                                      │  │
│  docs-finalizer (Sonnet)                   unblocks  │  │
│               ║══════════════════════════╗  T7, T8   │  │
│    waiting... ║ T7: CLAUDE.md ◄──────────╬───────────┘  │
│               ║ T8: skill-priorities     ║              │
│               ║ T9: validate             ║              │
│               ║══════════════════════════╝              │
│                         │                                │
│                    T9 complete                            │
└─────────────────────┬────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 4: Summary & Teardown                             │
│                                                          │
│  • Opus reads validation results                         │
│  • Presents before/after freshness scores                │
│  • Lists all created/updated/unchanged components        │
│  • Lists deferred PRPs with next-step commands           │
│  • Shuts down teammates                                  │
│  • Suggests: /all_skills, test commands, rerun schedule  │
└──────────────────────────────────────────────────────────┘
```

### Mode Detection (Phase 0 Detail)

```
                    /repo-optimize "<path>"
                            │
                            ▼
                    ┌───────────────┐
                    │ Path exists?  │──── No ──► Error: path not found
                    └───────┬───────┘
                            │ Yes
                            ▼
                    ┌───────────────┐
                    │ Is this repo  │──── Yes ─► Error: use /sync-reference
                    │ (templates)?  │
                    └───────┬───────┘
                            │ No
                            ▼
                    ┌───────────────┐
                    │ Has .claude/? │──── No ──► MODE = GREENFIELD
                    └───────┬───────┘           (full equipment)
                            │ Yes
                            ▼
                    ┌───────────────────┐
                    │ Repo name found   │
                    │ in MANIFEST.json? │──── Yes ─► MODE = UPGRADE
                    └───────┬───────────┘           (diff & patch)
                            │ No
                            ▼
                      MODE = AUDIT
                      (quality audit +
                       integrate best
                       practices)
```

## 1. Command Entry Point

**Invocation**: `/repo-optimize "<path>" ["focus hint"]`

**Handles three scenarios:**

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Greenfield** | No `.claude/` directory | Full analysis + equipment from scratch |
| **Upgrade** | `.claude/` exists + repo name in MANIFEST.json | Diff against latest templates, upgrade stale components |
| **Audit** | `.claude/` exists + not in MANIFEST | Quality audit, suggest improvements, integrate best practices |

**Key files:**

| File | Purpose |
|------|---------|
| `.claude/commands/workflow/repo-optimize.md` | Command definition |
| `.claude/skills/repo-optimize-engine/SKILL.md` | Scoring rubrics, mode detection, task graph rules |
| `.claude/skills/repo-optimize-engine/prompts/gemini-needs-analysis.md` | Gemini Pro fork prompt |
| `.claude/skills/repo-optimize-engine/prompts/codex-quality-audit.md` | Codex fork prompt |
| `.claude/skills/repo-optimize-engine/templates/optimization-plan.md` | Phase 2 plan format |
| `.claude/skills/repo-optimize-engine/templates/teammate-spawn.md` | Spawn prompt per role |

## 2. Phase 0 — Validation & Mode Detection

### Parse Arguments

Extract from `$ARGUMENTS`:
- **First argument**: Target repo path (required) — strip quotes
- **Second argument**: Focus hint (optional) — narrows analysis scope

### Validate Target

1. **Path exists**: Verify directory is accessible
2. **Not this repo**: If path resolves to claude-code-templates, decline and suggest `/sync-reference`
3. **Is a git repo**: Check for `.git/` (warn if not, don't block)

### Detect Mode

Check for `.claude/` directory in target repo:
- **No `.claude/`** → `MODE = GREENFIELD`
- **Has `.claude/`** → Check `MANIFEST.json` in templates repo for entries matching repo name
  - **Found** → `MODE = UPGRADE`
  - **Not found** → `MODE = AUDIT`

### Set Working Variables

- `REPO_PATH`: Absolute path to target repo
- `REPO_NAME`: Directory basename (e.g., `cbass`, `mac-manage`)
- `FOCUS_HINT`: Optional focus string or empty
- `TEMPLATES_REPO`: Path to claude-code-templates repo
- `MODE`: `greenfield`, `upgrade`, or `audit`

## 3. Phase 1 — Multi-Model Analysis

Two forked terminals run simultaneously via `fork-terminal` skill. Opus stays lean, just orchestrating.

### Fork A: Gemini Pro — "What does this repo need?"

Gemini gets full repo context (1M window) and answers:

| Analysis Area | What Gemini Discovers |
|---------------|----------------------|
| Architecture | Entry points, module boundaries, data flow |
| Tech stack | Languages, frameworks, build tools, test frameworks, CI/CD |
| Workflows | What developers actually do (build, test, deploy, debug, release) |
| Domain concepts | Terminology, business logic patterns, specialized vocabulary |
| Pain points | TODOs, FIXMEs, missing tests, no docs, complex undocumented areas |
| CLI surface | CLI tools with subcommands, argument patterns, output formats |

If `FOCUS_HINT` is provided, weight exploration toward that area.

**Output**: `docs/optimization/{repo-name}-needs.md` (progressive disclosure format)

**Fork command**:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
  "gemini -p '{FILLED_PROMPT}' --model gemini-3-pro-preview --approval-mode yolo"
```

### Fork B: Codex — "How good is what's here?"

Codex audits the existing `.claude/` directory (or absence thereof) against latest templates:

| Audit Area | What Codex Evaluates |
|------------|---------------------|
| Component inventory | Every agent, command, skill, hook, workflow found |
| Freshness scores | Each component's patterns vs. current templates |
| Coverage gaps | What the tech stack demands vs. what's configured |
| Quality issues | Vague prompts, missing tool restrictions, no related fields, broken refs |
| Hook effectiveness | Whether hooks catch what they should |
| CLAUDE.md quality | Score against `claude-md-improver` rubric (A-F grade) |

For greenfield repos, Codex audits against "what *should* exist" rather than "what *does* exist."

**Output**: `docs/optimization/{repo-name}-audit.md`

**Fork command**:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex \
  "codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex '{FILLED_PROMPT}'"
```

### Polling

Both forks complete in ~2-3 minutes. Opus polls for output files every 15 seconds, timeout after 5 minutes:

```bash
for i in $(seq 1 20); do
  FOUND=0
  [ -f "docs/optimization/{repo-name}-needs.md" ] && FOUND=$((FOUND+1))
  [ -f "docs/optimization/{repo-name}-audit.md" ] && FOUND=$((FOUND+1))
  [ "$FOUND" -ge 2 ] && break
  sleep 15
done
```

### Fallback Chain

If a fork fails (output missing after timeout):

```
Gemini fails (429/capacity) → Fall back to Sonnet subagent (Task tool)
Codex fails                 → Fall back to Sonnet subagent (Task tool)
```

Note which fallback was used in the final report.

## 4. Phase 2 — Opus Synthesis & Task Graph

Opus reads both analysis files and produces a unified upgrade plan with dependency-aware task decomposition.

### Step 1: Cross-Reference Findings

| Gemini Says | Codex Says | Priority |
|-------------|-----------|----------|
| "Repo needs X" | "X is stale/missing/weak" | **High** — both agree |
| "Repo needs Y" | (no mention) | **Medium** — new addition |
| (no mention) | "Z has quality issues" | **Medium** — quality fix |

### Step 2: Score and Prioritize

Each upgrade task gets three scores:

**Impact** (how much it improves the Claude experience):
- **High**: Daily workflow improvement (new commands, better CLAUDE.md)
- **Medium**: Occasional benefit (hooks, updated agents)
- **Low**: Completeness (MANIFEST entries, REGISTRY updates)

**Effort** (using `repo-equip-engine` complexity scoring):
- **Simple** (score 1-3): Build inline during Phase 3
- **Complex** (score 4+): Generate a PRP for later development

**Category** (determines teammate ownership):
- `config`: Context skills, hooks, MANIFEST, REGISTRY
- `command`: Commands, workflows, PRPs
- `docs`: CLAUDE.md, skill-priorities, validation

### Step 3: Build Task Graph

Assign every task to a teammate and wire up `blockedBy` dependencies:

```
config-upgrader tasks:          command-builder tasks:         docs-finalizer tasks:
─────────────────────          ──────────────────────         ────────────────────
[T1] Create/update context     [T4] Create new commands       [T7] Update CLAUDE.md
     skill                          (refs context skill)            (needs T4, T5 done)
[T2] Fix/add hooks                  blockedBy: [T1]          [T8] Generate skill-priorities
[T3] Update MANIFEST +         [T5] Create/update workflows        blockedBy: [T4, T5]
     REGISTRY                       blockedBy: [T1]           [T9] Run validation suite
                               [T6] Generate PRPs for              blockedBy: [T7, T8]
                                    complex gaps
```

Key dependency rules:
- `config-upgrader` has **no blockers** — starts immediately
- `command-builder` T4/T5 are **blocked by T1** (context skill must exist before commands can reference it)
- `command-builder` T6 (PRPs) has **no blockers** (PRPs are standalone documents)
- `docs-finalizer` T7/T8 are **blocked by T4, T5** (needs final command list to document)
- `docs-finalizer` T9 is **blocked by T7, T8** (validates everything)

### Step 4: Present Plan to User

```markdown
# Optimization Plan for {repo-name}

## Mode: {greenfield | upgrade | audit}

## Analysis Summary
- Gemini found: {N} needs across {categories}
- Codex found: {N} issues, avg freshness score: {X}/100

## Upgrade Tasks ({N} total)

### config-upgrader ({N} tasks, no blockers)
| # | Task | Impact | Effort |
|---|------|--------|--------|
| T1 | Create cbass-context skill | High | Simple |
| T2 | Add PostToolUse format hook | Medium | Simple |
| T3 | Update MANIFEST + REGISTRY | Low | Simple |

### command-builder ({N} tasks, blocked by T1)
| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
| T4 | Create /cbass-health command | High | Simple | T1 |
| T5 | Create deploy workflow | Medium | Simple | T1 |
| T6 | PRP: monitoring dashboard | High | Complex | — |

### docs-finalizer ({N} tasks, blocked by T4, T5)
| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
| T7 | Update CLAUDE.md | High | Simple | T4, T5 |
| T8 | Generate skill-priorities | Medium | Simple | T4, T5 |
| T9 | Run validation suite | High | Simple | T7, T8 |

### Deferred (PRPs)
| PRP | Why Complex | Effort Est |
|-----|-------------|------------|
| cbass-monitoring.md | Multiple dashboards, domain knowledge | 4+ |
```

### Step 5: User Approval

Present via `AskUserQuestion` with options:
- **Proceed with full plan** — execute everything
- **Modify plan** — let user adjust before proceeding
- **Proceed without PRPs** — only direct work, skip complex gaps

**Never execute without user confirmation.**

## 5. Phase 3 — Agent Team Execution

### Team Structure

| Teammate | Model | Owns | Blocked By |
|----------|-------|------|------------|
| `config-upgrader` | Sonnet | Context skills, hooks, MANIFEST, REGISTRY | Nothing |
| `command-builder` | Sonnet | Commands, workflows, PRPs | T1 (context skill) |
| `docs-finalizer` | Sonnet | CLAUDE.md, skill-priorities, validation | T4, T5 |

### File Ownership Boundaries

Enforced via spawn prompts to prevent conflicts:

**config-upgrader:**
```
WRITE: .claude/skills/{repo}-context/*, .claude/hooks/*, MANIFEST.json, .claude/REGISTRY.md
READ:  docs/optimization/*.md, .claude/skills/repo-optimize-engine/*
```

**command-builder:**
```
WRITE: .claude/commands/{repo}/*.md, .claude/workflows/*.md, PRPs/*.md
READ:  docs/optimization/*.md, .claude/skills/{repo}-context/*
```

**docs-finalizer:**
```
WRITE: {REPO_PATH}/CLAUDE.md, {REPO_PATH}/.claude/memory/skill-priorities.md
READ:  Everything (needs to see what others built)
```

### Blocking Mechanics

1. Opus seeds all tasks via `TaskCreate` with `blockedBy` wiring
2. `config-upgrader` and `command-builder` start immediately on unblocked tasks
3. `config-upgrader` finishes T1 (context skill) → marks complete → T4/T5 unblock for `command-builder`
4. When both finish → T7/T8 unblock for `docs-finalizer`
5. `docs-finalizer` reads everything, writes CLAUDE.md and skill-priorities, runs validation

### Spawn Prompt Contents

Each teammate receives:
1. Role and objective
2. The synthesized plan (relevant tasks only)
3. Gemini + Codex analysis doc paths to read
4. Template references from `repo-optimize-engine`
5. File ownership rules (what they can/cannot touch)
6. Completion criteria (what "done" means for each task)

### Opus Lead Behavior

- Enters **delegate mode** (Shift+Tab) — does no implementation work
- Monitors task list for completions and blockage resolution
- Handles teammate questions or conflicts
- After `docs-finalizer` marks validation complete → synthesizes final summary

## 6. Engine Skill

### Directory Structure

```
.claude/skills/repo-optimize-engine/
├── SKILL.md                          # Scoring rubrics, freshness criteria,
│                                     #   mode detection, task graph templates
├── prompts/
│   ├── gemini-needs-analysis.md      # Gemini Pro fork prompt template
│   └── codex-quality-audit.md        # Codex fork prompt template
└── templates/
    ├── optimization-plan.md          # Phase 2 plan presentation format
    └── teammate-spawn.md             # Spawn prompt template per role
```

### SKILL.md Contents

**Mode detection logic** — the greenfield vs upgrade vs audit flowchart.

**Freshness scoring rubric** (how Codex scores existing components):

| Criterion | Points | What It Checks |
|-----------|--------|----------------|
| Current frontmatter schema | +10 | Uses latest YAML fields |
| `related` fields present | +5 | Cross-references other components |
| Tools properly restricted | +10 | Not over-permissioned |
| `$ARGUMENTS` usage correct | +5 | Commands accept input properly |
| Prompt specificity | +15 | Specific vs generic instructions |
| Matches latest template | +15 | Structural alignment with current templates |
| Has completion criteria | +10 | Defines what "done" looks like |
| Error handling present | +10 | Handles edge cases |
| References context skill | +10 | Uses shared knowledge base |
| Documentation quality | +10 | Clear, concise, actionable |
| **Total** | **/100** | **Mapped to A-F grades** |

**Impact scoring rules:**
- **High**: Daily workflow improvement (new commands, better CLAUDE.md, critical hooks)
- **Medium**: Occasional benefit (agent updates, workflow refinements)
- **Low**: Completeness (MANIFEST entries, REGISTRY rows)

**Task graph generation rules:**
- Context skill is always T1 (everything else may depend on it)
- Hooks and MANIFEST/REGISTRY have no cross-dependencies
- Commands and workflows depend on context skill
- PRPs have no dependencies (standalone documents)
- CLAUDE.md depends on final command list
- Skill-priorities depends on final component list
- Validation depends on all documentation being complete

### Relationship to `repo-equip-engine`

`repo-optimize-engine` **imports** from `repo-equip-engine`:
- Component Applicability Matrix
- Gap Detection Heuristics
- Complexity Scoring
- All Templates (context skill, command, CLAUDE.md section, skill priorities, MANIFEST entries)

`repo-optimize-engine` **adds**:
- Multi-model orchestration logic (fork management, polling, fallbacks)
- Freshness scoring rubric (new)
- Task graph generation with dependency wiring (new)
- Team spawn templates per role (new)
- Before/after scoring for reruns (new)

`repo-equip-engine` stays the single source of truth for "what components fit what signals."

### Prompt Templates

Templates use `{VARIABLES}` filled by the command at runtime.

**`gemini-needs-analysis.md`:**
- Variables: `{REPO_PATH}`, `{REPO_NAME}`, `{FOCUS_HINT}`, `{MODE}`
- Output format: progressive disclosure (executive summary → deep findings)
- Sections to analyze: architecture, tech stack, workflows, domain, pain points, CLI

**`codex-quality-audit.md`:**
- Variables: `{REPO_PATH}`, `{REPO_NAME}`, `{TEMPLATES_REPO}`, `{MODE}`, `{EXISTING_COMPONENTS}`
- For upgrade mode: includes current component list to diff against
- Output format: component-by-component scorecard + gap list

## 7. Output & Artifacts

### Files Created During Run

```
docs/optimization/                    # Analysis artifacts (in templates repo)
├── {repo-name}-needs.md              # Gemini Pro analysis
├── {repo-name}-audit.md              # Codex quality audit
└── {repo-name}-plan.md               # Synthesized plan (saved after approval)

In the templates repo:                # New/updated components
├── MANIFEST.json                     # Updated entries
├── .claude/REGISTRY.md               # Updated catalog
├── .claude/skills/{repo}-context/    # New or refreshed context skill
├── .claude/commands/{repo}/*.md      # New or refreshed commands
└── PRPs/{repo}-*.md                  # Complex gaps deferred to PRPs

In the target repo:                   # Target repo improvements
├── CLAUDE.md                         # Updated with Claude Code Commands section
└── .claude/memory/skill-priorities.md # Tier-based activation priorities

Globally installed (via symlinks):    # Ready to use immediately
├── ~/.claude/skills/{repo}-context/
└── ~/.claude/commands/{repo}/*.md
```

### Final Summary Format

```markdown
# Optimization Complete: {repo-name}

## Mode: {greenfield | upgrade | audit}
## Models Used: Gemini Pro (analysis) + Codex (audit) + 3x Sonnet (execution)

## What Changed
- {N} components created, {N} updated, {N} unchanged
- Freshness score: {before}/100 → {after}/100
- Coverage: {before}% → {after}% of detected needs addressed

## Components
| Component | Action | Status |
|-----------|--------|--------|
| cbass-context skill | Created | Installed globally |
| /cbass-status command | Updated | Installed globally |
| PostToolUse hook | Added | Active |
| CLAUDE.md | Rewritten | In target repo |

## Deferred (PRPs)
| PRP | Purpose | Next Step |
|-----|---------|-----------|
| PRPs/cbass-monitoring.md | Complex dashboard system | /prp-claude-code-execute |

## Next Steps
1. Run `/all_skills` in {repo-name} to verify
2. Test new commands: `/{repo}-status`, `/{repo}-logs`
3. Execute PRPs if generated: `/prp-claude-code-execute "PRPs/{repo}-*.md"`
4. Run `/repo-optimize` again in 2-4 weeks to catch drift
```

### Rerun Behavior

Running `/repo-optimize` again on the same repo:
- Gemini re-analyzes (repo may have evolved)
- Codex re-audits (scores components we previously created)
- Plan shows "unchanged" items skipped, only genuine upgrades proposed
- Freshness scores show improvement over time (before → after delta)
- `docs/optimization/{repo-name}-audit.md` overwrites previous, providing a fresh baseline

## 8. Implementation Plan

### Files to Create

| # | File | Effort |
|---|------|--------|
| 1 | `.claude/skills/repo-optimize-engine/SKILL.md` | Medium — scoring rubrics, mode detection, task graph rules |
| 2 | `.claude/skills/repo-optimize-engine/prompts/gemini-needs-analysis.md` | Medium — structured analysis prompt |
| 3 | `.claude/skills/repo-optimize-engine/prompts/codex-quality-audit.md` | Medium — structured audit prompt |
| 4 | `.claude/skills/repo-optimize-engine/templates/optimization-plan.md` | Simple — plan presentation format |
| 5 | `.claude/skills/repo-optimize-engine/templates/teammate-spawn.md` | Medium — spawn prompts for 3 roles |
| 6 | `.claude/commands/workflow/repo-optimize.md` | Large — full command orchestrating all phases |

### Files to Update

| File | Change |
|------|--------|
| `MANIFEST.json` | Add repo-optimize-engine skill + repo-optimize command |
| `.claude/REGISTRY.md` | Add entries to catalog |

### Dependencies

- `fork-terminal` skill (existing) — for forking Gemini/Codex
- `repo-equip-engine` skill (existing) — imported for matching heuristics and templates
- `agent-teams` skill (existing) — referenced patterns for team coordination
- Agent teams feature enabled (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`)

### Suggested Build Order

1. Engine skill (`SKILL.md`) — establishes all the rules
2. Prompt templates — what the forks actually do
3. Spawn + plan templates — team coordination formats
4. Command file — ties everything together
5. MANIFEST + REGISTRY updates
6. Test on a real repo
