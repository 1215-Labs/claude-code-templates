# Decisions

## Decisions

### DEC-001: Example Decision Format

- **Date**: YYYY-MM-DD
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Alternatives**: What else was considered

### DEC-002: Create reference-distill skill for evaluation-to-integration pipeline

- **Date**: 2026-02-09
- **Context**: After running /skill-evaluator on claude-code-hooks-mastery (3.50/5, verdict: Extract Components), we identified a pipeline gap between evaluation and integration. No tool existed to act on evaluation verdicts.
- **Decision**: Created `reference-distill` skill + `/reference-distill` command as a 5-phase workflow: parse eval reports, plan extractions with multi-model agents (Gemini Pro + Codex), adapt to our conventions, register in MANIFEST/REGISTRY, and track provenance in adoptions.md. Hybrid execution: direct for simple adaptations (1-3 effort points), PRP generation for complex ones (4+ points).
- **Alternatives**: (1) Manual extraction — error-prone and inconsistent, (2) Full automation without PRPs — too risky for complex convention conversions, (3) Single-model approach — misses Gemini's 1M context advantage for extraction planning.

### DEC-003: Adopt patterns from claude-code-hooks-mastery

- **Date**: 2026-02-09
- **Context**: skill-evaluator scored claude-code-hooks-mastery at 3.50/5 with verdict "Extract Components". Extracted 9 components (5 direct, 4 as PRPs).
- **Decision**: Directly adopted: ruff-validator (PostToolUse lint), ty-validator (PostToolUse type check), meta-agent (agent generator), team-builder (engineering agent), team-validator (read-only validation agent). Generated PRPs for: dangerous-command-blocker (rm -rf + .env protection), prompt-validator (UserPromptSubmit hook), uv-hook-template (UV single-file script skill), status-line-context (context window progress bar). Deferred: output styles, TTS, hooks-in-frontmatter.
- **Alternatives**: (1) Adopt As-Is — symlink from submodule, but high risk with single-maintainer dependency, (2) Adapt Patterns — implement from scratch, 6-12 weeks effort, (3) Skip — miss high-ROI patterns that fill genuine ecosystem gaps.
