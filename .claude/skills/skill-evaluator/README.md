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
2. **OpenCode oracle** (openai/gpt-5.2 via oracle agent) - Ecosystem fit: novelty, gaps, overlap, combinations
3. **OpenCode momus** (openai/gpt-5.2 via momus agent) - Risk & adoption: security, maintenance, dependencies, cost

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
    ecosystem-fit-agent.md              # OpenCode oracle prompt template
    risk-adoption-agent.md              # OpenCode momus prompt template
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
- `opencode` CLI (`go install github.com/opencode-ai/opencode@latest`)
- `OPENAI_API_KEY` environment variable (OpenCode handles its own auth)

## Related Components

| Component | Relationship |
|-----------|-------------|
| `fork-terminal` | Used to dispatch agents |
| `multi-model-orchestration` | Shared orchestration patterns |
| `/orchestrate` | General-purpose task delegation |
| `codebase-analyst` | Internal code analysis (use instead for own code) |
| `/code-review` | Code review (use instead for PRs) |
