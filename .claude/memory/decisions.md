# Decisions

### DEC-006: Default Gemini model to `auto` (2026-02-11)
Preview models (`gemini-3-pro-preview`, `gemini-3-flash-preview`) return 429/RESOURCE_EXHAUSTED frequently. Use `--model auto` as safe default; use `gemini-2.5-flash` for reliability in parallel tasks. Only use specific models when user explicitly requests it.

### DEC-009: Cap parallel Gemini at 2 concurrent (2026-02-11)
5 parallel Gemini forks caused 100% failure rate due to `cloudcode-pa.googleapis.com` concurrency constraints (not RPM). Max 2 concurrent forks, staggered by 30-60s. Prefer `gemini-2.5-flash` for parallel tasks.

### DEC-010: OAuth takes precedence over API key (2026-02-11)
Gemini CLI ignores `GEMINI_API_KEY` when cached OAuth tokens exist in `~/.gemini/oauth_creds.json`. To force API key routing: clear OAuth cache or use E2B sandbox. `GOOGLE_GENAI_USE_VERTEXAI=true` overrides both.

### DEC-011: Executor retry/fallback chain with error classification (2026-02-11)
`gemini_task_executor.py` upgraded with `classify_error()` (QUOTA_EXHAUSTED, MODEL_CAPACITY, AUTH_FAILED, TIMEOUT, CLI_NOT_FOUND, PERMISSION_DENIED), `build_auth_env()` for `--auth-mode oauth|api-key|vertex-ai`, model fallback chain via `--fallback-models`, and `--retry-delay`/`--max-retries` flags. `done.json` now includes `error_type`, `auth_mode`, `retries_used`.

## Archived

_Completed implementation decisions moved here to save context budget. See git history for full details._

- **DEC-002** (2026-02-09): Created `reference-distill` as 5-phase eval-to-integration pipeline
- **DEC-003** (2026-02-09): Adopted 9 components from claude-code-hooks-mastery (3.50/5 eval)
- **DEC-004** (2026-02-10): Merged ecosystem recommender into repo-equip/optimize engine
- **DEC-005** (2026-02-10): Removed false API key gates from Codex/Gemini delegators (use OAuth)
- **DEC-007** (2026-02-11): Added `set -o pipefail` to executor shell pipes
- **DEC-008** (2026-02-11): Clean stale done.json/result files before executor retry
