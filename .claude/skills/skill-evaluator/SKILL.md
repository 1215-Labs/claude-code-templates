---
name: skill-evaluator
description: Use when evaluating external skills, plugins, or reference submodules before adoption — assesses structural quality, ecosystem fit, and adoption risk using parallel agents
---

# Skill Evaluator

Evaluate external skills/plugins before adoption by dispatching parallel agents (Codex for structural quality, Gemini Pro for ecosystem fit, Gemini Flash for risk analysis), then synthesizing a decision-ready report with adoption strategies.

## When to Use

- Evaluating a recommended skill/plugin before adding it
- Assessing reference submodules for adoption
- Pre-adoption due diligence on any external component
- Comparing multiple candidate skills/plugins

## When NOT to Use

- Reviewing your own code (use `/code-review`)
- Trivial single-file scripts (just read them)
- Internal refactoring decisions (use `codebase-analyst`)

## Variables

EVALUATION_DEPTH: full | quick
OUTPUT_DIR: docs/evaluations
STRUCTURAL_MODEL: gpt-5.2-codex
ECOSYSTEM_MODEL: gemini-3-pro-preview
RISK_MODEL: gemini-3-flash-preview

## Architecture

```
                      +-- Codex 5.2: Structural Quality --> {name}-structural.md
                      |
User Request --> Opus +-- Gemini Pro: Ecosystem Fit ------> {name}-ecosystem.md
                      |
                      +-- Gemini Flash: Risk & Adoption --> {name}-risk.md

                Then: Opus reads all reports -> synthesizes -> {name}-eval.md
```

**Model rationale:**
- **Codex** for structural quality: SWE-bench leader, best at judging code architecture and testing patterns
- **Gemini Pro** for ecosystem fit: 1M context ingests entire ecosystem snapshot alongside target
- **Gemini Flash** for risk: Lighter analysis (git log, dependency counting) doesn't need Pro-level reasoning

## Workflow

### Step 1: Parse Input

Extract from user request:
- `TARGET_PATHS` - Local paths, reference submodule paths, or git URLs
- `SKILL_NAMES` - Human-readable names for each target
- `INTENDED_USE` - What the user wants to use the skill for (optional)
- `EVALUATION_DEPTH` - "full" (3 agents) or "quick" (2 agents, skip risk)

**Input resolution:**
- Local path: Use directly
- Reference submodule (`references/X`): Use directly
- Git URL: Clone to `/tmp/skill-eval-{name}` first

### Step 2: Gather Context

#### Pre-Fork Inventory (target)

Run lightweight analysis on the target:

```bash
# File listing with sizes
find {TARGET_PATH} -type f | head -200

# Line counts by type
find {TARGET_PATH} -type f -name "*.md" -o -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.json" | xargs wc -l 2>/dev/null | tail -1

# Git history summary (if available)
git -C {TARGET_PATH} log --oneline -20 2>/dev/null

# README/docs presence
ls {TARGET_PATH}/README* {TARGET_PATH}/SKILL.md {TARGET_PATH}/docs/ 2>/dev/null
```

Save inventory to `/tmp/skill-eval-{name}-inventory.txt`.

#### Ecosystem Snapshot (our components)

Generate a snapshot of current installed components:

```bash
# Current skills
ls -la ~/.claude/skills/ 2>/dev/null

# Current agents
ls -la ~/.claude/agents/ 2>/dev/null

# Current commands
find ~/.claude/commands/ -name "*.md" 2>/dev/null

# MANIFEST summary
cat MANIFEST.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'{t}: {len(d[\"components\"][t])}') for t in d['components'] if isinstance(d['components'][t], list)]" 2>/dev/null
```

Save snapshot to `/tmp/skill-eval-ecosystem-snapshot.txt`.

### Step 3: Create Output Directory

```bash
mkdir -p docs/evaluations
```

### Step 4: Fork Agents

Read the prompt templates, fill variables, and fork via fork-terminal.

**Read:** `.claude/skills/fork-terminal/tools/fork_terminal.py` to understand invocation.

#### Agent 1: Structural Quality (Codex)

Read prompt template: `.claude/skills/skill-evaluator/prompts/structural-quality-agent.md`

Fill variables:
- `{TARGET_PATH}` - Path to the skill being evaluated
- `{SKILL_NAME}` - Human-readable name
- `{INVENTORY}` - Pre-fork inventory contents
- `{OUTPUT_FILE}` - `docs/evaluations/{name}-structural.md`

Fork:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex \
  "codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex '{FILLED_PROMPT}'"
```

#### Agent 2: Ecosystem Fit (Gemini Pro)

Read prompt template: `.claude/skills/skill-evaluator/prompts/ecosystem-fit-agent.md`

Fill variables:
- `{TARGET_PATH}` - Path to the skill being evaluated
- `{SKILL_NAME}` - Human-readable name
- `{ECOSYSTEM_SNAPSHOT}` - Ecosystem snapshot contents
- `{OUTPUT_FILE}` - `docs/evaluations/{name}-ecosystem.md`

Fork:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
  "gemini -p '{FILLED_PROMPT}' --model gemini-3-pro-preview --approval-mode yolo"
```

#### Agent 3: Risk & Adoption (Gemini Flash)

*Skip this agent if `EVALUATION_DEPTH` is "quick".*

Read prompt template: `.claude/skills/skill-evaluator/prompts/risk-adoption-agent.md`

Fill variables:
- `{TARGET_PATH}` - Path to the skill being evaluated
- `{SKILL_NAME}` - Human-readable name
- `{OUTPUT_FILE}` - `docs/evaluations/{name}-risk.md`

Fork:
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
  "gemini -p '{FILLED_PROMPT}' --model gemini-3-flash-preview --approval-mode yolo"
```

### Step 5: Poll for Completion

Wait for agent output files to appear:

```bash
# Poll every 15 seconds, timeout after 5 minutes
for i in $(seq 1 20); do
  FOUND=0
  [ -f "docs/evaluations/{name}-structural.md" ] && FOUND=$((FOUND+1))
  [ -f "docs/evaluations/{name}-ecosystem.md" ] && FOUND=$((FOUND+1))
  [ -f "docs/evaluations/{name}-risk.md" ] && FOUND=$((FOUND+1))  # skip check if quick mode

  EXPECTED=3  # or 2 for quick mode
  [ "$FOUND" -ge "$EXPECTED" ] && break
  sleep 15
done
```

Check logs on timeout:
```bash
tail -20 /tmp/fork_codex_*.log /tmp/fork_gemini_*.log 2>/dev/null
```

### Step 6: Synthesize Report

Read all agent reports (executive summaries first, then details as needed).

Read the report template: `.claude/skills/skill-evaluator/templates/evaluation-report.md`

**Synthesis guidelines:**
- Do NOT just merge agent outputs — synthesize a coherent narrative
- Resolve contradictions between agents (e.g., structural quality says "great testing" but risk says "unmaintained" — which is true?)
- Weight the final recommendation based on the user's `INTENDED_USE`
- Executive summary should be YOUR assessment, not a summary of summaries

### Step 7: Write Report

Write final report to `docs/evaluations/{name}-eval.md` following the template.

### Step 8: Present to User

Show:
1. One-line verdict (Adopt / Extract Components / Adapt Patterns / Skip)
2. Executive summary (2-3 sentences)
3. Weighted score
4. Top recommendation with effort estimate
5. Link to full report

## Quick Mode

When `EVALUATION_DEPTH` is "quick":
- Fork only 2 agents (structural + ecosystem)
- Use Gemini Flash instead of Pro for ecosystem
- Skip risk analysis entirely
- Produce abbreviated report (no risk section)
- Target: < 2 minutes wall-clock

## Multi-Target Evaluation

When evaluating multiple targets:
1. Run parallel pipelines (one per target)
2. After all complete, add a comparison table to each report
3. Present ranked recommendation

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Agent output missing | Check `/tmp/fork_*.log` for errors |
| Git clone fails | Verify URL, check network, try SSH vs HTTPS |
| Codex API key missing | Set `OPENAI_API_KEY` in environment |
| Gemini API key missing | Set `GEMINI_API_KEY` in environment |
| Timeout waiting for agents | Increase poll timeout, check agent logs |
| Ecosystem snapshot empty | Run from project root with MANIFEST.json present |

## Dependencies

Requires the `fork-terminal` skill and its dependencies:
- `python3`, `xterm` (or other terminal emulator)
- `codex` CLI (`npm install -g @openai/codex`)
- `gemini` CLI (`npm install -g @google/gemini-cli`)

## Output Conventions

```
docs/evaluations/
  {name}-structural.md   # Codex agent output (raw)
  {name}-ecosystem.md    # Gemini Pro agent output (raw)
  {name}-risk.md         # Gemini Flash agent output (raw)
  {name}-eval.md         # Final synthesized report (Opus)
```
