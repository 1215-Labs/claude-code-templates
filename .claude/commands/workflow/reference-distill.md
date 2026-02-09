---
name: reference-distill
description: |
  Extract and integrate high-ROI patterns from evaluated reference submodules.
  Reads skill-evaluator reports, plans component extraction, adapts to our conventions,
  and tracks provenance for downstream propagation via /repo-equip and /repo-optimize.

  Usage: /reference-distill ["eval-name-or-path"]

  Examples:
  /reference-distill "claude-code-hooks-mastery"
  /reference-distill "docs/evaluations/claude-code-hooks-mastery-eval.md"
  /reference-distill                    # Batch: all pending evals with verdict != Skip

  Best for: Converting evaluation insights into integrated template library components
  Use after: /skill-evaluator (produces the evaluation reports this command consumes)
  See also: /repo-equip (propagates adopted patterns to target repos), /repo-optimize (deep optimization)
argument-hint: ["eval report path or name"]
user-invocable: true
related:
  commands: [workflow/sync-reference, workflow/repo-equip, workflow/repo-optimize]
  skills: [reference-distill, skill-evaluator, repo-equip-engine, fork-terminal, multi-model-orchestration]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Task
  - AskUserQuestion
---

# Reference Distillation

**Input**: $ARGUMENTS

Reference the `reference-distill` skill for evaluation report parsing rules, extraction plan schema, adaptation heuristics, conflict detection, provenance format, and multi-model orchestration patterns.

---

## Phase 0: Validate & Resolve Input

### Parse Arguments

Extract from `$ARGUMENTS`:
- **Path to eval report**: If argument contains `/` or ends in `.md`, treat as a direct path
- **Eval name**: If argument is a plain name (e.g., `claude-code-hooks-mastery`), resolve to `docs/evaluations/{name}-eval.md`
- **Empty**: Batch mode — scan all files in `docs/evaluations/` matching `*-eval.md`

### Locate Evaluation Reports

1. If a specific eval was requested, verify the file exists at the resolved path
2. If batch mode, find all `*-eval.md` files in `docs/evaluations/`
3. Read each eval report and extract the `**Verdict:**` line
4. Filter out reports with verdict `Skip`
5. Sort remaining by overall score descending

### Validate Prerequisites

For each evaluation report:

1. **Source repo exists**: Parse `**Target:**` line to get the reference submodule path. Verify the directory exists and is not empty. If empty, suggest: `git submodule update --init {path}`
2. **Report completeness**: Verify the eval has: Executive Summary, At a Glance table, Recommended Strategy section, and at least one Priority subsection
3. **No duplicate adoptions**: Read `.claude/memory/adoptions.md` and check if any ADO records already reference the same source repo + source files

### Load Context

Read these files for cross-referencing during planning:
- `MANIFEST.json` — existing component registry
- `REGISTRY.md` — human-readable catalog
- `.claude/memory/adoptions.md` — existing adoption records
- `.claude/memory/decisions.md` — for DEC numbering

### Set Working Variables

- `EVAL_REPORTS`: Array of eval report paths to process
- `EVAL_COUNT`: Number of evaluations (1 for single, N for batch)
- `TEMPLATES_REPO`: Path to this claude-code-templates repo
- `ADOPTIONS_FILE`: `.claude/memory/adoptions.md`
- `DECISIONS_FILE`: `.claude/memory/decisions.md`
- `TASKS_FILE`: `.claude/memory/tasks.md`

---

## Phase 1: Parse & Plan (Multi-Model)

### Parse Evaluation Reports

For each eval report, use the parser rules from the `reference-distill` skill (Section 1) to extract:

| Field | Parse Method |
|-------|-------------|
| `EVAL_NAME` | Filename: strip path and `-eval.md` suffix |
| `VERDICT` | `**Verdict:**` line |
| `OVERALL_SCORE` | `**Overall**` row in At a Glance table |
| `DIMENSION_SCORES` | All rows in At a Glance table |
| `NOVELTY_MAP` | "What's Genuinely New" table rows |
| `COMBINATORIAL_LEVERAGE` | "Combinatorial Leverage" table rows |
| `PRIORITY_ITEMS` | Priority subsections in Recommended Strategy |
| `SOURCE_REPO` | `**Target:**` line |
| `RISK_FLAGS` | "Key Risks" table rows |

### Generate Extraction Plan

**Try multi-model first** (reference `reference-distill` skill Section 7):

1. **Fork A — Extraction Planner (Gemini Pro)**:
   - Fill the prompt template at `.claude/skills/reference-distill/prompts/extraction-planner-agent.md`
   - Substitute: `{EVAL_REPORT}`, `{SOURCE_REPO_PATH}`, `{MANIFEST_JSON}`, `{REGISTRY_MD}`, `{EXISTING_ADOPTIONS}`, `{OUTPUT_FILE}`
   - Fork via `fork-terminal` skill with `--tool gemini`
   - Output: `/tmp/distill-{name}-plan.json`

2. **Fork B — Adaptation Specialist (Codex)**:
   - Fill the prompt template at `.claude/skills/reference-distill/prompts/adaptation-agent.md`
   - Substitute: `{EXTRACTION_PLAN}` (from Fork A output), `{SOURCE_FILES}`, `{OUR_CONVENTIONS}`, `{SIMILAR_COMPONENTS}`, `{OUTPUT_DIR}`
   - Fork via `fork-terminal` skill with `--tool codex`
   - Output: `/tmp/distill-{name}-adapted/`

3. **Polling**: Check every 15 seconds, 5-minute timeout per agent

4. **Fallback chain**:
   - Gemini Pro fails → retry with Gemini Flash → Sonnet subagent via Task tool
   - Codex fails → Sonnet subagent via Task tool

**If multi-model unavailable** (WSL2, no fork-terminal):
- Use Sonnet subagents via Task tool for both extraction planning and adaptation
- Pass the same prompt templates as task descriptions

### Batch Conflict Detection

If processing multiple evaluations, run conflict detection per `reference-distill` skill Section 4:
- **Destination collisions**: Two extractions targeting same path → higher score wins
- **Competing approaches**: Different solutions to same gap → present to user
- **Dependency cycles**: Flag for manual ordering
- **Naming collisions**: Prefix with source repo abbreviation

### Build Final Extraction Plan

Merge multi-model outputs into a unified extraction plan. For each extraction record:

| Field | Source |
|-------|--------|
| `id` | Sequential EXT-001, EXT-002, etc. |
| `source_file` | From extraction planner output |
| `destination_path` | From destination path rules in skill |
| `adaptation_needed` | From extraction planner analysis |
| `execution_mode` | `direct` if effort 1-3 pts, `prp` if 4+ pts |
| `priority` | From evaluation report |
| `batch_score` | Computed per ranking algorithm |

Sort by `batch_score` descending.

---

## Phase 2: Present Plan & Confirm

### Fill Plan Template

Use the template at `.claude/skills/reference-distill/templates/distill-plan.md`:
- Fill all variable sections with extraction plan data
- Include conflict details if any
- Show execution mode breakdown (direct vs PRP counts)
- List registry updates that will be made

### Present to User

Display the filled plan and ask:

```
AskUserQuestion:
  "How would you like to proceed?"
  Options:
  1. "Execute full plan" — Extract all components as planned
  2. "Priority 1 only" — Extract only Priority 1 items
  3. "Modify plan" — Let me adjust specific extractions
  4. "Save plan only" — Write plan to docs/ without executing
```

- **Execute full plan**: Continue to Phase 3 with all extractions
- **Priority 1 only**: Filter to priority=1 extractions only, continue to Phase 3
- **Modify plan**: Ask follow-up questions about what to change, rebuild plan, re-present
- **Save plan only**: Write plan to `docs/distill-plans/{eval_name}-plan.md`, skip to Phase 5 (report only)

**Never execute without explicit user confirmation.**

---

## Phase 3: Extract & Adapt

### Simple Adaptations (Direct Execution)

For each extraction with `execution_mode: direct`:

1. **Read source file** from the reference submodule
2. **Apply adaptation** per type (reference `reference-distill` skill Section 3):

   **`none`**: Add provenance header, copy to destination
   ```
   <!-- Adapted from: {source_repo}/{source_file} on YYYY-MM-DD -->
   ```

   **`frontmatter`**: Rewrite frontmatter using the mapping tables in the skill, preserve body content, add provenance header

3. **Write adapted file** to destination path
4. **Validate**: Check that frontmatter conforms to our schema (agents need name/description/model/tools, skills need name/description/version/category, commands need description)

### Complex Adaptations (PRP Generation)

For each extraction with `execution_mode: prp`:

1. **Read source file** from the reference submodule
2. **Read similar existing component** of the same type from our library (for convention reference)
3. **Generate PRP** at `PRPs/distill-{component-name}.md` containing:
   - Full source code with annotations
   - Target conventions with exemplars
   - Step-by-step adaptation requirements
   - Integration checklist (hooks.json, MANIFEST, REGISTRY)
   - Acceptance criteria
   - Test plan
4. **Note**: PRPs are NOT executed in this command. User executes them later via `/prp-claude-code-execute "PRPs/distill-{name}.md"`

### Track Results

Maintain a running list of:
- `direct_adopted[]`: Components extracted and written directly
- `prp_deferred[]`: Components with PRPs generated
- `skipped[]`: Components that couldn't be extracted (with reason)
- `errors[]`: Any errors encountered

---

## Phase 4: Register & Remember

### Update MANIFEST.json

For each **directly adopted** component (not PRPs):

Add entry to the appropriate `components` array:
```json
{
  "name": "{component_name}",
  "path": "{destination_path}",
  "deployment": "global",
  "status": "beta",
  "description": "{adapted description}"
}
```

### Update REGISTRY.md

- Add row to Quick Lookup table
- Add entry to appropriate category section
- Update component counts (skills, agents, commands, hooks as applicable)
- Add cross-references in Related Components

### Append Decision Record

Add to `.claude/memory/decisions.md`:

```markdown
### DEC-{NNN}: Adopt patterns from {eval_name}

- **Date**: {today}
- **Context**: skill-evaluator scored {eval_name} at {score}/5 with verdict "{verdict}". Extracted {N} components ({M} direct, {K} as PRPs).
- **Decision**: Extracted {component_list}. Direct: {direct_list}. PRPs: {prp_list}.
- **Alternatives**: (1) Adapt Patterns only — higher effort, custom implementations, (2) Adopt As-Is — lower effort but maintenance dependency, (3) Skip — miss high-ROI patterns.
```

### Append Adoption Records

For each extraction, append to `.claude/memory/adoptions.md` using the template at `.claude/skills/reference-distill/templates/adoption-record.md`:

- **Direct extractions**: Status = `adopted`
- **PRP extractions**: Status = `deferred-to-prp`, include PRP path

### Add Follow-Up Tasks

Append to `.claude/memory/tasks.md` under `## Active`:

```markdown
- [{today}] Execute PRP: PRPs/distill-{name}.md (from {eval_name} distillation)
- [{today}] Test extracted {component} in isolation
- [{today}] Run /repo-equip on target repos to propagate new patterns
```

---

## Phase 5: Verify & Report

### Run Validation

```bash
python3 scripts/validate-docs.py
```

If validation fails, identify the issue and fix it before continuing. Common issues:
- Missing MANIFEST entry (add it)
- Frontmatter validation failure (fix the frontmatter)
- Cross-reference mismatch (update REGISTRY)

### Run Installation

```bash
python3 scripts/install-global.py --dry-run
```

If dry-run succeeds:
```bash
python3 scripts/install-global.py
```

### Present Summary

```markdown
# Distillation Complete: {eval_name}

## Results
- **Direct adoptions**: {M} components written
- **PRPs generated**: {K} for later execution
- **Skipped**: {S} (with reasons)

## Components Adopted
| Component | Type | Source | Destination | Status |
|-----------|------|--------|-------------|--------|
{component_table}

## Provenance
- Decision: DEC-{NNN}
- Adoptions: ADO-{first} through ADO-{last}
- Tasks: {task_count} follow-up items added

## Validation
- validate-docs.py: {pass/fail}
- install-global.py: {pass/fail}

## Next Steps
1. Execute PRPs: {prp_commands}
2. Test extracted components in isolation
3. Run `/repo-equip` on target repos to propagate new patterns
4. Update reference submodule: `./scripts/update-references.sh`
```

---

## Error Handling

| Error | Recovery |
|-------|----------|
| Eval report not found | List available reports in `docs/evaluations/`, ask user to pick |
| Source submodule empty | Run `git submodule update --init {path}`, retry |
| Multi-model agents timeout | Fall back to Sonnet subagent via Task tool |
| MANIFEST validation fails | Show error, attempt auto-fix, re-validate |
| Frontmatter schema mismatch | Show expected vs actual, fix and re-validate |
| Destination file already exists | Ask user: overwrite, skip, or rename with `-v2` suffix |
| ADO numbering conflict | Re-parse adoptions.md for highest number |
