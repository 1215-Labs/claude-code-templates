# last30days-skill Structural Evaluation

**Executive Summary**

Overall, the skill is thoughtfully modularized with clear separation between orchestration, API access, normalization, scoring, and rendering. The documentation is extensive and example-rich, but there are a few mismatches with current behavior (notably the “at least one key required” statement despite web-only fallback), and the WebSearch pipeline is only partially wired. Tests cover many core utilities, yet omit several critical paths (WebSearch, env validation, HTTP error handling, and the main orchestrator). I recommend adoption with light remediation of the WebSearch integration and documentation accuracy.

**Scorecard**

| Dimension | Score (1-5) | Weight | Weighted |
| --- | --- | --- | --- |
| Code Architecture | 4 | 25% | 1.00 |
| Documentation Quality | 4 | 20% | 0.80 |
| Testing | 3 | 20% | 0.60 |
| Metadata & Distribution | 3 | 15% | 0.45 |
| Code Quality Signals | 4 | 20% | 0.80 |
| **Total** | **3.65 / 5** | **100%** | **3.65** |

**Detailed Findings**

**Code Architecture (4/5)**

- Strong separation of concerns across `scripts/lib/` (env, dates, cache, HTTP, model selection, normalization, scoring, dedupe, rendering), with `scripts/last30days.py` acting as an orchestrator. This keeps modules cohesive and discoverable. `references/last30days-skill/SPEC.md:11-25`.
- The main orchestrator is readable and staged (search → normalize → filter → score → dedupe → render). `references/last30days-skill/scripts/last30days.py:161-475`.
- WebSearch support is structurally present (schema, scoring, parsing, dedupe) but not integrated into the orchestration flow; `run_research` only signals “web_needed” and never ingests or scores web results. `references/last30days-skill/scripts/last30days.py:161-274`, `references/last30days-skill/scripts/lib/websearch.py:1-401`, `references/last30days-skill/scripts/lib/schema.py:141-185`, `references/last30days-skill/scripts/lib/score.py:224-278`.
- Cache infrastructure exists but is not used for research results (only model selection is cached). This is a mismatch with the caching claims and UI hooks. `references/last30days-skill/scripts/lib/cache.py:1-152`, `references/last30days-skill/scripts/lib/render.py:75-79`, `references/last30days-skill/scripts/lib/schema.py:193-223`.

**Documentation Quality (4/5)**

- README is comprehensive with concrete examples, usage, and output expectations. `references/last30days-skill/README.md:1-721`.
- SKILL.md provides clear operational guidance, mode behavior, and research flow. `references/last30days-skill/SKILL.md:1-176`.
- SPEC.md summarizes architecture and CLI options cleanly. `references/last30days-skill/SPEC.md:1-75`.
- Documentation mismatch: README claims “At least one key is required,” but the implementation supports web-only fallback via `get_available_sources` and `validate_sources`. This should be corrected to avoid user confusion. `references/last30days-skill/README.md:702-707`, `references/last30days-skill/scripts/lib/env.py:57-112`, `references/last30days-skill/scripts/last30days.py:345-362`.

**Testing (3/5)**

- Unit tests cover core utilities: cache keying, dates, dedupe, model selection, normalization, scoring, rendering, and model fallback logic. `references/last30days-skill/tests/test_cache.py:1-59`, `references/last30days-skill/tests/test_dates.py:1-114`, `references/last30days-skill/tests/test_dedupe.py:1-111`, `references/last30days-skill/tests/test_models.py:1-135`, `references/last30days-skill/tests/test_normalize.py:1-138`, `references/last30days-skill/tests/test_score.py:1-168`, `references/last30days-skill/tests/test_render.py:1-116`, `references/last30days-skill/tests/test_openai_reddit.py:1-77`.
- Missing tests for WebSearch parsing/scoring, env source validation, HTTP retry/error handling, and main orchestrator behavior (including web-only mode). `references/last30days-skill/scripts/lib/websearch.py:1-401`, `references/last30days-skill/scripts/lib/env.py:93-149`, `references/last30days-skill/scripts/lib/http.py:34-114`, `references/last30days-skill/scripts/last30days.py:161-521`.
- No integration tests for end-to-end flow or cache usage in real runs.

**Metadata & Distribution (3/5)**

- SKILL.md frontmatter is present and specifies tools, agent, and context. `references/last30days-skill/SKILL.md:1-10`.
- There is no explicit versioning field in the skill metadata or in the repo artifacts for this skill; changelog is outside the target folder. (No `version` in SKILL.md frontmatter). `references/last30days-skill/SKILL.md:1-10`.
- Dependencies are implicit (stdlib + external APIs) but no lockfile or dependency declaration exists within the skill folder. `references/last30days-skill/scripts/lib/http.py:1-125`, `references/last30days-skill/scripts/lib/openai_reddit.py:43-173`, `references/last30days-skill/scripts/lib/xai_x.py:17-115`.

**Code Quality Signals (4/5)**

- Input validation and normalization are consistent across sources (date format checks, URL checks, relevance clamping). `references/last30days-skill/scripts/lib/openai_reddit.py:257-275`, `references/last30days-skill/scripts/lib/xai_x.py:178-215`, `references/last30days-skill/scripts/lib/websearch.py:304-339`.
- Error handling is generally defensive (HTTP errors wrapped, per-item failures in enrichment do not crash). `references/last30days-skill/scripts/lib/http.py:72-114`, `references/last30days-skill/scripts/last30days.py:258-268`, `references/last30days-skill/scripts/lib/reddit_enrich.py:193-231`.
- Several silent failure paths could mask issues (cache writes ignored, JSON parse failures ignored). `references/last30days-skill/scripts/lib/cache.py:98-113`, `references/last30days-skill/scripts/lib/openai_reddit.py:245-249`, `references/last30days-skill/scripts/lib/xai_x.py:172-176`.
- No hardcoded secrets are present; key handling uses environment or config file. `references/last30days-skill/scripts/lib/env.py:34-47`, `references/last30days-skill/README.md:15-21`.

**Critical Files**

| File | Why It Matters |
| --- | --- |
| `references/last30days-skill/scripts/last30days.py` | Orchestrator for the full pipeline, includes source selection, date range, scoring, and output. `references/last30days-skill/scripts/last30days.py:161-521`. |
| `references/last30days-skill/scripts/lib/openai_reddit.py` | OpenAI Responses API search prompt and parsing logic for Reddit. `references/last30days-skill/scripts/lib/openai_reddit.py:53-278`. |
| `references/last30days-skill/scripts/lib/xai_x.py` | xAI Responses API usage and parsing for X content. `references/last30days-skill/scripts/lib/xai_x.py:26-217`. |
| `references/last30days-skill/scripts/lib/websearch.py` | WebSearch normalization, date extraction, and dedupe; not yet wired into orchestration. `references/last30days-skill/scripts/lib/websearch.py:1-401`. |
| `references/last30days-skill/scripts/lib/score.py` | Scoring logic, including WebSearch penalties and date-confidence adjustments. `references/last30days-skill/scripts/lib/score.py:8-278`. |
| `references/last30days-skill/scripts/lib/schema.py` | Canonical data models and serialization for report outputs. `references/last30days-skill/scripts/lib/schema.py:8-336`. |
| `references/last30days-skill/README.md` | User-facing contract and expectations, includes requirements statement that currently conflicts with code. `references/last30days-skill/README.md:702-707`. |
| `references/last30days-skill/SKILL.md` | Skill metadata and operational instructions. `references/last30days-skill/SKILL.md:1-176`. |

**Red Flags**

- WebSearch is described as a supported source and has full schema/scoring logic, but the orchestrator never consumes WebSearch results; it only prints instructions for Claude. This creates a functional gap between implementation and stated capabilities. `references/last30days-skill/scripts/last30days.py:161-274`, `references/last30days-skill/scripts/lib/websearch.py:1-401`.
- README states “At least one key is required,” but the code explicitly supports web-only mode without keys. This is a user-facing contract mismatch. `references/last30days-skill/README.md:702-707`, `references/last30days-skill/scripts/lib/env.py:57-112`.
- Cache support for reports appears in schema/UI but is not actually used in the orchestrator, suggesting unfinished functionality. `references/last30days-skill/scripts/lib/cache.py:1-152`, `references/last30days-skill/scripts/lib/render.py:75-79`, `references/last30days-skill/scripts/last30days.py:1-521`.

**Green Flags**

- Clear, modular architecture with focused modules and a small, readable orchestrator. `references/last30days-skill/SPEC.md:11-25`, `references/last30days-skill/scripts/last30days.py:161-475`.
- Thoughtful scoring system that explicitly accounts for engagement, recency, and WebSearch penalties. `references/last30days-skill/scripts/lib/score.py:8-278`.
- Robust date handling and hard filters to enforce the 30-day window. `references/last30days-skill/scripts/lib/dates.py:7-124`, `references/last30days-skill/scripts/lib/normalize.py:10-47`.
- Extensive documentation with many concrete examples and usage scenarios. `references/last30days-skill/README.md:1-721`.
- Tests cover most core utilities and edge cases for normalization, scoring, and rendering. `references/last30days-skill/tests/test_normalize.py:1-138`, `references/last30days-skill/tests/test_score.py:1-168`, `references/last30days-skill/tests/test_render.py:1-116`.
