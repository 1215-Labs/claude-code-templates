# Decisions

### DEC-002: reference-distill skill (2026-02-09)
Created `reference-distill` as 5-phase evaluation-to-integration pipeline. Hybrid: direct for simple (1-3 effort), PRP for complex (4+). Uses Gemini for extraction planning, Codex for implementation.

### DEC-003: Adopt claude-code-hooks-mastery patterns (2026-02-09)
Extracted 9 components (5 direct, 4 PRPs) from 3.50/5 eval. Direct: ruff-validator, ty-validator, meta-agent, team-builder, team-validator. PRPs: dangerous-command-blocker, prompt-validator, uv-hook-template, status-line-context. Deferred: output styles, TTS, hooks-in-frontmatter.

### DEC-004: Merge ecosystem into repo-equip/optimize (2026-02-10)
Merged recommender's 18 MCP servers + 13 plugins into `repo-equip-engine` SKILL.md. 7 files changed, all additive. Codex-then-Gemini-validate pipeline.

### DEC-005: Remove delegator API key gates (2026-02-10)
Codex/Gemini authenticate via OAuth, not API keys. False key checks caused Sonnet delegator to bypass `codex_task_executor.py` and run bare `codex exec` without write perms. Removed checks from both delegator agents + command files. Added `--model auto` fallback for Gemini 429s.

### DEC-006: Default Gemini model to `auto` (2026-02-11)
Preview models (`gemini-3-pro-preview`, `gemini-3-flash-preview`) return 429/RESOURCE_EXHAUSTED frequently. Use `--model auto` as safe default; use `gemini-2.5-flash` for reliability in parallel tasks. Only use specific models when user explicitly requests it.

### DEC-007: Use `set -o pipefail` with tee (2026-02-11)
Shell pipe `cli | tee log` returns tee's exit code (always 0), masking CLI failures. Added `set -o pipefail;` prefix to all executor shell commands so the pipe returns the first non-zero exit code.

### DEC-008: Clean stale files before execution (2026-02-11)
Same slug produces identical file paths. On retries, orchestrator reads stale `done.json` from a previous run. Executors now call `Path(stale).unlink(missing_ok=True)` at startup for done.json and result files.

### DEC-009: Cap parallel Gemini at 2 concurrent (2026-02-11)
5 parallel Gemini forks caused 100% failure rate due to `cloudcode-pa.googleapis.com` concurrency constraints (not RPM). Max 2 concurrent forks, staggered by 30-60s. Prefer `gemini-2.5-flash` for parallel tasks.

### DEC-010: OAuth takes precedence over API key (2026-02-11)
Gemini CLI ignores `GEMINI_API_KEY` when cached OAuth tokens exist in `~/.gemini/oauth_creds.json`. To force API key routing: clear OAuth cache or use E2B sandbox. `GOOGLE_GENAI_USE_VERTEXAI=true` overrides both.

### DEC-011: Executor retry/fallback chain with error classification (2026-02-11)
`gemini_task_executor.py` upgraded with `classify_error()` (QUOTA_EXHAUSTED, MODEL_CAPACITY, AUTH_FAILED, TIMEOUT, CLI_NOT_FOUND, PERMISSION_DENIED), `build_auth_env()` for `--auth-mode oauth|api-key|vertex-ai`, model fallback chain via `--fallback-models`, and `--retry-delay`/`--max-retries` flags. `done.json` now includes `error_type`, `auth_mode`, `retries_used`.
