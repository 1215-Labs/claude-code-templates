# Repo Audit Engine — Worked Example

## Scenario

The user runs: `/repo-audit "/home/user/projects/myapp"`

The target repo is a Node.js Express API with a Dockerfile and GitHub Actions deploy workflow.

## Step 1: Pre-Flight Checks

```bash
ls /home/user/projects/myapp
# → src/ tests/ Dockerfile .github/ package.json CLAUDE.md docs/ .claude/
```

Checks pass:
- Path exists
- Not the templates repo
- Has `.git/` directory

## Step 2: Layer Detection

Check for deploy config:
```bash
ls /home/user/projects/myapp/Dockerfile          # exists
ls /home/user/projects/myapp/.github/workflows/  # exists, contains deploy.yml
```

Result: All three layers apply — Docs-to-Code, Internal Consistency, Code-to-Deploy.

## Step 3: Create Run Directory

```bash
RUN_DIR=/tmp/repo-audit/myapp/20260307_143022
mkdir -p $RUN_DIR
```

## Step 4: Launch Forks A and B Concurrently

**Fork A (OpenCode — Docs-to-Code):**

Filled prompt includes:
- `{REPO_PATH}` = `/home/user/projects/myapp`
- `{REPO_NAME}` = `myapp`
- `{RUN_DIR}` = `/tmp/repo-audit/myapp/20260307_143022`
- `{KNOWN_DRIFT}` = contents from `.claude/INDEX.md` Known Drift section (if present)

Task: Cross-reference all docs against actual code. Check README, CLAUDE.md, `.claude/` component references, API docs, env var documentation.

**Fork B (Codex — Internal Consistency):**

Task: Find dead code, broken imports, unused dependencies, stale `.claude/` references, broken package scripts.

Both launched simultaneously (different providers, no rate conflict).

## Step 5: Wait for A, Then Launch C

After Fork A completes (~3-4 min):

Launch Fork C (OpenCode — Code-to-Deploy):

Task: Cross-reference `Dockerfile`, `.github/workflows/deploy.yml` with codebase. Check port configs, env vars, build output directories, health check endpoints.

## Step 6: Poll for Completion

Check every 30 seconds:
```bash
ls $RUN_DIR/fork-a.done.json  # appears after ~3-4 min
ls $RUN_DIR/fork-b.done.json  # appears after ~3-4 min
ls $RUN_DIR/fork-c.done.json  # appears after A + ~2 min
```

## Step 7: Synthesize Findings

Read all three `fork-*.response.json` files. Apply cross-reference rules:

**Fork A finds:** "README says `npm run dev` starts the server, but package.json has no `dev` script."

**Fork B finds:** "package.json `start` script references `dist/server.js` but no `dist/` directory exists — build step missing."

**Cross-reference:** Both A and B flag the missing build step. Severity promoted: LOW → MEDIUM → HIGH. Gating issue? Yes — build command fails. Grade capped at C.

**Fork C finds:** "Dockerfile exposes port 3000, but app listens on `process.env.PORT || 8080`. Deploy config uses port 3000. Mismatch when PORT env var is not set."

## Step 8: Score Each Layer

**Docs-to-Code:** 100 points
- Build/test commands accurate: -15 (README `npm run dev` does not exist)
- API docs match endpoints: -15 (3 documented endpoints missing from router)
- Commands/agents referenced exist: -5 (one stale .claude reference)
- Score: 65/100 → D

**Internal Consistency:** 100 points
- All imports resolve: -20 (`dist/server.js` referenced but not built)
- No stale .claude/ references: -10 (REGISTRY.md references deleted agent)
- No unused dependencies: -10 (`lodash` imported nowhere)
- Score: 60/100 → D

**Code-to-Deploy:** 100 points
- Port/host configs consistent: -10 (port 3000 vs 8080 mismatch)
- Env vars documented and used: -15 (`PORT` used but not in .env.example)
- CI builds what deploy expects: -20 (no build step in CI before deploy)
- Score: 55/100 → F

**Gating issues detected:**
- Build command fails (npm run dev missing, no build step)
- Grade cap: C regardless of numeric scores

**Overall: C (Gating Issue Present)**

## Step 9: Report to User

```
Repo Audit: myapp — Grade C (Gating Issue)

Fix First (gating issues — cap grade at C):
  1. [CRITICAL] No build step in CI — deploy copies unbuild source. Add `npm run build` before deploy.
  2. [CRITICAL] README references `npm run dev` which does not exist in package.json.

High Priority:
  3. Port mismatch: Dockerfile EXPOSE 3000, app defaults to 8080 when PORT unset.
  4. 3 API endpoints documented in docs/api.md do not exist in router.

Medium Priority:
  5. `lodash` in package.json but not imported anywhere.
  6. Stale .claude/REGISTRY.md row references deleted `query-builder` agent.
  7. `PORT` env var used in code but missing from .env.example.

Scores: Docs-to-Code 65/100 | Internal Consistency 60/100 | Code-to-Deploy 55/100
Full report: /tmp/repo-audit/myapp/20260307_143022/
```

## Timeline

| Phase | Duration |
|-------|----------|
| Pre-flight + layer detection | ~30 sec |
| Forks A + B concurrent | ~3-4 min |
| Fork C (after A) | ~2 min |
| Synthesis + scoring | ~1 min |
| **Total** | **~7-8 min** |
