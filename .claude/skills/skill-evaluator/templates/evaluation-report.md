# Evaluation Report Template

Opus fills this template after reading all agent reports. Variables in `{BRACES}` are replaced during synthesis.

---

# Skill Evaluation: {SKILL_NAME}

**Date:** {DATE}
**Evaluator:** Opus (synthesized from 3 parallel agents)
**Target:** `{TARGET_PATH}`
**Intended use:** {INTENDED_USE}
**Evaluation depth:** {EVALUATION_DEPTH}

## Executive Summary

{OPUS_SYNTHESIS}

> This is Opus's independent assessment — not a merge of agent summaries. Contradictions between agents have been resolved and noted below.

## At a Glance

| Dimension | Score | Agent |
|-----------|-------|-------|
| Structural Quality | {STRUCTURAL_SCORE}/5 | Codex |
| Ecosystem Fit | {ECOSYSTEM_SCORE}/5 | Gemini Pro |
| Risk Profile | {RISK_SCORE}/5 | Gemini Flash |
| **Overall** | **{OVERALL_SCORE}/5** | **Opus (weighted)** |

**Verdict:** {VERDICT}

> Possible verdicts: **Adopt** | **Extract Components** | **Adapt Patterns** | **Skip**

## What's Genuinely New

{NOVELTY_ANALYSIS}

- Key novel capabilities not available in current ecosystem
- Reference the ecosystem fit agent's novelty map

## What Gap It Fills

{GAP_ANALYSIS}

- Which unmet need this addresses
- How critical that gap is
- What we'd do without it

## Combinatorial Leverage

| Combination | New Capability | Effort | Value |
|-------------|---------------|--------|-------|
| {SKILL_NAME} + {COMPONENT_1} | {NEW_CAPABILITY_1} | {EFFORT} | {VALUE} |
| {SKILL_NAME} + {COMPONENT_2} | {NEW_CAPABILITY_2} | {EFFORT} | {VALUE} |
| {SKILL_NAME} + {COMPONENT_3} | {NEW_CAPABILITY_3} | {EFFORT} | {VALUE} |

## Risk Profile

### Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| {RISK_1} | {SEVERITY} | {MITIGATION} |
| {RISK_2} | {SEVERITY} | {MITIGATION} |

### Maintenance Health

| Signal | Status |
|--------|--------|
| Last activity | {LAST_ACTIVITY} |
| Contributors | {CONTRIBUTOR_COUNT} |
| Dependencies | {DEP_COUNT} direct, ~{TRANSITIVE_DEP_COUNT} transitive |

## Adoption Strategies

### Strategy A: Adopt As-Is

{STRATEGY_A_DESCRIPTION}

**Steps:**
1. {STEP_1}
2. {STEP_2}
3. {STEP_3}

| Effort | Risk | Value |
|--------|------|-------|
| {EFFORT} | {RISK} | {VALUE} |

### Strategy B: Extract Components

{STRATEGY_B_DESCRIPTION}

**Extract:**
- `{FILE_1}` -> `{DESTINATION_1}`
- `{FILE_2}` -> `{DESTINATION_2}`

| Effort | Risk | Value |
|--------|------|-------|
| {EFFORT} | {RISK} | {VALUE} |

### Strategy C: Adapt Patterns

{STRATEGY_C_DESCRIPTION}

**Patterns:**
- {PATTERN_1}: {APPLICATION}
- {PATTERN_2}: {APPLICATION}

| Effort | Risk | Value |
|--------|------|-------|
| {EFFORT} | {RISK} | {VALUE} |

## Recommended Strategy

**{RECOMMENDED_STRATEGY}**

{RECOMMENDATION_RATIONALE}

## Integration Checklist

If adopting (Strategy A or B):

- [ ] Add to `MANIFEST.json` (deployment: global, status: beta)
- [ ] Update `REGISTRY.md` (category, quick lookup, relationships)
- [ ] Update `install-global.sh` (if global deployment)
- [ ] Run `python3 scripts/validate-manifest.py`
- [ ] Run `python3 scripts/validate-docs.py`
- [ ] Update component counts in REGISTRY

## Agent Reports

Raw agent reports for deep-dive:

- **Structural Quality:** [`docs/evaluations/{SKILL_NAME}-structural.md`](docs/evaluations/{SKILL_NAME}-structural.md)
- **Ecosystem Fit:** [`docs/evaluations/{SKILL_NAME}-ecosystem.md`](docs/evaluations/{SKILL_NAME}-ecosystem.md)
- **Risk & Adoption:** [`docs/evaluations/{SKILL_NAME}-risk.md`](docs/evaluations/{SKILL_NAME}-risk.md)

## Contradictions & Resolutions

| Agent A Says | Agent B Says | Resolution |
|-------------|-------------|------------|
| {CONTRADICTION_1_A} | {CONTRADICTION_1_B} | {RESOLUTION_1} |

> If no contradictions were found, note that all agents aligned.
