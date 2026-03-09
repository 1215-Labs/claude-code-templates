# Repo Audit Engine — Example Walkthrough

## Scenario

A developer runs a repo audit on a mid-sized Node.js API project called `cbass`. The project has a CLAUDE.md, README, some `.claude/` components, and a Dockerfile. They want to know how well the documentation matches the actual code and whether the deployment configuration is consistent.

## Trigger

> User: `/repo-audit "/home/user/projects/cbass"`

## Step-by-Step

### Step 1: Layer Detection

The audit engine inspects the target repo for deploy configuration. It finds:
- `Dockerfile` — present
- `.github/workflows/deploy.yml` — present

Code-to-Deploy layer is applicable. All three layers will run.

### Step 2: Fork Allocation

The engine sets up an isolated run directory:
```
/tmp/repo-audit/cbass/20260305_143022/
```

Two forks launch concurrently (different providers, no rate conflict):

- **Fork A** — OpenCode oracle (`openai/gpt-5.2 via oracle agent`): Docs-to-Code layer
  - Reads ALL docs (README, CLAUDE.md, .claude/INDEX.md) and ALL code via OpenCode's multi-provider model access
  - Cross-references every claim: "Does CLAUDE.md say `npm run dev` works? Does package.json have that script?"

- **Fork B** — Codex (`gpt-5.2-codex`): Internal Consistency layer
  - Scans for dead exports, broken imports, stale .claude/ references, unused dependencies

Fork C (OpenCode, Code-to-Deploy) is queued to launch after Fork A completes (max 2 concurrent OpenCode).

### Step 3: Fork A Completes — Docs-to-Code Results

After ~4 minutes, Fork A writes `fork-a.response.json`. Key findings:

| Criterion | Score | Finding |
|-----------|-------|---------|
| Build/test commands accurate | 15/15 | `npm run dev` and `npm test` both verified |
| README project description | 8/10 | Minor: README mentions "v2 API" but code is v3 |
| API docs match endpoints | 10/15 | 3 endpoints documented but not in code (deleted) |
| Directory structure matches docs | 10/10 | All documented paths exist |
| INDEX.md present and accurate | 12/15 | INDEX.md exists; 1 Critical Path references missing dir |
| Commands/agents referenced exist | 15/15 | All .claude/ components verified present |
| Environment setup docs current | 7/10 | .env.example missing `REDIS_URL` used in code |
| Glossary consistency | 10/10 | Terminology consistent |

**Docs-to-Code raw score: 87/100 → Grade B**

### Step 4: Fork B Completes — Internal Consistency Results

Fork B writes `fork-b.response.json`:

| Criterion | Score | Finding |
|-----------|-------|---------|
| No dead code | 10/15 | `src/utils/legacy-auth.ts` — exported but never imported |
| No orphaned configs | 10/10 | All config files match installed tools |
| All imports resolve | 20/20 | Every import verified |
| No stale .claude/ references | 15/15 | All verified |
| Package scripts work | 10/10 | All scripts valid |
| No unused dependencies | 8/10 | `lodash` installed but only used in the dead code file |
| Consistent naming conventions | 10/10 | Uniform |
| No stale TODOs | 5/10 | 3 TODOs older than 90 days in src/services/ |

**Internal Consistency raw score: 88/100 → Grade B**

### Step 5: Fork C Launches — Code-to-Deploy

Fork C launches after Fork A completes. Results after ~3 minutes:

| Criterion | Score | Finding |
|-----------|-------|---------|
| Dockerfile installs all deps | 15/20 | Missing `redis-cli` in build stage |
| CI builds what deploy expects | 20/20 | Build output matches |
| Env vars documented and used | 5/15 | `REDIS_URL` not in .env.example (matches Fork A finding) |
| Port/host configs consistent | 10/10 | Port 3000 consistent throughout |
| Build artifacts match deploy | 15/15 | Output dir matches |
| Health check endpoints exist | 10/10 | /health endpoint verified |
| Secrets not hardcoded | 10/10 | No hardcoded secrets |

**Code-to-Deploy raw score: 85/100 → Grade B**

### Step 6: Cross-Reference Synthesis

Opus applies cross-reference rules to the combined findings:

- **HIGH priority**: `.env.example` missing `REDIS_URL` — found in BOTH Fork A (env docs stale) and Fork C (deploy env mismatch). Two-layer overlap → promoted to HIGH.
- **HIGH priority**: 3 endpoints in API docs that don't exist in code — Fork A (doc claims X exists) + implicit in Fork B (no dead imports for those handlers). Promoted.
- **MEDIUM priority**: `src/utils/legacy-auth.ts` dead code (Fork B only)
- **MEDIUM priority**: 3 stale TODOs (Fork B only)
- **MEDIUM priority**: README version mismatch (Fork A only)

No gating issues found. Grade remains as-scored.

### Step 7: Gap Report Presented to User

```
REPO AUDIT: cbass
Run ID: 20260305_143022

SCORES:
  Docs-to-Code:        87/100  B
  Internal Consistency: 88/100  B
  Code-to-Deploy:      85/100  B
  Overall Average:     87/100  B

FIX FIRST (HIGH):
  1. Add REDIS_URL to .env.example
     → Referenced in src/services/cache.ts:14 but missing from docs and Dockerfile ENV
  2. Remove 3 stale API docs entries (GET /v2/users, POST /v2/auth, DELETE /v2/sessions)
     → Documented in README API section but handlers deleted in commit a3f9d2b

RECOMMENDED NEXT (MEDIUM):
  3. Delete src/utils/legacy-auth.ts (dead code, also pulls in lodash)
  4. Resolve 3 TODOs in src/services/ (oldest: 2025-08-14)
  5. Update README version from "v2 API" to "v3 API"
  6. Add redis-cli to Dockerfile build stage

Full report: /tmp/repo-audit/cbass/20260305_143022/
```

## Output

**What the user gets:**
- Layer-by-layer scores with letter grades in under 10 minutes
- Prioritized gap list (HIGH first, then MEDIUM) with exact file references
- No false positives — cross-referenced findings get higher priority, single-layer findings stay MEDIUM
- A permanent run directory with all raw fork outputs for deeper review
