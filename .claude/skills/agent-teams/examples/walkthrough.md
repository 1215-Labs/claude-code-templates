# Agent Teams — Example Walkthrough

## Scenario

A developer needs to implement a full CRUD API for a user management system, complete with unit tests and OpenAPI documentation. The work clearly separates into three independent layers: backend routes, test coverage, and API docs. Doing this sequentially in one session would be slow; the layers can be built in parallel with no file conflicts.

## Trigger

> User: "implement a full CRUD API for user management with tests and OpenAPI docs"

## Step-by-Step

### Step 1: Task Analysis

Opus evaluates whether this warrants a team:
- Parallel work available? Yes — backend, tests, and docs can be built simultaneously
- Workers need to communicate? Minimal — tests need to know the route signatures, but docs and backend are independent
- File conflicts possible? No — clear directory partitioning
- Worth the coordination overhead? Yes — 3 layers in parallel is ~3x faster than sequential

Decision: spawn a 3-teammate team with a lead + builder + validator pattern.

### Step 2: Create Team and Decompose Tasks

Opus creates the team and defines tasks before spawning teammates:

```
Team: user-crud-feature
Teammates:
  - backend-api   (implements routes)
  - test-writer   (writes unit tests)
  - docs-writer   (produces OpenAPI schema)
```

**Task assignments:**

| Task | Owner | Files | Blocked By |
|------|-------|-------|-----------|
| T1: GET /users endpoint | backend-api | src/routes/users.ts | — |
| T2: POST /users endpoint | backend-api | src/routes/users.ts | — |
| T3: PUT /users/:id endpoint | backend-api | src/routes/users.ts | — |
| T4: DELETE /users/:id endpoint | backend-api | src/routes/users.ts | — |
| T5: Update route index | backend-api | src/routes/index.ts | T1, T2, T3, T4 |
| T6: Unit tests for GET/POST | test-writer | tests/routes/users.test.ts | — |
| T7: Unit tests for PUT/DELETE | test-writer | tests/routes/users.test.ts | T6 |
| T8: GET + POST OpenAPI schema | docs-writer | docs/api/users.yaml | — |
| T9: PUT + DELETE OpenAPI schema | docs-writer | docs/api/users.yaml | T8 |

### Step 3: Spawn Teammates

Opus spawns three teammates with scoped prompts:

**backend-api spawn prompt:**
```
Implement CRUD endpoints for /api/users in src/routes/users.ts.
Follow existing patterns in src/routes/products.ts.
You own these files exclusively: src/routes/users.ts, src/routes/index.ts.
Do NOT modify any other files.
Run tests after each endpoint: npm test -- --grep "users"
```

**test-writer spawn prompt:**
```
Write unit tests for the /api/users CRUD endpoints in tests/routes/users.test.ts.
Follow existing test patterns in tests/routes/products.test.ts.
You own this file exclusively: tests/routes/users.test.ts.
Test all four methods: GET, POST, PUT, DELETE.
Mock the database layer using the existing db-mock helper.
```

**docs-writer spawn prompt:**
```
Write OpenAPI 3.0 schema for the /api/users CRUD endpoints in docs/api/users.yaml.
Follow the existing schema structure in docs/api/products.yaml.
You own this file exclusively: docs/api/users.yaml.
Document all request bodies, response shapes, and error codes.
```

### Step 4: Opus Enters Delegate Mode

Opus presses Shift+Tab to enter delegate mode. It will not implement anything itself — only coordinate, answer questions, and resolve blockers.

### Step 5: Parallel Execution

All three teammates work simultaneously:

- **backend-api** implements GET /users (T1), commits, moves to POST /users (T2), etc.
- **test-writer** writes GET + POST tests (T6) in parallel, then PUT + DELETE tests (T7)
- **docs-writer** documents GET + POST schema (T8) in parallel, then PUT + DELETE (T9)

backend-api finishes T1-T4 and messages Opus:

> "All four CRUD endpoints implemented and tests passing locally. Ready for T5 (route index update)."

Opus unblocks T5 in the task list. backend-api updates the route index.

### Step 6: Validation Check

test-writer messages Opus after T7:

> "All 8 tests written. 7 pass. The DELETE test is failing — DELETE /users/:id returns 204 but my test expects 200. Should I update the test or is the route wrong?"

Opus checks the API conventions doc and responds:

> "204 is correct for DELETE. Update the test to expect 204."

test-writer fixes the test. All 8 pass.

### Step 7: Shutdown and Summary

Opus sends shutdown requests to all three teammates after confirming all tasks are complete. Opus synthesizes a handoff summary:

```
User CRUD API complete:
  - 4 endpoints implemented: GET, POST, PUT, DELETE /api/users
  - 8 unit tests passing (tests/routes/users.test.ts)
  - OpenAPI schema documented (docs/api/users.yaml)
  - Route index updated (src/routes/index.ts)

Files changed:
  src/routes/users.ts
  src/routes/index.ts
  tests/routes/users.test.ts
  docs/api/users.yaml
```

## Output

**What the user gets:**
- A complete CRUD API implementation with tests and OpenAPI docs, delivered in the time it would have taken to build just the backend routes alone
- All 4 files clearly partitioned — no merge conflicts
- A clean task history showing exactly which teammate built what
- Opus's context preserved for further coordination (no implementation work done by lead)

**Files created/modified:**
- `src/routes/users.ts` — 4 CRUD endpoints
- `src/routes/index.ts` — registered new routes
- `tests/routes/users.test.ts` — 8 unit tests
- `docs/api/users.yaml` — OpenAPI 3.0 schema
