---
name: reference-distill
description: |
  Evaluation-to-integration engine — parses skill-evaluator reports, plans component extraction,
  adapts source conventions to our standards, integrates into the template library, and tracks
  provenance for downstream propagation via /repo-equip and /repo-optimize.
version: 1.0.0
category: orchestration
user-invocable: false
related:
  commands: [workflow/reference-distill]
  skills: [skill-evaluator, repo-equip-engine, repo-optimize-engine, fork-terminal, multi-model-orchestration]
---

# Reference Distill Engine

Bridge between evaluation (skill-evaluator) and integration (repo-equip/repo-optimize). Reads evaluation reports, extracts recommended components adapted to our conventions, and records provenance so downstream commands propagate adopted patterns to other repos.

## Pipeline Position

```
/sync-reference  -->  /skill-evaluator  -->  /reference-distill  -->  /repo-equip  -->  /repo-optimize
                                                     |
                                                     +--> .claude/memory/adoptions.md
```

## Multi-Model Architecture

```
                      +-- Gemini Pro: Extraction Planner --> extraction-plan.json
                      |     (reads eval + source repo + MANIFEST/REGISTRY)
User Request --> Opus |
                      +-- Codex: Adaptation Specialist --> adapted files
                      |     (reads source files + our convention exemplars)
                      |
                 Then: Opus validates, writes, registers, remembers
```

Fallback: Gemini/Codex unavailable -> Sonnet subagent via Task tool.

## Variables

EVAL_REPORTS_DIR: docs/evaluations
ADOPTIONS_FILE: .claude/memory/adoptions.md
DECISIONS_FILE: .claude/memory/decisions.md
TASKS_FILE: .claude/memory/tasks.md
PRP_OUTPUT_DIR: PRPs
EXTRACTION_MODEL: gemini-3-pro-preview
ADAPTATION_MODEL: gpt-5.2-codex

---

## Section 1: Evaluation Report Parser

Parse `docs/evaluations/{name}-eval.md` files to extract structured data. The parser is tolerant of format variations — it matches by section heading patterns, not exact formatting.

### Extracted Fields

| Field | Source Section | Parse Method |
|-------|--------------|--------------|
| `EVAL_NAME` | Filename `{name}-eval.md` | Strip path and suffix |
| `EVAL_DATE` | `**Date:**` line | Text after colon |
| `VERDICT` | `**Verdict:**` line | One of: Adopt, Extract Components, Adapt Patterns, Skip |
| `OVERALL_SCORE` | `## At a Glance` table, `**Overall**` row | Float from `**X.XX/5**` |
| `DIMENSION_SCORES` | `## At a Glance` table | Array of {dimension, score, agent} |
| `NOVELTY_MAP` | `## What's Genuinely New` table | Array of {capability, gap_level, impact} |
| `COMBINATORIAL_LEVERAGE` | `## Combinatorial Leverage` table | Array of {combination, capability, effort, value} |
| `RECOMMENDED_STRATEGY` | `## Recommended Strategy` section | Strategy name + rationale |
| `PRIORITY_ITEMS` | Priority subsections within strategy | Array of {priority, files[], description} |
| `SOURCE_REPO` | `**Target:**` line | Path to reference submodule |
| `RISK_FLAGS` | `## Risk Profile` -> `### Key Risks` table | Array of {risk, severity, mitigation} |
| `INTEGRATION_CHECKLIST` | `## Integration Checklist` | Array of checkbox items |

### Parser Heuristics

- **Heading-based**: Find sections by `## ` prefix, not by line number
- **Table-based**: Parse markdown tables by `|` delimiter, strip whitespace
- **Tolerant**: If a section is missing, set field to empty array/null (don't fail)
- **Priority detection**: Look for `**Priority 1**`, `**Week 1:**`, `### Priority 1`, or numbered list items in the Recommended Strategy section
- **File path extraction**: Regex for paths containing `/` or `.` with common extensions (`.py`, `.md`, `.ts`, `.json`, `.sh`)

---

## Section 2: Extraction Plan Generator

For each `PRIORITY_ITEM` from the evaluation, generate an extraction record.

### Extraction Record Schema

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | `EXT-{NNN}` sequential identifier |
| `source_file` | string | Path within the reference submodule |
| `source_repo` | string | Reference submodule path (e.g., `references/claude-code-hooks-mastery`) |
| `destination_path` | string | Target path in our template library |
| `destination_type` | enum | `skill` / `agent` / `command` / `hook` / `workflow` / `output-style` / `status-line` |
| `adaptation_needed` | enum | `none` / `frontmatter` / `convention-convert` / `full-rewrite` |
| `execution_mode` | enum | `direct` (simple) / `prp` (complex) |
| `dependencies` | string[] | IDs of other extractions this requires |
| `estimated_effort` | enum | `simple` (1-3 points) / `complex` (4+ points) |
| `priority` | int | 1-3 from evaluation report |
| `eval_score` | float | Overall score from the evaluation |
| `notes` | string | Adaptation-specific notes |

### Destination Path Rules

| Source Location | Destination Pattern |
|-----------------|-------------------|
| `.claude/hooks/*.py` | `.claude/hooks/{adapted-name}.py` |
| `.claude/agents/*.md` | `.claude/agents/{adapted-name}.md` |
| `.claude/agents/team/*.md` | `.claude/agents/{adapted-name}.md` |
| `.claude/commands/*.md` | `.claude/commands/workflow/{adapted-name}.md` |
| `.claude/skills/*` | `.claude/skills/{adapted-name}/SKILL.md` |
| `.claude/output-styles/*.md` | `.claude/output-styles/{name}.md` |
| `.claude/status_lines/*.py` | `.claude/status-lines/{name}.py` |
| Conceptual pattern | Generate PRP with full context |

### Effort Scoring (from repo-equip-engine)

| Factor | Points |
|--------|--------|
| New file creation | +1 |
| Frontmatter rewrite | +1 |
| Logic adaptation | +2 |
| New dependencies | +1 |
| hooks.json modification | +1 |
| Cross-component wiring | +2 |
| Full architecture conversion | +3 |

**Simple (1-3 points)**: Execute directly
**Complex (4+ points)**: Generate PRP for `/prp-claude-code-execute`

---

## Section 3: Adaptation Rules

### Adaptation Type: `none`

Source file is compatible as-is. Just:
1. Add provenance header: `<!-- Adapted from: {source_repo}/{source_file} on {date} -->`
2. Copy to destination

### Adaptation Type: `frontmatter`

Source file has different frontmatter schema. Rewrite frontmatter while preserving body content.

**Agent frontmatter mapping:**

| Source Field | Our Field | Transformation |
|-------------|-----------|---------------|
| `name` | `name` | Validate kebab-case |
| `description` | `description` | Ensure action-oriented (starts with verb or "Use when...") |
| `tools` | `tools` | Validate against available tools list |
| `model` | `model` | Map to: haiku / sonnet / opus |
| `color` | `color` | Keep if valid color name |
| (missing) | `category` | Infer from description (general / security / validation / orchestration) |
| (missing) | `related` | Auto-populate based on similar existing agents |

**Skill frontmatter mapping:**

| Source Field | Our Field | Transformation |
|-------------|-----------|---------------|
| `name` | `name` | Validate kebab-case |
| `description` | `description` | Multi-line, 1-3 sentences |
| (missing) | `version` | Set to `1.0.0` |
| (missing) | `category` | Infer: orchestration / patterns / tools / context |
| (missing) | `user-invocable` | Default `false` unless it's a standalone capability |
| (missing) | `related` | Auto-populate from MANIFEST relationships |

**Command frontmatter mapping:**

| Source Field | Our Field | Transformation |
|-------------|-----------|---------------|
| `description` | `description` | Add Usage/Examples/Best for/See also sections |
| (missing) | `argument-hint` | Infer from command body |
| (missing) | `user-invocable` | Default `true` |
| (missing) | `related` | Link to distill skill + source skill-evaluator |
| (missing) | `thinking` | Set `auto` for complex commands |
| (missing) | `allowed-tools` | Infer minimal set from command body |

### Adaptation Type: `convention-convert`

Major structural changes. This is the **complex** path that generates PRPs.

**UV single-file hook -> Our hook system:**
1. Preserve `#!/usr/bin/env -S uv run --script` shebang and PEP 723 inline deps
2. Place script in `.claude/hooks/`
3. Add entry to `.claude/hooks/hooks.json` under the appropriate event
4. Map the hook's event type (PreToolUse, PostToolUse, Stop, etc.)
5. Add matcher pattern if the hook is tool-specific (e.g., `"Write|Edit"` for validators)
6. PRP includes: source code, target hooks.json structure, event mapping, test plan

**Their command chain -> Our workflow:**
1. Map multi-step command to our workflow format
2. Extract variables, phases, report sections
3. Wire up related components
4. PRP includes: source command, our workflow template, integration points

### Adaptation Type: `full-rewrite`

No direct source file. Generate from pattern description in the evaluation.

1. Read the evaluation's description of the pattern/concept
2. Read similar existing components as structural templates
3. Generate PRP with: concept description, target architecture, acceptance criteria, test plan
4. Place PRP at `PRPs/distill-{component-name}.md`

---

## Section 4: Conflict Detection

When processing multiple evaluations in batch mode, run conflict detection.

### Conflict Types

| Type | Detection | Resolution |
|------|-----------|------------|
| **Destination collision** | Two extractions target same `destination_path` | Higher `eval_score` wins; loser gets `destination_path` with `-alt` suffix |
| **Competing approaches** | Two evals recommend different solutions to same gap (match by `NOVELTY_MAP.capability`) | Present both to user via `AskUserQuestion` |
| **Dependency cycle** | EXT-A depends on EXT-B and EXT-B depends on EXT-A | Flag for manual ordering; suggest breaking the cycle |
| **Naming collision** | Two components would get the same `name` in MANIFEST | Prefix with source repo abbreviation |

### Batch Ranking Algorithm

Score each extraction for batch prioritization:

```
batch_score = (priority_weight * (4 - priority))
            + (score_weight * overall_score)
            + (leverage_weight * combinatorial_value)
            + (effort_penalty * -effort_score)
```

Weights: priority=0.35, score=0.25, leverage=0.25, effort=0.15

Sort extractions by `batch_score` descending. Execute in this order, respecting dependency constraints.

---

## Section 5: Provenance System

### ADO-NNN Records (`adoptions.md`)

Every extracted component gets a provenance record:

```markdown
### ADO-NNN: {component_name}

- **Date**: YYYY-MM-DD
- **Source Repo**: {source_repo}
- **Source File**: {source_file_path}
- **Target Location**: {destination_path}
- **Component Type**: {destination_type}
- **Adaptation**: {adaptation_type}
- **Execution Mode**: {direct | prp}
- **Evaluation**: {eval_name} ({overall_score}/5)
- **Priority**: {priority}
- **Status**: adopted | deferred-to-prp | propagated
- **Propagated To**: []
- **PRP Path**: {prp_path or "N/A"}
```

### ADO Numbering

- Parse existing `adoptions.md` for highest ADO-NNN number
- Increment from there (start at ADO-001 if file is new)
- Never reuse numbers even if records are deleted

### DEC-NNN Records (`decisions.md`)

One decision record per distillation batch:

```markdown
### DEC-NNN: Adopt patterns from {eval_name}

- **Date**: YYYY-MM-DD
- **Context**: skill-evaluator scored {eval_name} at {score}/5 with verdict "{verdict}". Extracted {N} components ({M} direct, {K} as PRPs).
- **Decision**: Extracted {component_list} into template library. Direct: {direct_list}. PRPs: {prp_list}.
- **Alternatives**: (1) Adapt Patterns only, (2) Adopt As-Is, (3) Skip.
```

### Task Records (`tasks.md`)

Add to `## Active` section:

```markdown
- [YYYY-MM-DD] Execute PRP: PRPs/distill-{name}.md (from {eval_name} distillation)
- [YYYY-MM-DD] Test extracted {component} in isolation
- [YYYY-MM-DD] Run /repo-equip on target repos to propagate new patterns
```

---

## Section 6: Propagation Protocol

When `/repo-equip` or `/repo-optimize` runs on a target repo:

1. **Read** `.claude/memory/adoptions.md`
2. **Filter** for records with `Status: adopted` and `Date` within last 30 days
3. **Match** each adoption's `Component Type` against the target repo's tech stack
4. **Include** matching adoptions in the equipment/optimization plan with a note: "Recently adopted from {source_repo} (ADO-NNN)"
5. **After propagation**: Update the ADO record's `Propagated To` field with the target repo name

This requires no code changes to `/repo-equip` or `/repo-optimize` for v1 — they already read `.claude/memory/` during discovery. The adoptions.md file is just additional context they'll pick up naturally. Future versions can add explicit propagation logic.

---

## Section 7: Multi-Model Orchestration

### Fork A: Extraction Planner (Gemini Pro)

**Why Gemini Pro**: 1M context window can ingest the full eval report + source reference submodule + MANIFEST/REGISTRY simultaneously.

**Prompt template**: `.claude/skills/reference-distill/prompts/extraction-planner-agent.md`

**Fork command**:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
  "gemini -p '{FILLED_PROMPT}' --model gemini-3-pro-preview --approval-mode yolo"
```

**Output**: JSON extraction plan at `/tmp/distill-{name}-plan.json`

### Fork B: Adaptation Specialist (Codex)

**Why Codex**: SWE-bench leader; best at understanding code conventions and producing adapted implementations.

**Prompt template**: `.claude/skills/reference-distill/prompts/adaptation-agent.md`

**Fork command**:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex \
  "codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex '{FILLED_PROMPT}'"
```

**Output**: Adapted files at `/tmp/distill-{name}-adapted/`

### Fallback Chain

```
Gemini Pro fails  --> retry with Gemini Flash
Gemini Flash fails --> Sonnet subagent via Task tool
Codex fails       --> Sonnet subagent via Task tool
```

Wait 30s between retries. Note which model was used in the final report.

### Polling

15-second intervals, 5-minute timeout per agent. Check for output files:
```bash
[ -f "/tmp/distill-{name}-plan.json" ] && [ -f "/tmp/distill-{name}-adapted/" ]
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Eval report not found | Check `docs/evaluations/` for `-eval.md` files; re-run `/skill-evaluator` |
| Source submodule empty | Run `git submodule update --init references/{name}` |
| Gemini/Codex unavailable | Automatic fallback to Sonnet subagent; check API keys |
| MANIFEST validation fails | Check for duplicate names or missing paths; run `validate-docs.py` for details |
| Frontmatter validation fails | Compare against schema in `validate-docs.py`; check required fields |
| ADO numbering conflict | Parser finds highest existing number; delete stale records if needed |
| Hooks.json malformed | Read current hooks.json before modifying; validate JSON after write |

## Dependencies

- `skill-evaluator` — must have produced evaluation reports first
- `fork-terminal` — for multi-model agent forking
- `validate-docs.py` — for post-integration validation
- `install-global.py` — for symlink creation
