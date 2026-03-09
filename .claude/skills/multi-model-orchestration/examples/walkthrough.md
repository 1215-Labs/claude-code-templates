# Multi-Model Orchestration — Example Walkthrough

## Scenario

A developer has a 500k-token monorepo containing a Django REST API, React frontend, and Postgres schema spread across hundreds of files. They need to find all API endpoints and understand which ones lack authentication. The codebase is too large for Opus to hold in context, and manually grepping is error-prone across this many files.

## Trigger

> User: "our codebase is 500k tokens, help me find all the API endpoints and which ones are missing authentication"

## Step-by-Step

### Step 1: Task Classification

Opus recognizes this as a large-codebase exploration task — the user's 500k-token codebase exceeds what Opus can hold directly. OpenCode with multi-provider model access is the right tool. Opus will NOT attempt to grep or read files itself.

Decision path:
- Large task? Yes
- Codebase exploration? Yes → Fork OpenCode (multi-provider)

### Step 2: Structure the OpenCode Prompt

Opus constructs a scoped exploration prompt:

```
Explore the API endpoint structure in this Django/React codebase at /home/user/projects/myapp.

Focus on:
- All URL patterns in urls.py files (list every endpoint with HTTP method)
- Authentication decorators or middleware applied to each view
- Views that have NO authentication (no @login_required, no IsAuthenticated, no JWT check)
- The pattern used for auth — is it decorator-based, class-based, or middleware?

Write findings to docs/exploration/api-endpoints.md using progressive disclosure format:
- Executive Summary (2-3 sentences)
- Quick Reference table: endpoint | method | auth status
- Critical Files (urls.py files, auth middleware, base view classes)
- Patterns & Conventions (how auth is applied)
- Edge Cases (public endpoints that should be public, e.g. /health, /login)
- Raw Findings (full endpoint list with file:line references)
```

### Step 3: Fork OpenCode

Opus invokes the fork-terminal skill to launch OpenCode in a new terminal window with the constructed prompt. OpenCode has access to the full codebase via its multi-provider model access and begins reading all relevant files.

```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool opencode \
  "opencode -p '{FILLED_PROMPT}' --agent oracle"
```

Opus monitors for output at `docs/exploration/api-endpoints.md`. Poll interval: 30 seconds.

### Step 4: OpenCode Completes Exploration

After ~3 minutes, `docs/exploration/api-endpoints.md` appears. Opus reads the Executive Summary first:

> "This codebase has 47 API endpoints across 8 URL conf files. 12 endpoints have no authentication, including 3 that appear sensitive (user data export, admin stats, billing history). Auth is applied via `@login_required` decorator for function-based views and `IsAuthenticated` permission class for DRF ViewSets."

### Step 5: Opus Reads Quick Reference Table

Opus scans the Quick Reference table — the 12 unauthenticated endpoints are listed with file:line references. Three are flagged as high-risk. Opus does NOT need to read Raw Findings yet.

### Step 6: Opus Synthesizes and Presents to User

Opus presents a structured response:

```
Found 47 endpoints, 12 without authentication.

3 HIGH RISK (likely should be protected):
- GET /api/v1/users/export/ → views/users.py:145 (exports PII)
- GET /api/v1/admin/stats/ → views/admin.py:67 (admin dashboard data)
- GET /api/v1/billing/history/ → views/billing.py:203 (financial records)

9 LOW RISK (likely intentionally public):
- POST /api/v1/auth/login/
- GET /api/v1/health/
- ... (7 more)

Auth pattern: @login_required for FBVs, IsAuthenticated for DRF ViewSets.
Full report: docs/exploration/api-endpoints.md
```

### Step 7: (Optional) Fork Codex to Fix

If the user wants to add authentication to the 3 high-risk endpoints, Opus forks Codex with the exploration doc as context:

```
Fix authentication on these 3 endpoints based on the analysis in docs/exploration/api-endpoints.md:
- views/users.py:145 — add @login_required
- views/admin.py:67 — add IsAdminUser permission
- views/billing.py:203 — add IsAuthenticated permission

Follow the existing auth patterns documented in the exploration.
Run tests after: python manage.py test api.tests.auth
Document changes in docs/implementation/auth-fixes-log.md
```

## Output

**What the user sees:**
- A clear summary of all 47 endpoints in under 5 minutes
- Prioritized list of 3 high-risk unauthenticated endpoints with file:line references
- A permanent reference doc at `docs/exploration/api-endpoints.md` for the team
- Opus's context window remains clean (only the summary was read, not all 500k tokens)

**Files created:**
- `docs/exploration/api-endpoints.md` — OpenCode's full exploration output
- (Optional) `docs/implementation/auth-fixes-log.md` — Codex implementation log
