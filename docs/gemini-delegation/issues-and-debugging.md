# Gemini Forked Terminal — Issues & Debugging Guide

**Created:** 2026-02-11
**Source:** Observations from OpenClaw architecture deep-dive delegation (5 parallel Gemini tasks, all failed)

---

## Executive Summary

The Gemini CLI forked terminal delegation pipeline initially had a **0% success rate** across 10 attempts (2 rounds of 5 parallel tasks). Every task exited with code 1. Root cause was **429 RESOURCE_EXHAUSTED** on `gemini-3-flash-preview` via the `cloudcode-pa.googleapis.com` endpoint, compounded by launching 5 concurrent processes.

**Status (2026-02-11):** All issues investigated and resolved. Single tasks, parallel x2, and API key auth all validated. Executor upgraded with retry/fallback, error classification, and auth mode support.

---

## Issue 1: MODEL_CAPACITY_EXHAUSTED (429) — Primary Blocker

**Severity:** Critical
**Frequency:** 100% of attempts (10/10)

### Symptoms

All 5 parallel Gemini tasks fail with:
```
RetryableQuotaError: No capacity available for model gemini-3-flash-preview on the server
```

HTTP error details:
```json
{
  "error": {
    "code": 429,
    "message": "No capacity available for model gemini-3-flash-preview on the server",
    "status": "RESOURCE_EXHAUSTED",
    "details": [{
      "@type": "type.googleapis.com/google.rpc.ErrorInfo",
      "reason": "MODEL_CAPACITY_EXHAUSTED",
      "domain": "cloudcode-pa.googleapis.com"
    }]
  }
}
```

### API Endpoint

All requests go to:
```
https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse
```

This is the **internal Code Assist API** (OAuth-authenticated), NOT the standard Gemini API (`generativelanguage.googleapis.com`). The `v1internal` path suggests it uses Google's free-tier Code Assist quota, which has aggressive rate limits.

### Observations

1. **Both OAuth and API key fail** — First round used OAuth (Google account), second round used explicit `GEMINI_API_KEY=AIzaSyCx5...`. Both hit the same 429.
2. **`--model auto` doesn't help** — The `auto` router still resolves to `gemini-3-flash-preview` which is exhausted.
3. **Gemini's built-in retry exhausts** — The CLI retries 3 times with backoff, then gives up and dumps the error as a client error JSON to `/tmp/gemini-client-error-*.json`.
4. **11 client error JSONs dumped** — 11 separate `sendMessageStream` errors in `/tmp/` from a single session.
5. **All 5 tasks fail at the FIRST turn** — Gemini never processes any file reads or tool calls. It dies on the initial prompt submission.

### Root Cause Hypothesis

The `cloudcode-pa.googleapis.com` endpoint has **per-user or per-project concurrent request limits**. Launching 5 parallel Gemini processes saturates this quota instantly. Even sequential retries fail because:
- All 5 processes retry at roughly the same time (backoff jitter is insufficient)
- The quota may have a longer cooldown than the retry window (~2-3 minutes)

### Investigation Needed

1. **What are the actual rate limits?** — Is it per-minute, per-hour, or per-project?
2. **Does the standard API (`generativelanguage.googleapis.com`) have different limits?** — Can we force Gemini CLI to use the standard endpoint instead of `cloudcode-pa`?
3. **Does `GEMINI_API_KEY` route to a different endpoint?** — The error shows the same `cloudcode-pa` endpoint even with an API key, suggesting the CLI ignores the API key when OAuth is also cached.
4. **Is there a concurrency limit vs. rate limit?** — Would 1 sequential task succeed where 5 parallel fail?
5. **Would a paid Google Cloud project bypass this?** — AI Studio vs. Vertex AI quotas.

---

## Issue 2: OAuth vs API Key Routing Confusion

**Severity:** High

### Problem

The Gemini CLI seems to prefer OAuth credentials over API key even when `GEMINI_API_KEY` is explicitly set. Evidence:

1. Second attempt exported `GEMINI_API_KEY` in the executor script
2. Error logs still show `cloudcode-pa.googleapis.com` (OAuth endpoint)
3. The standard API key endpoint would be `generativelanguage.googleapis.com`

### From the Executor Script

```python
# gemini_task_executor.py line 192-194
gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
env_export = f"export GEMINI_API_KEY='{gemini_api_key}' && " if gemini_api_key else ""
shell_cmd = f"set -o pipefail; {env_export}{gemini_cmd} 2>&1 | tee -a '{log_file}'"
```

The key IS exported, but Gemini CLI may have a credential precedence chain:
1. Cached OAuth token (`~/.gemini/` or `~/.config/google/`) — **takes priority**
2. `GEMINI_API_KEY` environment variable
3. Application Default Credentials (ADC)

### Investigation Needed

1. Check `~/.gemini/settings.json` for `security.auth.selectedType`
2. Can we force API key auth? (`--auth-mode api-key`?)
3. Does clearing OAuth cache (`~/.gemini/credentials.json`?) force API key usage?
4. What's the actual credential precedence in the Gemini CLI source?

---

## Issue 3: Parallel Execution Overwhelms Quota

**Severity:** High

### Problem

The delegation pipeline launches 5 Gemini processes simultaneously. Even if the per-request limit is generous, 5 concurrent processes with 3 retries each = up to 15 near-simultaneous requests.

### Evidence

Fork logs show all 5 tasks starting within 5 seconds of each other:
```
/tmp/fork_gemini-task_20260211_093418.log
/tmp/fork_gemini-task_20260211_093420.log
/tmp/fork_gemini-task_20260211_093421.log
/tmp/fork_gemini-task_20260211_093423.log
/tmp/fork_gemini-task_20260211_093424.log
```

And the second round (retry) also starts 5 within 5 seconds:
```
/tmp/fork_gemini-task_20260211_093946.log
/tmp/fork_gemini-task_20260211_093948.log
/tmp/fork_gemini-task_20260211_093950.log
/tmp/fork_gemini-task_20260211_093951.log
/tmp/fork_gemini-task_20260211_093953.log
```

### Possible Solutions

1. **Staggered launch** — Add configurable delay between forks (e.g., 30-60 seconds)
2. **Sequential fallback** — If first task hits 429, switch to sequential mode for remaining
3. **Concurrency limit** — Cap parallel Gemini tasks at 2-3 instead of 5
4. **Queue with retry** — Add a task queue with per-task exponential backoff

---

## Issue 4: Model Selection with `auto` is Opaque

**Severity:** Medium

### Problem

All done.json files show `"model_used": "auto"` — we never learn which actual model Gemini attempted to use. The error says `gemini-3-flash-preview` but that may be the auto-router's first choice, not the only option.

### From done.json (all 5 tasks identical pattern)

```json
{
  "exit_code": 1,
  "model_used": "auto",
  "duration_seconds": 143.4,
  "task_name": "g1-gateway"
}
```

### Investigation Needed

1. Does `auto` try Flash first, then Pro? Or vice versa?
2. If Flash is exhausted, does `auto` fall back to Pro? Or just fail?
3. Can we observe the actual model attempted from the error JSON?
4. Would explicit `--model gemini-2.5-flash` (older, stable) bypass the preview model limits?

---

## Issue 5: No Response JSON Parsed on Failure

**Severity:** Low (cosmetic)

### Problem

When Gemini fails at the first turn, there's no JSON output to parse. The executor correctly handles this:
```
WARNING: Could not parse JSON from Gemini output
```

But the done.json has no `tokens` field, making it impossible to know if ANY tokens were consumed.

### Impact

Can't tell if we're being charged for failed requests. The 429 may occur before token consumption, but without stats we can't confirm.

---

## Issue 6: IDE Extension Warning Noise

**Severity:** Low

### Symptom

Every Gemini task logs:
```
[ERROR] [IDEClient] Failed to connect to IDE companion extension. Please ensure the extension is running.
```

This is expected in a headless/forked terminal but clutters logs. Not a functional issue.

### Fix

Investigate if there's a `--no-ide` flag or env var to suppress this.

---

## Complete Failure Timeline (Round 1)

```
09:34:18  Fork G1 (gateway)
09:34:20  Fork G2 (agent-runtime)
09:34:21  Fork G3 (channels)
09:34:23  Fork G4 (memory-core)
09:34:24  Fork G5 (memory-plugins)
~09:35    All 5 hit first 429 (Attempt 1)
~09:36    All 5 retry (Attempt 2) — still 429
~09:37    All 5 retry (Attempt 3) — still 429
09:39:47  G1 gives up (wrote client-error JSON), starts cleanup
09:41:19  G3 completes (exit 1, 88.8s)
09:41:35  G5 completes (exit 1, 101.6s)
09:42:00  G2 completes (exit 1, 131.9s)
09:42:10  G1 completes (exit 1, 143.4s)
09:42:45  G4 completes (exit 1, 173.3s)
```

All tasks ran for 88-173 seconds despite failing immediately — the time is spent in retry backoff loops.

---

## Debugging Checklist (Completed 2026-02-11)

- [x] Run a SINGLE Gemini task (not parallel) and verify it succeeds — **PASS** (auto model, fell back from gemini-3-flash-preview to gemini-2.5-flash-lite)
- [x] Check `~/.gemini/settings.json` auth configuration — `oauth-personal` confirmed
- [x] Test with explicit `--model gemini-2.5-flash` (non-preview, older model) — **PASS** (immediate success, 1.8s)
- [x] Test with `GEMINI_API_KEY` after clearing OAuth cache — **PASS** (E2B sandbox, routes to `generativelanguage.googleapis.com`)
- [x] Verify which API endpoint is hit (cloudcode-pa vs generativelanguage) — Both confirmed, depends on auth method
- [ ] Check Google Cloud Console for quota usage/limits — Not needed, issues resolved empirically
- [x] Test at different times of day (capacity may vary) — Preview models are capacity-constrained, stable models work reliably
- [x] Add staggered launch delay to executor — **DONE** (`--delay` flag in fork_terminal.py)
- [x] Add concurrency limit to delegator agent — **DONE** (max 2 concurrent, documented in delegator)
- [ ] Test with Vertex AI endpoint as alternative — **DEFERRED** (needs GCP project setup)
- [x] Test parallel x2 — **PASS** (both tasks succeeded simultaneously)
- [x] Test stream-json output — **PASS** (NDJSON events: init, message, result)
- [x] Add error classification to executor — **DONE** (`classify_error()` function)
- [x] Add retry/fallback to executor — **DONE** (model chain with configurable retries)
- [x] Add auth mode support to executor — **DONE** (`--auth-mode oauth|api-key|vertex-ai`)

---

## Related Files (Copied to This Repo)

| File | Description |
|------|-------------|
| `agents/gemini-delegator.md` | Orchestration agent |
| `commands/gemini.md` | `/gemini` slash command |
| `skills/fork-terminal/` | Terminal forking infrastructure |
| `skills/multi-model-orchestration/` | Model selection framework |
| `docs/delegation-pipeline-guide.md` | Operational guide (from previous debugging) |
| `docs/gemini-cli-cookbook.md` | CLI usage reference |
| `logs/` | Preserved error logs from failed attempts |
