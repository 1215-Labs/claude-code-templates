# Decisions

### DEC-012: Retire Gemini fork terminals, adopt OpenCode delegator (2026-03-09)
Gemini fork terminals never worked reliably (429 rate limits, auth routing complexity, concurrency constraints). Replaced with OpenCode CLI delegator which provides multi-provider model access (OpenAI flat-rate via ChatGPT Pro, GLM-5 free, Kimi K2.5 cheap, Antigravity free Gemini proxy) and oh-my-opencode agent harness. Synced from agent-os. Anthropic models blocked in OpenCode to avoid API costs — use Claude Code (Max Plan) for Claude tasks.

## Archived

_Completed implementation decisions moved here to save context budget. See git history for full details._

- **DEC-002** (2026-02-09): Created `reference-distill` as 5-phase eval-to-integration pipeline
- **DEC-003** (2026-02-09): Adopted 9 components from claude-code-hooks-mastery (3.50/5 eval)
- **DEC-004** (2026-02-10): Merged ecosystem recommender into repo-equip/optimize engine
- **DEC-005** (2026-02-10): Removed false API key gates from Codex/Gemini delegators (use OAuth)
- **DEC-007** (2026-02-11): Added `set -o pipefail` to executor shell pipes
- **DEC-008** (2026-02-11): Clean stale done.json/result files before executor retry
- **DEC-006** (2026-02-11): Default Gemini model to `auto` — _Retired: Gemini fork terminals removed (DEC-012)_
- **DEC-009** (2026-02-11): Cap parallel Gemini at 2 concurrent — _Retired: Gemini fork terminals removed (DEC-012)_
- **DEC-010** (2026-02-11): OAuth takes precedence over API key — _Retired: Gemini fork terminals removed (DEC-012)_
- **DEC-011** (2026-02-11): Executor retry/fallback chain with error classification — _Retired: Gemini fork terminals removed (DEC-012)_
