# Gemini CLI Forked Terminal — Research Findings

**Date**: 2026-02-11
**Sources**: Official Gemini CLI docs, Google Cloud docs, Perplexity research, empirical testing

---

## 1. Rate Limits by Auth Method

From [geminicli.com/docs/quota-and-pricing](https://geminicli.com/docs/quota-and-pricing/):

| Auth Method | RPM | RPD | Models Available | API Endpoint | Cost |
|---|---|---|---|---|---|
| **OAuth (free individual)** | 60 | 1,000 | Gemini family (auto-routed) | `cloudcode-pa.googleapis.com` | Free |
| **GEMINI_API_KEY (free)** | 10 | 250 | Flash only | `generativelanguage.googleapis.com` | Free |
| **GEMINI_API_KEY (paid tier)** | varies | varies | varies by tier | `generativelanguage.googleapis.com` | Per-token |
| **Google AI Pro subscription** | higher | higher | all | `cloudcode-pa.googleapis.com` | $20/mo |
| **Google AI Ultra subscription** | highest | highest | all | `cloudcode-pa.googleapis.com` | $250/mo |
| **Gemini Code Assist Standard** | 120 | 1,500 | auto-routed | `cloudcode-pa.googleapis.com` | Per-seat license |
| **Gemini Code Assist Enterprise** | 120 | 2,000 | auto-routed | `cloudcode-pa.googleapis.com` | Per-seat license |
| **Vertex AI Express (free 90d)** | variable | variable | variable | `{region}-aiplatform.googleapis.com` | Free (90 days) |
| **Vertex AI (paid)** | dynamic shared | no hard limit | all | `{region}-aiplatform.googleapis.com` | Per-token |

### Why 5 Parallel Tasks Failed

5 parallel tasks × ~3 model requests each = 15 requests in the first few seconds.

- Free OAuth quota: 60 RPM — should handle 15 requests mathematically
- **But**: `cloudcode-pa.googleapis.com` appears to have additional **concurrency constraints** beyond RPM (likely 1-3 simultaneous connections per user)
- All 5 processes retry at similar times, creating a thundering herd
- Gemini CLI retries 3 times with backoff, but jitter is insufficient when 5 processes do it simultaneously

### Key Takeaway

The bottleneck isn't RPM — it's **concurrent connections**. Even at 60 RPM, the Code Assist endpoint throttles parallel requests aggressively.

---

## 2. Authentication Routing

From [google-gemini.github.io/gemini-cli/docs/get-started/authentication](https://google-gemini.github.io/gemini-cli/docs/get-started/authentication.html):

### Three Auth Methods

| Method | Trigger | Endpoint | Quota Pool |
|---|---|---|---|
| **Login with Google (OAuth)** | `security.auth.selectedType: "oauth-personal"` in `~/.gemini/settings.json` | `cloudcode-pa.googleapis.com` | Code Assist (60 RPM) |
| **Gemini API Key** | `GEMINI_API_KEY` env var (no OAuth cached) | `generativelanguage.googleapis.com` | AI Studio (10 RPM free, higher paid) |
| **Vertex AI** | `GOOGLE_GENAI_USE_VERTEXAI=true` + project + location | `{region}-aiplatform.googleapis.com` | Vertex AI (dynamic shared) |

### Credential Precedence

Our system has `settings.json` → `security.auth.selectedType: "oauth-personal"` with cached OAuth tokens in `~/.gemini/oauth_creds.json`. This means:

1. **OAuth always wins** when cached tokens exist, even if `GEMINI_API_KEY` is set
2. Setting `GEMINI_API_KEY` alone does NOT override OAuth
3. To force API key: must either clear OAuth creds OR test in clean environment (E2B sandbox)
4. To use Vertex AI: set `GOOGLE_GENAI_USE_VERTEXAI=true` — this env var **does** override other auth methods

### No `--auth-mode` Flag

GitHub issue #3144 documents this gap. There is no CLI flag to force auth method. Workarounds:
- Use E2B sandbox (no cached OAuth)
- Use `GOOGLE_GENAI_USE_VERTEXAI=true` (overrides OAuth)
- Temporarily rename `~/.gemini/oauth_creds.json`

### Per-Project Auth via `.gemini/.env`

Gemini CLI auto-loads variables from `.gemini/.env` (searches up from cwd, then `~/.gemini/.env`). Can use this for per-project auth config without polluting shell:

```
# .gemini/.env
GEMINI_API_KEY=your-key-here
```

Variables loaded from first `.env` found, not merged.

---

## 3. Model Routing

### `auto` Behavior

- Routes between Flash and Pro based on task complexity
- **Does NOT fall back on 429** — if the selected model is capacity-exhausted, it fails
- All done.json files show `"model_used": "auto"` — actual model is opaque
- The error message reveals the actual model attempted (e.g., `gemini-3-flash-preview`)

### Model Quota Pools

**Unconfirmed hypothesis**: Preview models (`gemini-3-flash-preview`, `gemini-3-pro-preview`) may share a different quota pool than stable models (`gemini-2.5-flash`). Testing needed.

### Model Aliases (from CLI help)

| Alias | Resolves To |
|---|---|
| `auto` | Routes Flash/Pro by complexity |
| `pro` | `gemini-3-pro-preview` |
| `flash` | `gemini-3-flash-preview` |
| `flash-lite` | `gemini-2.5-flash-lite` |

---

## 4. Untapped Gemini CLI Features

### Stream-JSON Output (`--output-format stream-json`)

Emits NDJSON events: `init`, `message`, `tool_use`, `tool_result`, `error`, `result`.

**Value**: Detect 429 errors in real-time without waiting for process exit. Currently we use `--output-format json` which buffers everything until completion.

### Allowed Tools (`--allowed-tools`)

Restrict which tools Gemini can use: `--allowed-tools grep,read_file,ls,glob`.

**Value**: Read-only safety for exploration tasks. Prevents accidental file writes.

### Session Resume (`--resume latest`)

Resume the most recent session without re-sending the full prompt.

**Value**: Recover from network failures or timeouts without wasting quota on re-sending context.

### Vertex AI Mode (`GOOGLE_GENAI_USE_VERTEXAI=true`)

Routes to Vertex AI endpoints with dynamic shared quota (no hard RPM limit for paid projects).

**Value**: Highest quota ceiling. Best for parallel/heavy workloads. Free 90-day express mode available.

### `.gemini/.env` File

Per-project auth config without shell pollution. First found file wins (cwd → parent → `~/.gemini/`).

**Value**: Different projects can use different auth methods.

### Gemini Skills System

`.gemini/skills/SKILL.md` files auto-loaded by model based on task context.

**Value**: Project-specific instructions injected automatically — could guide Gemini's exploration strategy.

### Thinking Level

Control reasoning depth: `--thinking-level minimal|medium|high`.

**Value**: Use `high` for architecture reviews, `minimal` for simple file listing — saves tokens and time.

---

## 5. Recommendations

### Immediate (resolve 0% success rate)

1. **Run 1 task first** to confirm single-task baseline works
2. **Cap concurrency at 2** and stagger launches by 60 seconds
3. **Add error classification** in executor to distinguish 429 from other failures
4. **Suppress IDE warning** (`ide.enabled: false` in settings.json)

### Short-term (improve reliability)

5. **Add model fallback chain** in executor: auto → gemini-2.5-flash → fail
6. **Test API key auth** in E2B sandbox (separate quota pool)
7. **Set up Vertex AI** for highest quota ceiling
8. **Use stream-json** for real-time error detection

### Long-term (expand capabilities)

9. **Per-project `.gemini/.env`** for auth flexibility
10. **Gemini skills system** for project-specific exploration guidance
11. **Session resume** for recovering interrupted tasks
12. **Thinking level tuning** per task type
