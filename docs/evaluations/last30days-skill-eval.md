# Skill Evaluation: last30days-skill

**Date:** 2026-02-04
**Evaluator:** Opus (synthesized from Codex structural + Gemini ecosystem + Opus risk analysis)
**Target:** `references/last30days-skill/`
**Intended use:** Assess for potential adoption into template library
**Evaluation depth:** Full (3 dimensions; risk analysis performed by Opus due to Gemini rate limits)

## Executive Summary

last30days-skill is a well-architected Python skill that fills a genuinely novel gap in our ecosystem: real-time social trend analysis from Reddit and X. It's the only component that can answer "what are people saying about X right now?" — something our existing researchers (library-researcher, technical-researcher) explicitly don't do. Critically, a [tutorial transcript](references/The_Claude_Code_Skill_My_Smartest_Friends_Use_coding_agent.md) reveals this skill is designed as the **first stage of a pipeline** with compound-engineering: `research → plan → build`. Its primary value is "prompt priming" — enriching the agent's context with fresh trend data before planning and implementation. **Recommended strategy: Adopt As-Is** — wrap as a `/last30days` command and build a workflow chain connecting it to our planning/orchestration pipeline.

## At a Glance

| Dimension | Score | Source |
|-----------|-------|--------|
| Structural Quality | 3.65/5 | Codex |
| Ecosystem Fit | 4.25/5 | Gemini Pro |
| Risk Profile | 3.50/5 | Opus |
| **Overall** | **3.80/5** | **Weighted average** |

**Verdict:** Adopt As-Is

## What's Genuinely New

The ecosystem fit analysis scored Novelty at 5/5 — the highest possible. This skill introduces capabilities entirely absent from our library:

- **Social listening** (Reddit/X) vs our existing doc-focused researchers
- **Recency-weighted scoring** — strictly enforces a 30-day window with confidence penalties for older content
- **Multi-source normalization** — unified schema across Reddit, X, and web results
- **Prompt pack generation** — synthesizes actionable prompts from community discussions

None of our 7 global skills, 13 agents, or 17 commands touch this space.

## What Gap It Fills

**Primary gap:** "What are developers actually experiencing with X this week?"

Our `library-researcher` finds official docs. Our `technical-researcher` produces formal analysis. Neither captures the informal, fast-moving community knowledge that's critical for:
- Zero-day bug discovery (community chatter precedes docs by days/weeks)
- Prompt engineering best practices (rapidly evolving, rarely documented)
- Sentiment/adoption signals ("is this framework dying?")

**Gap importance:** Medium-High. Increasingly critical as AI tooling moves faster than documentation.

## The Pipeline Pattern (Critical Context)

A [tutorial by Matt Van Horn](references/The_Claude_Code_Skill_My_Smartest_Friends_Use_coding_agent.md) reveals that last30days-skill and compound-engineering are designed to work as a **workflow pipeline**, not as independent tools:

```
last30days "topic" → compound-engineering /workflows plan → build
     (research)              (architecture)            (implementation)
```

This is called the **"Kung Fu Hack"** — prime the agent with fresh trend data, then use that enriched context to produce dramatically better plans and code. The key insight is that even if you don't read the research results yourself, the agent uses that context to improve all subsequent output.

**What this means for our ecosystem:**

We already have the building blocks for this pipeline:
- **Research phase**: last30days (novel) or library-researcher/technical-researcher (existing)
- **Planning phase**: `/orchestrate`, PRP commands, or multi-model-orchestration
- **Build phase**: Codex fork via fork-terminal

The missing piece is **automatic context handoff** — where research output flows seamlessly into planning without manual copying. compound-engineering's `workflows plan` command does this natively. We should consider building a similar workflow chain: `/research → /plan → /build` where each step inherits the prior context.

## Combinatorial Leverage

| Combination | New Capability | Effort | Value |
|-------------|---------------|--------|-------|
| **last30days + compound-engineering plan** | **"Prompt Priming Pipeline" — research → plan → build with automatic context flow** | **Medium** | **Very High** |
| last30days + library-researcher | "Reality Check" — docs vs what's actually breaking | Low | High |
| last30days + skill-evaluator | Find trending skills, then evaluate them | Low | High |
| last30days + code-reviewer | Trend-aware review ("this pattern was deprecated last week") | Medium | Medium |
| last30days + new-developer workflow | Current best practices beyond stale READMEs | Low | Medium |

## Risk Profile

### Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| External API dependency (OpenAI, xAI) | Medium | Web-only fallback mode exists; but core value requires API keys |
| Incomplete features (WebSearch, cache) | Low | Functional without them; these are additive |
| No dependency declaration/lockfile | Low | Pure Python stdlib + API calls; no pip packages |
| Single maintainer | Medium | 20+ commits show active development; monitor for staleness |

### Maintenance Health

| Signal | Status |
|--------|--------|
| Last activity | Active (20+ recent commits with features and fixes) |
| Contributors | Appears single-maintainer |
| Dependencies | Zero pip deps (stdlib only + external API calls) |
| Test coverage | 8 test files covering core modules; gaps in orchestrator and WebSearch |

## Adoption Strategies

### Strategy A: Adopt As-Is

Install as a global skill alongside existing components.

**Steps:**
1. Copy `references/last30days-skill/` to `.claude/skills/last30days/`
2. Add to MANIFEST.json (deployment: global, status: beta)
3. Update REGISTRY.md, USER_GUIDE.md
4. Create `/last30days` command wrapper
5. Run install-global.sh

| Effort | Risk | Value |
|--------|------|-------|
| Low | Medium (incomplete features may confuse users) | High |

### Strategy B: Extract Components

Cherry-pick the scoring/normalization engine and adapt for our ecosystem.

**Extract:**
- `scripts/lib/score.py` — Recency-weighted scoring with engagement and confidence signals
- `scripts/lib/normalize.py` — Multi-source normalization to unified schema
- `scripts/lib/schema.py` — Canonical data models
- `scripts/lib/dates.py` — Date handling and 30-day window enforcement
- `SKILL.md` — As a reference for the skill pattern (frontmatter, tools declaration)

**Adapt:**
- Integrate scoring patterns into a new `trend-researcher` agent
- Use the normalization approach for any future multi-source agents

| Effort | Risk | Value |
|--------|------|-------|
| Medium | Low | High |

### Strategy C: Adapt Patterns

Learn from the architecture without importing code.

**Patterns to adopt:**
- **Multi-source normalization**: Unified schema across heterogeneous APIs — apply to our own multi-agent outputs
- **Recency-weighted scoring**: Confidence penalties for date uncertainty — useful for any time-sensitive research
- **Web-only fallback mode**: Graceful degradation when API keys unavailable — apply to our orchestration skills
- **Parallel source execution**: Reddit and X searches run in parallel — matches our fork-terminal patterns

| Effort | Risk | Value |
|--------|------|-------|
| Low | None | Medium |

## Recommended Strategy

**Strategy A: Adopt As-Is** (revised from Extract, based on pipeline context)

The tutorial transcript reveals this skill's primary value isn't just its scoring engine — it's the **prompt priming pipeline** where research context flows into planning and implementation. Extracting individual modules would lose this workflow value. The skill is designed to be invoked as a unit (`last 30 days [topic]`) and its output primes the entire session context.

**Revised rationale:** Adopt the skill as-is, wrap it with a `/last30days` command, and build a workflow chain that connects it to our existing planning/orchestration commands. The incomplete features (WebSearch, cache) are additive and don't block the core use case. Monitor upstream for completion.

**Follow-up:** Study compound-engineering's `workflows plan` command to build the context handoff step that bridges research → planning in our ecosystem.

## Integration Checklist

If adopting (Strategy A or B):

- [ ] Add to `MANIFEST.json` (deployment: global, status: beta)
- [ ] Update `REGISTRY.md` (Research category, Quick Lookup, Relationships)
- [ ] Update `install-global.sh`
- [ ] Run `python3 scripts/validate-manifest.py`
- [ ] Run `python3 scripts/validate-docs.py`
- [ ] Update component counts in REGISTRY

## Agent Reports

- **Structural Quality:** [`docs/evaluations/last30days-skill-structural.md`](last30days-skill-structural.md) (Codex)
- **Ecosystem Fit:** [`docs/evaluations/last30days-skill-ecosystem.md`](last30days-skill-ecosystem.md) (Gemini Pro)
- **Risk & Adoption:** Performed by Opus inline (Gemini Flash unavailable — 429 rate limit)

## Contradictions & Resolutions

| Codex Says | Gemini Pro Says | Resolution |
|-----------|----------------|------------|
| WebSearch "not wired into orchestration" (red flag) | "High combinatorial potential" (5/5 leverage) | Both correct — the architecture is sound but the integration is incomplete. This supports Extract over Adopt. |
| Testing scored 3/5 (gaps in orchestrator) | High novelty implies high value despite gaps | Testing gaps are real but manageable — the tested modules (scoring, normalization) are exactly what we'd extract. |

> Gemini Flash risk agent was unavailable due to API rate limits. Risk analysis was performed by Opus using the same framework.
