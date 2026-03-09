# Skill Evaluator — Example Walkthrough

## Scenario

A developer discovers the `last30days-skill` reference submodule in their repo and wants to understand whether it's worth adopting. The skill generates a "last 30 days of activity" summary from git history. Before spending time integrating it, they want a structured assessment of its code quality, how well it fits their current component ecosystem, and what adoption risks exist.

## Trigger

> User: "evaluate this new skill at references/last30days-skill — we're thinking about adopting it for our /catchup command"

## Step-by-Step

### Step 1: Parse Input

Opus extracts:
- `TARGET_PATHS`: `references/last30days-skill`
- `SKILL_NAMES`: `last30days-skill`
- `INTENDED_USE`: integration with the /catchup command
- `EVALUATION_DEPTH`: full (default — this is a real adoption decision)

The path resolves to a reference submodule — use directly, no git clone needed.

### Step 2: Gather Context

**Pre-fork inventory (run on target):**

```bash
find references/last30days-skill -type f | head -200
# → SKILL.md, tools/git_summary.py, tools/format_output.py, README.md, tests/test_git_summary.py

git -C references/last30days-skill log --oneline -20
# → 8 commits, most recent 3 months ago

ls references/last30days-skill/README* references/last30days-skill/SKILL.md
# → Both present
```

Inventory saved to `/tmp/skill-eval-last30days-inventory.txt`.

**Ecosystem snapshot (current components):**

```bash
ls -la ~/.claude/skills/
# → 14 skills including fork-terminal, multi-model-orchestration, agent-teams...

cat MANIFEST.json | python3 -c "..."
# → agents: 13, commands: 17, skills: 14, hooks: 5
```

Snapshot saved to `/tmp/skill-eval-ecosystem-snapshot.txt`.

### Step 3: Create Output Directory

```bash
mkdir -p docs/evaluations
```

### Step 4: Fork Three Agents

All three agents launch in parallel:

**Agent 1 — Structural Quality (Codex):**
Codex reads `references/last30days-skill/` and the inventory. It evaluates:
- Code architecture: git_summary.py uses `subprocess` to call `git log` with configurable date range. Clean separation.
- Testing: `tests/test_git_summary.py` has 6 tests — covers happy path and empty-repo edge case. Missing tests for non-git directories.
- Dependencies: Standard library only (`subprocess`, `datetime`). No external deps.
- Error handling: Partial. git errors caught, but output parsing failures will raise uncaught exceptions.

Output: `docs/evaluations/last30days-structural.md`

**Agent 2 — Ecosystem Fit (OpenCode oracle):**
OpenCode oracle reads both the target skill and the full ecosystem snapshot via multi-provider model access. It assesses:
- Overlap with existing components: `/catchup` command already calls `git log` directly. This skill abstracts that logic — reduces duplication.
- Interface compatibility: SKILL.md uses standard frontmatter schema. Consistent with existing skills.
- Integration path: Could be called from `/catchup` as a Python subprocess or inlined. The tool output format (markdown) is compatible.
- Maintenance signals: 8 commits, 3-month-old latest commit. Active enough for its simplicity.

Output: `docs/evaluations/last30days-ecosystem.md`

**Agent 3 — Risk & Adoption (OpenCode momus):**
OpenCode momus analyzes:
- Dependency count: 0 external deps. No supply chain risk.
- Git history health: 8 commits, 1 contributor. Single-author risk if skill needs changes.
- Scope creep risk: Low — tool does one thing.
- Breaking change surface: Only risk is git CLI output format changes across versions.

Output: `docs/evaluations/last30days-risk.md`

### Step 5: Synthesis

Opus reads all three reports (executive summaries first). It resolves one apparent contradiction:
- Structural says "good testing" (6 tests)
- Risk says "single contributor, maintenance risk"

Resolution: Tests are present and reasonable for the scope. Maintenance risk is real but low-impact — if git output format changes, the fix is trivial. Not a blocker for adoption.

Final weighting given `INTENDED_USE` (integration with /catchup): ecosystem fit is the most important dimension here.

### Step 6: Final Report Written

`docs/evaluations/last30days-eval.md` written with:

```
VERDICT: Adopt

SCORE: 78/100
  Structural Quality:  72  (partial error handling, minor test gaps)
  Ecosystem Fit:       88  (reduces duplication in /catchup, compatible interface)
  Risk:                74  (single contributor, but low-impact maintenance surface)

EXECUTIVE SUMMARY:
The last30days-skill is a clean, dependency-free utility that solves a real gap
in the /catchup command — it abstracts git log parsing that currently lives
inline. Structural quality is adequate but not excellent (add error handling for
output parsing failures before adopting). Ecosystem fit is strong. Adoption risk
is low given zero external dependencies.

TOP RECOMMENDATION:
Adopt with one pre-integration fix: wrap the output parser in try/except in
git_summary.py:47. Estimated effort: 15 minutes.
```

### Step 7: Presented to User

```
VERDICT: Adopt

last30days-skill fits cleanly into /catchup — reduces duplicated git log logic.

Score: 78/100
  Structural: 72 | Ecosystem: 88 | Risk: 74

One fix before adopting:
  Add error handling to git_summary.py:47 output parser (15 min)

Full report: docs/evaluations/last30days-eval.md
```

## Output

**What the user gets:**
- A clear adopt/skip verdict with reasoning in under 5 minutes
- A weighted score across three independent dimensions
- One specific action item before integration, with effort estimate
- A permanent evaluation report in `docs/evaluations/` for team reference
- Confidence that the decision is based on structural, ecosystem, AND risk analysis — not just a quick read-through
