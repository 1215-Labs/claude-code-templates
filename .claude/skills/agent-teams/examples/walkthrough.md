# Agent Teams — Worked Example

## Scenario

The user asks: "We need to add user profile pages to the app. It needs a new API endpoint, a frontend component, and tests for both."

This is a cross-layer feature with clear boundaries: backend, frontend, and tests can be built in parallel. There are no sequential dependencies except tests coming after the main code.

## Step 1: Classify the Task

- Three independent workstreams: API endpoint, frontend component, tests
- Teammates can work in parallel on separate files
- Role pattern: Cross-Layer Builders (3 teammates)
- File ownership is clean — no shared files at risk

## Step 2: Define Teammate Roles and File Ownership

**Lead (Opus):** Coordinate, delegate, synthesize. No implementation.

**Teammate 1 — backend-api:**
- Implements `GET /users/:id/profile` endpoint
- Owns: `src/routes/users.ts`, `src/services/user-profile.ts`, `src/types/profile.ts`

**Teammate 2 — frontend-ui:**
- Implements the `<UserProfile>` React component
- Owns: `src/components/UserProfile.tsx`, `src/components/UserProfile.css`

**Teammate 3 — test-coverage:**
- Writes tests for both layers (blocked until teammates finish)
- Owns: `tests/routes/users.test.ts`, `tests/components/UserProfile.test.tsx`

## Step 3: Spawn the Team

Spawn teammate 1 (backend-api):
```
Implement GET /users/:id/profile endpoint.

You own these files exclusively:
- src/routes/users.ts (add new route)
- src/services/user-profile.ts (create new service)
- src/types/profile.ts (create Profile type)

Follow existing patterns in src/routes/posts.ts for route structure.
Do NOT modify files outside your ownership.
After each change, run: npm run type-check
```

Spawn teammate 2 (frontend-ui):
```
Implement the UserProfile React component.

You own these files exclusively:
- src/components/UserProfile.tsx (create component)
- src/components/UserProfile.css (create styles)

Follow existing patterns in src/components/PostCard.tsx.
Fetch data from GET /users/:id/profile endpoint (assume it exists).
Do NOT modify files outside your ownership.
```

Spawn teammate 3 (test-coverage):
```
Write tests for the user profile feature.
BLOCKED: Wait until backend-api and frontend-ui complete their tasks first.

You own these files exclusively:
- tests/routes/users.test.ts (API endpoint tests)
- tests/components/UserProfile.test.tsx (component tests)

Run tests after writing: npm test -- --testPathPattern=users
```

Enable delegate mode (Shift+Tab) immediately after spawning.

## Step 4: Monitor Progress

Monitor the task list (Ctrl+T). Expected sequence:

```
[~5 min] backend-api: Task 1 complete (src/routes/users.ts)
[~6 min] frontend-ui: Task 1 complete (UserProfile.tsx)
[~8 min] backend-api: All tasks complete
[~9 min] frontend-ui: All tasks complete
[~11 min] test-coverage: Unblocked — starts running
[~14 min] test-coverage: 12 tests passing, all complete
```

If a teammate messages with a question, respond via targeted message (not broadcast).

Example: backend-api asks "Should Profile include the user's email?" — answer directly, then continue monitoring.

## Step 5: Handle the Shared File Edge Case

Suppose both backend-api and frontend-ui need to update `src/types/index.ts` to export their new types.

Resolution: After both complete, the lead makes that single shared-file edit:
1. Read what backend-api added to `src/types/profile.ts`
2. Read what frontend-ui expects from the index
3. Add both exports to `src/types/index.ts` as the lead

This is a legitimate lead action — not implementation, but coordination.

## Step 6: Clean Up

After test-coverage completes:
1. Read the test results summary
2. Report to user: "User profile feature complete. 12 tests passing across API and frontend."
3. Say "clean up the team" to terminate all teammate sessions

## What Went Right

- Parallel execution cut a ~45-minute sequential task to ~14 minutes
- No file conflicts because ownership was explicit from the start
- The blocked test-coverage task naturally waited without needing manual coordination
- Lead stayed in delegate mode — no context pollution from implementation work

## Expected Timeline

| Phase | Duration |
|-------|----------|
| Spawn 3 teammates | ~2 min |
| Backend + frontend parallel work | ~8 min |
| Tests (after unblock) | ~5 min |
| Lead shared-file edit + cleanup | ~2 min |
| **Total** | **~17 min** |

Sequential equivalent: ~45 min. Parallelism saved ~28 min.
