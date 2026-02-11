# Decisions

### DEC-002: reference-distill skill (2026-02-09)
Created `reference-distill` as 5-phase evaluation-to-integration pipeline. Hybrid: direct for simple (1-3 effort), PRP for complex (4+). Uses Gemini for extraction planning, Codex for implementation.

### DEC-003: Adopt claude-code-hooks-mastery patterns (2026-02-09)
Extracted 9 components (5 direct, 4 PRPs) from 3.50/5 eval. Direct: ruff-validator, ty-validator, meta-agent, team-builder, team-validator. PRPs: dangerous-command-blocker, prompt-validator, uv-hook-template, status-line-context. Deferred: output styles, TTS, hooks-in-frontmatter.

### DEC-004: Merge ecosystem into repo-equip/optimize (2026-02-10)
Merged recommender's 18 MCP servers + 13 plugins into `repo-equip-engine` SKILL.md. 7 files changed, all additive. Codex-then-Gemini-validate pipeline.

### DEC-005: Remove delegator API key gates (2026-02-10)
Codex/Gemini authenticate via OAuth, not API keys. False key checks caused Sonnet delegator to bypass `codex_task_executor.py` and run bare `codex exec` without write perms. Removed checks from both delegator agents + command files. Added `--model auto` fallback for Gemini 429s.
