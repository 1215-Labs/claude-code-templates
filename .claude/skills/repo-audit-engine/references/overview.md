# Repo Audit Engine — Reference Overview

Supplementary reference for the `repo-audit-engine` skill. Read SKILL.md for full instructions.

## What This Engine Audits

The engine checks three alignment layers:

| Layer | Question | Always Run? |
|-------|----------|-------------|
| Docs-to-Code | Do documented commands, endpoints, and paths actually exist in code? | Yes |
| Internal Consistency | Are imports, deps, and .claude/ references internally valid? | Yes |
| Code-to-Deploy | Do app ports, env vars, and build outputs match deploy config? | Only if deploy config detected |

## Fork Assignment Logic

| Fork | Model | Layer | Why This Model |
|------|-------|-------|----------------|
| A | OpenCode | Docs-to-Code | 1M context reads all docs + all code simultaneously for cross-referencing |
| B | Codex | Internal Consistency | SWE-bench leader — best at dead code, broken imports, unused deps |
| C | OpenCode | Code-to-Deploy | Broad context cross-references deploy configs with codebase |

Concurrency rule: Launch A + B together (different providers, no rate conflict). Launch C after A completes to stay within the 2-concurrent-OpenCode limit.

## Deploy Config Detection Checklist

Run Code-to-Deploy layer only when one or more of these exist:

- `Dockerfile` or `docker-compose.yml`
- `.github/workflows/` with deploy steps
- `Caddyfile`, `nginx.conf`
- `vercel.json`, `netlify.toml`, `fly.toml`
- `Procfile`, `render.yaml`
- `k8s/` or `kubernetes/` directory
- `serverless.yml` or `serverless.ts`
- `.deploy/` directory

## Scoring Quick Reference

Each layer is scored 0-100. Final grade averages applicable layers.

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent alignment |
| B | 80-89 | Minor gaps only |
| C | 70-79 | Notable gaps; also the cap grade for any gating issue |
| D | 60-69 | Significant issues |
| F | <60 | Fundamental misalignment |

## Gating Issues (Cap Grade at C)

These findings override the numeric score — even a 95-point repo gets C if any gating issue exists:

1. Build command fails or does not exist
2. Secrets or credentials hardcoded in source
3. Deploy config references files that do not exist
4. Critical import paths are broken (app will not start)
5. INDEX.md Documentation Map points to non-existent files (if INDEX.md exists)

Always report gating issues in a "Fix First" section at the top of the report.

## Cross-Reference Priority Rules

When the same issue appears in multiple fork outputs, escalate severity:

| Docs Layer | Internal Layer | Combined Priority |
|-----------|----------------|-------------------|
| "Doc claims X exists" | "X is missing or dead code" | HIGH — documented feature is broken |
| "Doc claims command Y" | "Y has broken imports" | HIGH — documented feature is broken |
| "Doc is stale" | (no mention) | MEDIUM |
| (no mention) | "Orphaned config Z" | MEDIUM |
| "Doc claims deploy to X" | Deploy says "target mismatch" | HIGH — deploy drift |

Findings that overlap between two layers are promoted one severity level.

## INDEX.md Validation Rules

If `.claude/INDEX.md` exists, Docs-to-Code fork must verify:
- File is under 80 lines (flag if over-budget)
- `Purpose` field is present and non-empty
- "If you only read one file today" path exists on disk
- Every Quick Facts entry is verifiable (stack, deploy, entry point, build/test, package manager)
- Every Documentation Map path exists as a real file
- Every Critical Path hop references existing directories/files
- Known Drift entries have dates

If `.claude/INDEX.md` does NOT exist:
- Flag as "INDEX.md missing" in findings
- Deduct 15 points from docs-to-code only if `CLAUDE.md` is over 200 lines
- If `CLAUDE.md` is 200 lines or shorter, warn but do not penalize

## Fallback Chain

```
Fork timeout (5 min) → check error_type in done.json
├── QUOTA / CAPACITY → dispatch Sonnet subagent via Task tool with identical prompt
└── Other error      → check output log tail, then dispatch Sonnet subagent
```

## Run Directory Contract

All audit output goes to:
```
/tmp/repo-audit/{REPO_NAME}/{YYYYMMDD_HHMMSS}/
  fork-a.response.json
  fork-a.done.json
  fork-b.response.json
  fork-b.done.json
  fork-c.response.json   (if applicable)
  fork-c.done.json       (if applicable)
```

All forks emit JSON matching `schema/audit-layer-output.json` for uniform synthesis.
