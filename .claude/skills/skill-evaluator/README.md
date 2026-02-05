# Skill Evaluator

Evaluate external skills/plugins before adoption using parallel agents.

## Quick Info

| Field | Value |
|-------|-------|
| **Category** | Evaluation / Orchestration |
| **Status** | Beta |
| **Deployment** | Global |
| **User-invocable** | Yes |
| **Version** | 1.0.0 |

## What It Does

Dispatches 3 specialized agents in parallel to analyze a target skill/plugin:

1. **Codex** (gpt-5.2-codex) - Structural quality: code architecture, docs, tests, metadata
2. **Gemini Pro** (gemini-3-pro-preview) - Ecosystem fit: novelty, gaps, overlap, combinations
3. **Gemini Flash** (gemini-3-flash-preview) - Risk & adoption: security, maintenance, dependencies, cost

Opus then synthesizes all reports into a single decision-ready evaluation with 3 adoption strategies.

## Activation Phrases

- "Evaluate this skill before we adopt it"
- "Should we add this plugin to our ecosystem?"
- "Assess references/last30days-skill for adoption"
- "Compare these two skills"

## Files

```
skill-evaluator/
  SKILL.md                              # Main orchestration logic
  README.md                             # This file
  prompts/
    structural-quality-agent.md         # Codex prompt template
    ecosystem-fit-agent.md              # Gemini Pro prompt template
    risk-adoption-agent.md              # Gemini Flash prompt template
  templates/
    evaluation-report.md                # Final report template
```

## Output

Reports are written to `docs/evaluations/`:
- `{name}-structural.md` - Raw structural quality analysis
- `{name}-ecosystem.md` - Raw ecosystem fit analysis
- `{name}-risk.md` - Raw risk & adoption analysis
- `{name}-eval.md` - Final synthesized report

## Modes

- **Full** (default): All 3 agents, comprehensive report
- **Quick**: 2 agents (structural + ecosystem), abbreviated report, faster

## Dependencies

- `fork-terminal` skill (for agent dispatch)
- `codex` CLI (`npm install -g @openai/codex`)
- `gemini` CLI (`npm install -g @google/gemini-cli`)
- `OPENAI_API_KEY` and `GEMINI_API_KEY` environment variables

## Related Components

| Component | Relationship |
|-----------|-------------|
| `fork-terminal` | Used to dispatch agents |
| `multi-model-orchestration` | Shared orchestration patterns |
| `/orchestrate` | General-purpose task delegation |
| `codebase-analyst` | Internal code analysis (use instead for own code) |
| `/code-review` | Code review (use instead for PRs) |
