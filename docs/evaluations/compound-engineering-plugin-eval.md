# Skill Evaluation: compound-engineering-plugin

**Date:** 2026-02-04
**Evaluator:** Opus (synthesized from Codex structural + Opus ecosystem/risk analysis)
**Target:** `references/compound-engineering-plugin/`
**Intended use:** Assess for potential adoption into template library
**Evaluation depth:** Full (3 dimensions; ecosystem + risk performed by Opus due to Gemini rate limits)

## Executive Summary

compound-engineering-plugin is a substantial project (170+ files, 37K+ lines) that serves two distinct purposes: (1) a TypeScript CLI tool that converts Claude Code plugins to Codex/OpenCode formats, and (2) a plugin marketplace containing the `compound-engineering` plugin with 25+ agents, 20+ commands, and 10+ skills. A [tutorial transcript](references/The_Claude_Code_Skill_My_Smartest_Friends_Use_coding_agent.md) reveals its **key strategic value**: the `workflows plan` command serves as the bridge in a `research → plan → build` pipeline with last30days-skill. The `brainstorm → plan → work → review` command chain is the highest-value extractable piece — it defines a 4-step development cycle with automatic context handoff between phases. **Recommended strategy: Extract Components** — pull the workflow chain and agent-native-architecture references, wire them into our existing orchestration pipeline.

## At a Glance

| Dimension | Score | Source |
|-----------|-------|--------|
| Structural Quality | 3.65/5 | Codex |
| Ecosystem Fit | 3.00/5 | Opus |
| Risk Profile | 3.25/5 | Opus |
| **Overall** | **3.30/5** | **Weighted average** |

**Verdict:** Extract Components

## What's Genuinely New

Several capabilities are novel relative to our ecosystem:

| Capability | Novel? | Notes |
|------------|--------|-------|
| Plugin-to-Codex/OpenCode converter | Yes | We have no cross-platform conversion tool |
| `create-agent-skills` skill | Yes | Structured skill creation with templates, workflows, validation — more prescriptive than our writing-skills |
| `agent-native-architecture` skill | Yes | Comprehensive reference on agent-first design patterns (14 reference files) |
| `brainstorming` skill | Partial | We have `superpowers:brainstorming` — compare approaches |
| `compound-docs` skill | Yes | YAML-based documentation schema with templates |
| Persona-based reviewers (DHH, Kieran) | Yes | Opinionated code review from specific engineering philosophies |
| `gemini-imagegen` skill | Yes | Image generation via Gemini — we have nothing in this space |
| Plugin marketplace system | Yes | We use MANIFEST.json + install-global.sh instead |

## What Gap It Fills

**Primary gap:** Cross-platform plugin distribution and structured skill creation workflows.

Our template library distributes via symlinks and manual copying. compound-engineering-plugin has:
- A proper CLI (`npx compound-engineering convert/install/list`)
- Marketplace metadata (`plugin.json`, `marketplace.json`)
- Automated conversion to Codex and OpenCode formats
- CI/CD pipeline and versioned releases

**However:** This gap may not be critical for us. Our symlinking approach works well for a single-developer template library. The distribution problem compound-engineering solves is for multi-developer plugin marketplaces.

**Secondary gap:** Structured skill creation. Their `create-agent-skills` skill has 9 workflows, 13 reference docs, and 2 templates — significantly more structured than our current approach.

## The Pipeline Pattern (Critical Context)

A [tutorial by Matt Van Horn](references/The_Claude_Code_Skill_My_Smartest_Friends_Use_coding_agent.md) reveals that compound-engineering and last30days-skill are designed to work as a **workflow pipeline**:

```
last30days "topic" → compound-engineering /workflows plan → build
     (research)              (architecture)            (implementation)
```

The compound-engineering plugin's `workflows plan` command is the **bridge** in this chain — it takes research context (from last30days or any source) and generates architecture/implementation plans. The `brainstorm → plan → work → review` cycle isn't just a neat pattern; it's the orchestration layer that makes research actionable.

**What this means for our ecosystem:**

The `workflows/` commands (`brainstorm.md`, `plan.md`, `work.md`, `review.md`) are the most strategically valuable part of this plugin — more so than the agents or skills individually. They define a **4-step development cycle** with automatic context handoff between phases. Our current PRP and orchestration commands are similar in concept but lack this tight integration.

**Key insight:** The compound workflow chain is essentially what our `feature-development.md` workflow aspires to be, but with explicit command entry points at each phase. Consider extracting the workflow chain structure rather than just adapting the pattern conceptually.

## Combinatorial Leverage

| Combination | New Capability | Effort | Value |
|-------------|---------------|--------|-------|
| **compound workflow chain + last30days** | **"Prompt Priming Pipeline" — research → plan → build with automatic context flow** | **Medium** | **Very High** |
| **workflows/plan + our /orchestrate** | **Structured planning phase before fork-to-Codex implementation** | **Medium** | **High** |
| create-agent-skills patterns + our writing-skills | Better skill creation workflow with validation | Medium | High |
| agent-native-architecture refs + our agents | Deeper agent design patterns | Low | High |
| converter CLI + our template library | Distribute our components to Codex/OpenCode users | High | Medium |
| compound-docs schema + our MANIFEST | Structured documentation generation | Medium | Medium |

## Risk Profile

### Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Size/complexity (170+ files, 37K lines) | High | Don't adopt wholesale — extract patterns |
| Version inconsistency (CLI 0.1.1 vs plugin 2.28.0) | Medium | Metadata reliability concern for full adoption |
| Documentation count mismatches across files | Medium | Multiple places claim different component counts |
| Bun dependency (bun.lock, not npm) | Low | Only affects CLI; agents/skills are plain markdown |
| Different architecture (plugin system vs template library) | High | Fundamental mismatch with our approach |

### Maintenance Health

| Signal | Status |
|--------|--------|
| Last activity | Active (recent PRs, versioned releases) |
| Contributors | Multiple (PRs from different authors) |
| Dependencies | Bun runtime, TypeScript — only for CLI tool |
| CI/CD | GitHub Actions for tests and docs deployment |
| Release cadence | Regular (v2.27.0, v2.28.0 recent) |

## Adoption Strategies

### Strategy A: Adopt As-Is

Install the entire compound-engineering plugin alongside our components.

**Steps:**
1. Add as a Claude Code plugin via marketplace
2. Resolve naming conflicts (both have `agent-browser`)
3. Reconcile overlapping agents (code-reviewer vs their review agents)
4. Document which components come from where

| Effort | Risk | Value |
|--------|------|-------|
| High | High (naming conflicts, philosophy mismatch, maintenance burden) | Medium |

**When to choose:** If you want everything they offer and are willing to maintain two parallel systems.

### Strategy B: Extract Components

Cherry-pick specific valuable agents, skills, and patterns.

**Extract:**
- `plugins/compound-engineering/skills/create-agent-skills/` — Skill creation framework with 9 workflows
- `plugins/compound-engineering/skills/agent-native-architecture/` — 14 reference docs on agent design
- `plugins/compound-engineering/skills/brainstorming/SKILL.md` — Compare with our brainstorming skill
- `plugins/compound-engineering/agents/research/` — 5 research agents (learnings-researcher is novel)
- `plugins/compound-engineering/commands/workflows/` — brainstorm/plan/review/work chain

**Place in:**
- Agent patterns -> adapt into our `.claude/agents/` format
- Skill patterns -> merge insights into our existing skills
- Reference docs -> consider adding to a `references/patterns/` directory

| Effort | Risk | Value |
|--------|------|-------|
| Medium | Medium (adaptation needed to match our conventions) | High |

**When to choose:** If specific components fill gaps you've identified in your workflow.

### Strategy C: Adapt Patterns

Learn from the approach without importing code.

**Patterns to adopt:**
- **Persona-based reviewers:** Create opinionated code reviewers with specific engineering philosophies (e.g., a "minimalist" reviewer, a "security-first" reviewer) — our code-reviewer is generic
- **Skill creation workflows:** Their 9-step skill creation process (create, add-reference, add-template, add-script, add-workflow, verify, audit, upgrade-to-router, get-guidance) is more structured than ours
- **Compound workflow chain:** brainstorm -> plan -> work -> review is a clean 4-step cycle we could adopt
- **Agent categorization:** Their research/review/design/workflow/docs categories are more granular than our flat agents folder
- **Plugin converter concept:** If we ever want to distribute to Codex/OpenCode users, this shows the path

| Effort | Risk | Value |
|--------|------|-------|
| Low | None | High |

**When to choose:** Default recommendation. Maximum learning, zero maintenance burden.

## Recommended Strategy

**Strategy B: Extract Components** (revised from Adapt Patterns, based on pipeline context)

The tutorial transcript reveals that compound-engineering's highest value is its **workflow chain** (`brainstorm → plan → work → review`), which serves as the orchestration layer in a research-to-implementation pipeline with last30days-skill. This is more than a pattern to study — the workflow commands themselves are worth extracting.

**Revised rationale:** Extract the `workflows/` command chain (`brainstorm.md`, `plan.md`, `work.md`, `review.md`) and adapt them to our command format. Also extract `agent-native-architecture` reference docs as a learning resource. Skip the CLI converter, marketplace system, and persona-based reviewers (interesting patterns but not pipeline-critical).

**Priority extractions:**
1. `plugins/compound-engineering/commands/workflows/` — The 4-step development cycle
2. `plugins/compound-engineering/skills/agent-native-architecture/` — 14 reference docs on agent design
3. `plugins/compound-engineering/skills/create-agent-skills/` — Skill creation framework

**Follow-up:** Wire the extracted workflow chain to connect with an adopted last30days-skill, building the full `research → plan → build → review` pipeline in our ecosystem.

## Integration Checklist

If extracting specific components (Strategy B):

- [ ] Adapt agent frontmatter to match our convention
- [ ] Resolve naming conflicts (agent-browser exists in both)
- [ ] Add to `MANIFEST.json`
- [ ] Update `REGISTRY.md`
- [ ] Run `python3 scripts/validate-manifest.py`
- [ ] Run `python3 scripts/validate-docs.py`

## Agent Reports

- **Structural Quality:** [`docs/evaluations/compound-engineering-plugin-structural.md`](compound-engineering-plugin-structural.md) (Codex)
- **Ecosystem Fit:** Performed by Opus inline (Gemini Pro/Flash unavailable — 429 rate limit)
- **Risk & Adoption:** Performed by Opus inline (Gemini Flash unavailable — 429 rate limit)

## Contradictions & Resolutions

| Observation A | Observation B | Resolution |
|--------------|--------------|------------|
| Strong code architecture (4/5 structural) | Fundamental architecture mismatch with our library | Quality of code != fit for our use case. Well-built for its purpose, but that purpose differs from ours. |
| Extensive agent collection (25+ agents) | We already have 13 agents | Quantity isn't the value — their categorization (research/review/design/workflow) and persona patterns are what's novel. |
| Documentation inconsistencies (red flag) | Active maintenance with CI/CD | Growing project with versioning challenges — common in fast-moving repos, not a blocker for pattern adoption. |

> Gemini Pro and Flash agents were unavailable due to API rate limits. Ecosystem and risk analyses were performed by Opus using the same evaluation frameworks.
