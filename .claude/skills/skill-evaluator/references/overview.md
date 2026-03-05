# Skill Evaluator — Reference Overview

## Key Concepts

- **Parallel three-agent architecture**: Codex evaluates structural quality, Gemini Pro assesses ecosystem fit (using 1M context to ingest the entire ecosystem snapshot), and Gemini Flash analyzes risk and adoption. Opus synthesizes all three into a coherent verdict.
- **Synthesis is not merging**: The final report must resolve contradictions between agents and produce a coherent narrative — not a summary of summaries. Weight the recommendation based on the user's intended use case.
- **Evaluation depth controls cost**: Full mode runs all three agents (target: < 5 min). Quick mode skips risk analysis and uses Gemini Flash instead of Pro for ecosystem (target: < 2 min).
- **Creator video context enriches analysis**: If the component has associated videos (VIDEOS.md or user-provided URLs), transcripts are downloaded and appended to the ecosystem snapshot to capture author intent and maintenance signals.

## Decision Criteria

### When to Use

| Situation | Use Skill Evaluator? |
|-----------|---------------------|
| Evaluating a recommended skill/plugin before adding it | Yes |
| Assessing a reference submodule for adoption | Yes |
| Pre-adoption due diligence on any external component | Yes |
| Comparing multiple candidate skills/plugins | Yes (parallel pipelines) |
| Reviewing your own code | No — use /code-review |
| Trivial single-file script | No — just read it |
| Internal refactoring decisions | No — use codebase-analyst |

### Evaluation Depth Selection

| Mode | Agents | Model for Ecosystem | When to Use |
|------|--------|---------------------|-------------|
| full | 3 (structural + ecosystem + risk) | Gemini Pro | Default for any real adoption decision |
| quick | 2 (structural + ecosystem) | Gemini Flash | Time-constrained, low-stakes components |

### Model Assignment Rationale

| Agent | Model | Why |
|-------|-------|-----|
| Structural Quality | gpt-5.2-codex | SWE-bench leader — best at judging code architecture and testing patterns |
| Ecosystem Fit | gemini-3-pro-preview | 1M context ingests entire ecosystem snapshot alongside target |
| Risk & Adoption | gemini-3-flash-preview | Lighter analysis (git log, dep count) doesn't need Pro-level reasoning |

## Quick Reference

### Verdict Options

| Verdict | Meaning |
|---------|---------|
| Adopt | Integrate as-is |
| Extract Components | Use specific parts, not the whole thing |
| Adapt Patterns | Learn from it, reimplement locally |
| Skip | Not worth the integration effort |

### Output Files per Evaluation

```
docs/evaluations/
  {name}-structural.md   # Codex raw output
  {name}-ecosystem.md    # Gemini Pro raw output
  {name}-risk.md         # Gemini Flash raw output (skipped in quick mode)
  {name}-eval.md         # Final synthesized report (Opus)
```

### Fallback Chain

```
Gemini Flash fails (429/capacity) → retry with Gemini Pro
Gemini Pro fails (429/capacity)   → Sonnet subagent via Task tool
Codex fails                       → Sonnet subagent via Task tool
```

Wait 30s before retrying to allow rate limits to clear. Note which fallback was used in the final report.

### Red Flags to Watch For

- Structural quality says "great testing" but risk says "unmaintained" — resolve the contradiction; don't average it away
- Ecosystem snapshot empty — run from project root with MANIFEST.json present
- Agent output missing after timeout — check `/tmp/fork_*.log` before applying fallback
- Multiple targets: run parallel pipelines, then add a comparison table to each report

### Pre-Fork Inventory Commands

```bash
# File listing
find {TARGET_PATH} -type f | head -200

# Git history (if available)
git -C {TARGET_PATH} log --oneline -20 2>/dev/null

# Docs presence check
ls {TARGET_PATH}/README* {TARGET_PATH}/SKILL.md {TARGET_PATH}/docs/ 2>/dev/null
```
