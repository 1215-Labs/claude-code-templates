# Multi-Model Orchestration — Worked Example

## Scenario

The user asks: "I need to add rate limiting to our API. I've never looked at how the middleware layer works."

This is a classic explore-then-implement task. The codebase is unfamiliar, and there's a clear implementation goal after exploration.

## Step 1: Classify and Decide

- Unfamiliar middleware layer → needs exploration first
- Concrete implementation goal → Codex after exploration
- Pattern: Explore-Then-Implement (Pattern 1)

## Step 2: Fork OpenCode to Explore

Construct and send the exploration prompt:

```
Explore the middleware architecture in this codebase.

Focus on:
- How existing middleware is structured and registered (src/middleware/)
- The request/response lifecycle and where middleware hooks in
- Any existing rate limiting or throttling code (even partial)
- Naming conventions and patterns I should follow when adding new middleware

Write findings to docs/exploration/middleware.md using progressive disclosure format
(Executive Summary → Quick Reference → Architecture → Critical Files → Patterns → Recommendations).
```

Fork with: `openai/gpt-5.2 via oracle agent` via fork-terminal. Output: `docs/exploration/middleware.md`.

Tell the user: "Forking OpenCode to explore the middleware layer. This takes about 2-3 minutes."

## Step 3: Read Results Progressively

When `docs/exploration/middleware.md` appears:

1. Read Executive Summary (2-3 sentences) — get the gist
2. Scan Quick Reference table — key facts
3. Check Recommendations section — OpenCode's guidance for implementation

Example summary OpenCode might produce:
> "Middleware is registered in `src/middleware/index.ts` via an `applyMiddleware()` factory. All middleware must export a function matching the `Middleware` interface in `src/types/middleware.ts`. There is no existing rate limiting; the closest is the 10s request timeout in `src/middleware/timeout.ts`."

Synthesize this for the user: "Found the middleware pattern. All middleware goes in `src/middleware/`. There's a clean `Middleware` interface to implement. No existing rate limiting — we're building from scratch."

## Step 4: Fork Codex to Implement

Construct the implementation prompt using OpenCode's output:

```
Implement a rate limiting middleware for the API, based on the exploration in
docs/exploration/middleware.md.

Requirements:
- Create src/middleware/rate-limit.ts following the Middleware interface pattern
- Default: 100 requests per minute per IP address (configurable via env var RATE_LIMIT_RPM)
- Return 429 Too Many Requests with Retry-After header on limit exceeded
- Register the middleware in src/middleware/index.ts (after auth, before routes)
- Write unit tests in tests/middleware/rate-limit.test.ts

After implementation:
1. Run: npm test -- --testPathPattern=rate-limit
2. Document changes in docs/implementation/rate-limiting-log.md
3. List all files modified
```

Fork with: `gpt-5.2-codex` via fork-terminal.

Tell the user: "Forking Codex to implement the rate limiter. Estimated 3-5 minutes."

## Step 5: Review Implementation Results

When `docs/implementation/rate-limiting-log.md` appears, read the Files Changed table and test results:

```
Files Changed:
| File | Change Type | Description |
|------|-------------|-------------|
| src/middleware/rate-limit.ts | Created | Rate limiter with sliding window counter |
| src/middleware/index.ts | Modified | Registered after auth middleware |
| tests/middleware/rate-limit.test.ts | Created | 8 unit tests |

Tests:
✓ 8/8 passing
```

Report to user: "Done. Rate limiting middleware created and registered. 8 tests passing. Files are in `src/middleware/rate-limit.ts`. Want me to show you the implementation?"

## What Opus Does Throughout

- Classifies the task (2 seconds)
- Constructs exploration prompt with focused questions (30 seconds)
- Reads OpenCode's summary selectively, not raw findings (saves context)
- Synthesizes finding for user in plain language
- Constructs implementation prompt with exploration context attached
- Reports final results with file list and test status

Opus never reads the full codebase or writes code. Context window stays clean for user conversation.

## Expected Timeline

| Phase | Duration |
|-------|----------|
| Fork OpenCode + wait | ~2-3 min |
| Read summary + synthesize | ~30 sec |
| Fork Codex + wait | ~3-5 min |
| Read results + report | ~30 sec |
| **Total** | **~6-9 min** |
