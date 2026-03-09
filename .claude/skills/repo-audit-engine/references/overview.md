# Repo Audit Engine — Reference Overview

## Key Concepts

- **Three-layer architecture**: Every audit covers Docs-to-Code (always), Internal Consistency (always), and Code-to-Deploy (only when deploy configuration is detected). Each layer scores independently on a 100-point scale.
- **Complementary model strengths**: OpenCode oracle (multi-provider model access) cross-references docs against all code; Codex (SWE-bench leader) finds dead code, broken imports, unused deps. They run concurrently (different providers, no rate conflict).
- **Gating issues override scores**: Certain findings (hardcoded secrets, broken imports, nonexistent deploy targets) cap the grade at C regardless of point total. Report these prominently in a "Fix First" section.
- **Cross-layer promotion**: Findings that appear in multiple layers are promoted one severity level (LOW → MEDIUM, MEDIUM → HIGH).

## Decision Criteria

### Layer Applicability Detection

| Layer | Always Run? | Detection Trigger |
|-------|-------------|------------------|
| Docs-to-Code | Yes | Every repo has documentation |
| Internal Consistency | Yes | Every repo has code |
| Code-to-Deploy | Conditional | Dockerfile, docker-compose.yml, .github/workflows/ deploy steps, Caddyfile, nginx.conf, vercel.json, netlify.toml, fly.toml, Procfile, k8s/, serverless.yml, .deploy/, render.yaml |

### Fork Allocation

| Fork | Model | Layer | Launch Timing |
|------|-------|-------|---------------|
| A | openai/gpt-5.2 via oracle agent | Docs-to-Code | Immediately |
| B | gpt-5.2-codex | Internal Consistency | Immediately (concurrent with A) |
| C | openai/gpt-5.2 via oracle agent | Code-to-Deploy | After A completes (max 2 concurrent OpenCode) |

### Gating Issues (cap grade at C)

- Build command fails or doesn't exist
- Secrets/credentials hardcoded in source
- Deploy config references files that don't exist
- Critical import paths are broken (app won't start)
- INDEX.md Documentation Map points to non-existent files (when INDEX.md exists)

## Quick Reference

### Scoring Rubrics

**Docs-to-Code (100 points)**

| Criterion | Points |
|-----------|--------|
| Build/test commands accurate | +15 |
| README project description current | +10 |
| API docs match endpoints | +15 |
| Directory structure matches docs | +10 |
| INDEX.md present and accurate | +15 |
| Commands/agents referenced exist | +15 |
| Environment setup docs current | +10 |
| Glossary terms match code usage | +10 |

**Internal Consistency (100 points)**

| Criterion | Points |
|-----------|--------|
| No dead code | +15 |
| No orphaned configs | +10 |
| All imports resolve | +20 |
| No stale .claude/ references | +15 |
| Package scripts work | +10 |
| No unused dependencies | +10 |
| Consistent naming conventions | +10 |
| No stale TODOs (>90 days) | +10 |

**Code-to-Deploy (100 points)**

| Criterion | Points |
|-----------|--------|
| Dockerfile installs all deps | +20 |
| CI builds what deploy expects | +20 |
| Env vars documented and used | +15 |
| Port/host configs consistent | +10 |
| Build artifacts match deploy | +15 |
| Health check endpoints exist | +10 |
| Secrets not hardcoded | +10 |

### Grade Mapping

| Grade | Score |
|-------|-------|
| A | 90-100 |
| B | 80-89 |
| C | 70-79 |
| D | 60-69 |
| F | < 60 |

### Cross-Reference Priority Rules

| Docs Layer Says | Internal Layer Says | Priority |
|----------------|---------------------|----------|
| "Doc claims X exists" | "X is dead code/missing" | HIGH |
| "Doc claims command Y" | "Y has broken imports" | HIGH |
| "Doc claims deploy to X" | "Target mismatch" | HIGH |
| "Doc is stale" | (no mention) | MEDIUM |
| (no mention) | "Orphaned config Z" | MEDIUM |

### INDEX.md Validation Rules

- Line count > 80 lines: flag as over-budget
- Every Documentation Map path must exist as a file
- Every Quick Facts entry must be verifiable (stack, deploy, entry point, build/test commands)
- If INDEX.md is absent and CLAUDE.md > 200 lines: deduct 15 points from docs-to-code score

### Fallback Chain

Fork timeout (5 min) → check `error_type` in `done.json` → dispatch Sonnet subagent with identical prompt
