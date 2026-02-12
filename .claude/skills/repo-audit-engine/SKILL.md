---
name: repo-audit-engine
description: Scoring rubrics, alignment criteria, layer detection, and prompt templates for multi-layer repo auditing via forked Gemini + Codex instances
version: 1.0.0
category: orchestration
user-invocable: false
related:
  commands: [workflow/repo-audit]
  skills: [repo-optimize-engine, fork-terminal, multi-model-orchestration]
---

# Repo Audit Engine

Shared logic for the `/repo-audit` command. This skill defines scoring rubrics, layer detection, cross-referencing rules, and fork allocation for comprehensive repo alignment audits.

## Fork Allocation (Complementary Strengths)

| Fork | Model | Layer | Rationale |
|------|-------|-------|-----------|
| A | Gemini (`gemini-2.5-flash`) | Docs-to-Code | 1M context reads ALL docs + ALL code, cross-references every claim |
| B | Codex (`gpt-5.2-codex`) | Internal Consistency | SWE-bench leader — best at finding dead code, broken imports, unused deps |
| C | Gemini (`gemini-2.5-flash`) | Code-to-Deploy | Broad context to cross-reference deploy configs with codebase (conditional) |

**Concurrency**: Launch A + B concurrently (different providers, no rate conflict). Launch C after A completes (max 2 concurrent Gemini). Stagger if needed.

**Fallback chain**: Fork timeout (5 min) -> check error_type in done.json -> dispatch Sonnet subagent with identical prompt.

## Run-Directory Contract

All fork output goes to an isolated run directory:

```
/tmp/repo-audit/{REPO_NAME}/{RUN_ID}/
  fork-a.response.json    # Gemini docs-to-code
  fork-a.done.json         # Completion status
  fork-b.response.json    # Codex internal consistency
  fork-b.done.json
  fork-c.response.json    # Gemini code-to-deploy (if applicable)
  fork-c.done.json
```

`RUN_ID` = `YYYYMMDD_HHMMSS` timestamp.

## Layer Applicability Detection

### Docs-to-Code
Always applicable. Every repo has some documentation.

### Internal Consistency
Always applicable. Every repo has code to check for hygiene.

### Code-to-Deploy
Only applicable if deploy configuration is detected. Check for any of:
- `Dockerfile` or `docker-compose.yml`
- `.github/workflows/` with deploy steps
- `Caddyfile` or `nginx.conf`
- `vercel.json`, `netlify.toml`, `fly.toml`
- `Procfile`
- `k8s/` or `kubernetes/` directory
- `serverless.yml` or `serverless.ts`
- `.deploy/` directory
- `render.yaml`

## Alignment Scoring Rubrics

### Docs-to-Code (100 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| Build/test commands accurate | +15 | Commands in CLAUDE.md/README run successfully |
| README project description current | +10 | Matches actual functionality |
| API docs match endpoints | +15 | Every documented endpoint exists in code |
| Directory structure matches docs | +10 | Documented paths exist |
| INDEX.md present and accurate | +15 | Quick Facts, Doc Map, Critical Paths verified |
| Commands/agents referenced exist | +15 | Every named .claude/ component is findable |
| Environment setup docs current | +10 | .env.example matches actual usage |
| Glossary terms match code usage | +10 | Terminology consistent across docs and code |

### Internal Consistency (100 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| No dead code | +15 | No unreachable exported symbols |
| No orphaned configs | +10 | Config files match installed tools |
| All imports resolve | +20 | Every import/require points to existing module |
| No stale .claude/ references | +15 | Commands, skills, agents reference existing files |
| Package scripts work | +10 | All scripts in package.json/Makefile are valid |
| No unused dependencies | +10 | Every dep is imported somewhere |
| Consistent naming conventions | +10 | File and variable naming is uniform |
| No stale TODOs | +10 | No TODO/FIXME in runtime paths older than 90 days |

### Code-to-Deploy (100 points)

| Criterion | Points | Check |
|-----------|--------|-------|
| Dockerfile installs all deps | +20 | Build stage covers all required packages |
| CI builds what deploy expects | +20 | Build output matches deploy target |
| Env vars documented and used | +15 | Every referenced env var is in .env.example |
| Port/host configs consistent | +10 | App ports match Docker EXPOSE and proxy config |
| Build artifacts match deploy | +15 | Output dir matches what deploy copies/serves |
| Health check endpoints exist | +10 | If deploy expects health check, endpoint exists |
| Secrets not hardcoded | +10 | No API keys, passwords, tokens in source |

## Grade Mapping

| Grade | Score Range |
|-------|-----------|
| A | 90-100 |
| B | 80-89 |
| C | 70-79 |
| D | 60-69 |
| F | < 60 |

## Gating Issues

Certain findings are **gating issues** that cap the overall grade at C regardless of point score:

- Build command fails or doesn't exist
- Secrets/credentials hardcoded in source
- Deploy config references files that don't exist
- Critical import paths are broken (app won't start)
- INDEX.md Documentation Map points to non-existent files (if INDEX.md exists)

One gating issue = max grade C. Report gating issues prominently in the "Fix First" section.

## INDEX.md Validation Criteria

### If `.claude/INDEX.md` exists:
1. Line count check: >80 lines = flagged as over-budget
2. **Purpose** field present and non-empty
3. **"If you only read one file today"** path exists
4. Every Quick Facts entry is verifiable:
   - Stack: matches detected languages/frameworks
   - Deploy: matches detected deploy config
   - Entry point: file exists
   - Build/Test: commands exist in package.json/Makefile/etc.
   - Package mgr: matches detected package manager
5. Every Documentation Map path exists as a file
6. Every Critical Path hop references existing directories/files
7. Anti-Patterns are not contradicted by actual code patterns
8. Known Drift entries have dates

### If `.claude/INDEX.md` does NOT exist:
- Flag as "INDEX.md missing" in findings
- Recommend creation with link to template
- Only deduct 15 points from docs-to-code score if CLAUDE.md > 200 lines
- If CLAUDE.md <= 200 lines, warn but don't penalize (repo may not need INDEX.md yet)

## Cross-Reference Rules

When synthesizing findings from multiple forks, apply these priority rules:

| Docs Layer Says | Internal Layer Says | Priority |
|----------------|-------------------|----------|
| "Doc claims X exists" | "X is dead code/missing" | **HIGH** — doc references broken thing |
| "Doc claims command Y" | "Y has broken imports" | **HIGH** — documented feature is broken |
| "Doc is stale" | (no mention) | **MEDIUM** — accuracy issue |
| (no mention) | "Orphaned config Z" | **MEDIUM** — hygiene issue |
| "Doc claims deploy to X" | Deploy says "target mismatch" | **HIGH** — deploy drift |

Overlapping findings across layers get **promoted one severity level** (LOW -> MEDIUM, MEDIUM -> HIGH).

## Prompt Template Variables

All prompt templates accept these variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `{REPO_PATH}` | Absolute path to target repository | `/home/user/projects/myapp` |
| `{REPO_NAME}` | Directory basename | `myapp` |
| `{RUN_DIR}` | Run output directory | `/tmp/repo-audit/myapp/20260211_143022` |
| `{KNOWN_DRIFT}` | Contents of Known Drift section from INDEX.md (if present) | `- [2026-01-15] API v1 docs kept for migration reference` |

## Output Schema

All forks must emit JSON matching the schema at `schema/audit-layer-output.json`. This ensures Opus can synthesize uniformly regardless of which model produced the output.

## Dry-Run Mode

When `--dry-run` is passed as the layer filter, the `/repo-audit` command:
1. Detects applicable layers (same logic as normal)
2. Fills prompt templates with variables (same logic)
3. Prints the planned forks, detected layers, and filled prompts
4. Does NOT launch any LLM forks
5. Reports estimated quota usage

Useful for verifying configuration before spending API quota.
