# Skill Evaluator — Reference Overview

Supplementary reference for the `skill-evaluator` skill. Read SKILL.md for full instructions.

## When to Use vs. Alternatives

| Situation | Use |
|-----------|-----|
| Evaluating an external skill/plugin before adopting it | skill-evaluator |
| Assessing a reference submodule for integration | skill-evaluator |
| Comparing 2-3 candidate skills | skill-evaluator (multi-target mode) |
| Reviewing your own code quality | `/code-review` instead |
| Single-file script, trivial to read | Just read it directly |
| Deciding whether to refactor an internal component | `codebase-analyst` agent |

## Evaluation Depth Decision

| Signal | Depth | Agents Used |
|--------|-------|-------------|
| Critical dependency, production use | `full` | 3 agents (structural + ecosystem + risk) |
| Quick viability check before investing time | `quick` | 2 agents (structural + ecosystem, Flash not Pro) |
| Time-sensitive, just need a go/no-go | `quick` | Faster, ~2 min wall clock |
| Unmaintained or old repo suspected | `full` | Risk agent catches maintenance signals |

## Three Agent Roles and Their Lens

| Agent | Model | What It Looks For |
|-------|-------|-------------------|
| Structural Quality (Codex) | gpt-5.2-codex | Code architecture, testing patterns, API design, technical debt |
| Ecosystem Fit (OpenCode) | openai/gpt-5.2 via oracle agent | Overlap with existing components, naming conflicts, integration effort |
| Risk & Adoption (OpenCode) | openai/gpt-5.2 via oracle agent | Maintenance signals, dependency count, git activity, license |

**Why these models:** Codex (SWE-bench leader) judges code quality best. OpenCode's 1M context ingests the ecosystem snapshot alongside the target. Flash is sufficient for lighter risk signals (commit frequency, dep count).

## Pre-Fork Inventory — What to Collect

Before spawning agents, gather:

```bash
# File listing (understand scope)
find {TARGET_PATH} -type f | head -200

# Line counts by file type
find {TARGET_PATH} -type f \( -name "*.md" -o -name "*.py" -o -name "*.ts" -o -name "*.js" -o -name "*.json" \) | xargs wc -l 2>/dev/null | tail -1

# Git history (maintenance signal)
git -C {TARGET_PATH} log --oneline -20 2>/dev/null

# Docs presence
ls {TARGET_PATH}/README* {TARGET_PATH}/SKILL.md {TARGET_PATH}/docs/ 2>/dev/null
```

Save to `/tmp/skill-eval-{name}-inventory.txt`. This gives agents context without them exploring from scratch.

## Ecosystem Snapshot — What to Collect

```bash
ls -la ~/.claude/skills/
ls -la ~/.claude/agents/
find ~/.claude/commands/ -name "*.md"
# MANIFEST component counts
cat MANIFEST.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(f'{t}: {len(d[\"components\"][t])}') for t in d['components'] if isinstance(d['components'][t], list)]"
```

Save to `/tmp/skill-eval-ecosystem-snapshot.txt`. The Ecosystem Fit agent uses this to detect overlap with existing components.

## Creator Video Context (Optional Enhancement)

If the reference submodule has a `VIDEOS.md` or user provides YouTube URLs, download and transform transcripts before forking. This enriches agents with:
- Author's design intent (explains "why" decisions not visible in code)
- Known limitations mentioned in video but undocumented
- Maintenance philosophy and future plans

Add transformed content to the ecosystem snapshot under `## Creator Video Context`.

## Fallback Chain

```
OpenCode fails (429/capacity) → retry with OpenCode
OpenCode fails (429/capacity)   → Sonnet subagent via Task tool
Codex fails                       → Sonnet subagent via Task tool
```

Wait 30 seconds before retry to allow rate limits to clear. Always note which fallback was used in the final report.

## Synthesis Principles

Do NOT simply merge agent outputs. When synthesizing:

1. Resolve contradictions: if Structural says "great testing" but Risk says "last commit 18 months ago" — the tests are likely stale or unmaintained
2. Weight by intended use: if user wants to adopt wholesale vs. extract patterns, the structural quality matters more vs. less
3. Your executive summary is YOUR assessment, not a summary of summaries

## Final Verdict Options

| Verdict | Meaning |
|---------|---------|
| Adopt | Integrate as-is with minimal adaptation |
| Extract Components | Take specific files/functions, not the whole skill |
| Adapt Patterns | Use the concepts, rewrite for your conventions |
| Skip | Not worth the integration effort given the gaps |

Always pair verdict with an effort estimate (hours, not days/weeks).

## Output File Locations

```
docs/evaluations/
  {name}-structural.md   # Codex raw output
  {name}-ecosystem.md    # OpenCode raw output
  {name}-risk.md         # OpenCode raw output (full mode only)
  {name}-eval.md         # Final synthesized report (Opus)
```
