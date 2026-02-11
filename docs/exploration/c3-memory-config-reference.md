# C3 Memory Config Reference (OpenClaw)

Source files used:
- `references/openclaw/src/config/types.memory.ts`
- `references/openclaw/src/config/types.agent-defaults.ts`
- `references/openclaw/src/config/types.tools.ts`
- `references/openclaw/src/config/zod-schema.ts`
- `references/openclaw/src/config/zod-schema.agent-defaults.ts`
- `references/openclaw/src/config/zod-schema.agent-runtime.ts`
- `references/openclaw/src/memory/backend-config.ts`
- `references/openclaw/src/memory/types.ts`
- `references/openclaw/src/agents/memory-search.ts`
- `references/openclaw/src/auto-reply/reply/memory-flush.ts`
- `references/openclaw/src/agents/pi-settings.ts`
- `references/openclaw/src/config/paths.ts`
- `references/openclaw/src/agents/model-auth.ts`
- `references/openclaw/extensions/memory-lancedb/config.ts`
- `references/openclaw/extensions/memory-lancedb/openclaw.plugin.json`
- `references/openclaw/docs/concepts/memory.md`

## 1) Memory Configuration Schema

### 1.1 Top-level memory config (`memory.*`)

| Path | Type | Default (resolved) | Validation / rules | Description |
|---|---|---|---|---|
| `memory` | object | unset | strict object | Top-level memory backend config. |
| `memory.backend` | `"builtin" \| "qmd"` | `"builtin"` | zod enum | Memory backend selector. |
| `memory.citations` | `"auto" \| "on" \| "off"` | `"auto"` | zod enum | Controls citation footer behavior in memory snippets. |
| `memory.qmd` | object | unset | strict object | QMD sidecar configuration (used when backend is `qmd`). |
| `memory.qmd.command` | string | `"qmd"` | zod string | QMD binary/command. |
| `memory.qmd.includeDefaultMemory` | boolean | `true` | zod boolean | Include `MEMORY.md` + `memory/**/*.md` collections automatically. |
| `memory.qmd.paths` | `MemoryQmdIndexPath[]` | `[]` | zod array | Additional indexed paths/collections. |
| `memory.qmd.paths[].path` | string (required) | n/a | required by zod | Path to file/dir to index. |
| `memory.qmd.paths[].name` | string | auto-generated unique slug | optional | Stable collection name. |
| `memory.qmd.paths[].pattern` | string | `"**/*.md"` | optional | Glob mask relative to collection path. |
| `memory.qmd.sessions` | object | disabled object | strict object | Session transcript indexing to QMD collection. |
| `memory.qmd.sessions.enabled` | boolean | `false` | zod boolean | Enable session export/indexing. |
| `memory.qmd.sessions.exportDir` | string | `<state>/agents/<id>/qmd/sessions` | optional | Export directory for session markdown/jsonl transforms. |
| `memory.qmd.sessions.retentionDays` | number | unset | zod int `>= 0`; runtime keeps only `> 0` | Retention window for exported session data. |
| `memory.qmd.update` | object | defaults applied | strict object | Update/embed cadence and timeouts. |
| `memory.qmd.update.interval` | duration string | `"5m"` | parsed with default unit minutes | Periodic `qmd update` cadence. |
| `memory.qmd.update.debounceMs` | number | `15000` | zod int `>= 0` | Debounce for update triggers. |
| `memory.qmd.update.onBoot` | boolean | `true` | zod boolean | Run update once on startup. |
| `memory.qmd.update.waitForBootSync` | boolean | `false` | zod boolean | Block startup until boot update finishes. |
| `memory.qmd.update.embedInterval` | duration string | `"60m"` | parsed with default unit minutes | Cadence threshold for running `qmd embed`. |
| `memory.qmd.update.commandTimeoutMs` | number | `30000` | zod int `>= 0`; runtime uses fallback unless `> 0` | Timeout for generic qmd CLI commands. |
| `memory.qmd.update.updateTimeoutMs` | number | `120000` | zod int `>= 0`; runtime fallback unless `> 0` | Timeout for `qmd update`. |
| `memory.qmd.update.embedTimeoutMs` | number | `120000` | zod int `>= 0`; runtime fallback unless `> 0` | Timeout for `qmd embed`. |
| `memory.qmd.limits` | object | defaults applied | strict object | Limits for retrieval payload. |
| `memory.qmd.limits.maxResults` | number | `6` | zod int `> 0` | Max hits returned. |
| `memory.qmd.limits.maxSnippetChars` | number | `700` | zod int `> 0` | Per-snippet truncation cap. |
| `memory.qmd.limits.maxInjectedChars` | number | `4000` | zod int `> 0` | Total injected chars budget. |
| `memory.qmd.limits.timeoutMs` | number | `4000` | zod int `>= 0`; runtime fallback unless `> 0` | Query timeout. |
| `memory.qmd.scope` | `SessionSendPolicyConfig` | DM-only policy | Session schema | QMD recall visibility gating by channel/chat type. |

Default QMD `scope` if omitted:

```json
{
  "default": "deny",
  "rules": [{ "action": "allow", "match": { "chatType": "direct" } }]
}
```

### 1.2 Agent defaults memory search (`agents.defaults.memorySearch.*`)

| Path | Type | Default (resolved) | Validation / rules | Description |
|---|---|---|---|---|
| `agents.defaults.memorySearch` | object | enabled config | strict object | Built-in memory index/search config. |
| `agents.defaults.memorySearch.enabled` | boolean | `true` | zod boolean | Master toggle. |
| `agents.defaults.memorySearch.sources` | `("memory"\|"sessions")[]` | `["memory"]` | zod enum array | Indexed sources. `sessions` only active when sessionMemory is true. |
| `agents.defaults.memorySearch.extraPaths` | string[] | `[]` | zod array | Extra .md paths/dirs to index. |
| `agents.defaults.memorySearch.experimental.sessionMemory` | boolean | `false` | zod boolean | Enables session transcript source handling. |
| `agents.defaults.memorySearch.provider` | `"openai"\|"gemini"\|"local"\|"voyage"` | runtime allows `"auto"` fallback when unset | zod enum optional | Embedding provider selection. |
| `agents.defaults.memorySearch.remote.baseUrl` | string | provider default | zod string | Remote embeddings endpoint override. |
| `agents.defaults.memorySearch.remote.apiKey` | string | resolved from auth/env when unset | zod string | Explicit API key. |
| `agents.defaults.memorySearch.remote.headers` | map<string,string> | `{}` | zod record | Extra request headers. |
| `agents.defaults.memorySearch.remote.batch.enabled` | boolean | `false` | zod boolean | Batch embedding mode. |
| `agents.defaults.memorySearch.remote.batch.wait` | boolean | `true` | zod boolean | Wait for batch completion. |
| `agents.defaults.memorySearch.remote.batch.concurrency` | number | `2` | zod int `> 0` | Parallel batch job submissions. |
| `agents.defaults.memorySearch.remote.batch.pollIntervalMs` | number | `2000` | zod int `>= 0` | Batch polling interval. |
| `agents.defaults.memorySearch.remote.batch.timeoutMinutes` | number | `60` | zod int `> 0` | Batch timeout. |
| `agents.defaults.memorySearch.fallback` | `"openai"\|"gemini"\|"local"\|"voyage"\|"none"` | `"none"` | zod enum | Fallback provider when primary fails. |
| `agents.defaults.memorySearch.model` | string | provider-specific: `text-embedding-3-small` (openai), `gemini-embedding-001` (gemini), `voyage-4-large` (voyage), empty for auto/local unless set | zod string | Embedding model id. |
| `agents.defaults.memorySearch.local.modelPath` | string | unset | zod string | Local GGUF/hf path. |
| `agents.defaults.memorySearch.local.modelCacheDir` | string | unset | zod string | Local model cache path. |
| `agents.defaults.memorySearch.store.driver` | `"sqlite"` | `"sqlite"` | zod literal | Storage driver. |
| `agents.defaults.memorySearch.store.path` | string | `<state>/memory/{agentId}.sqlite` | zod string | DB path (`{agentId}` token supported). |
| `agents.defaults.memorySearch.store.vector.enabled` | boolean | `true` | zod boolean | sqlite-vec vector index toggle. |
| `agents.defaults.memorySearch.store.vector.extensionPath` | string | unset | zod string | sqlite-vec library path override. |
| `agents.defaults.memorySearch.chunking.tokens` | number | `400` | zod int `> 0` | Chunk size. |
| `agents.defaults.memorySearch.chunking.overlap` | number | `80` | zod int `>= 0`, clamped `< tokens` | Chunk overlap. |
| `agents.defaults.memorySearch.sync.onSessionStart` | boolean | `true` | zod boolean | Sync when session starts. |
| `agents.defaults.memorySearch.sync.onSearch` | boolean | `true` | zod boolean | Lazy sync before searches when dirty. |
| `agents.defaults.memorySearch.sync.watch` | boolean | `true` | zod boolean | File watcher enabled. |
| `agents.defaults.memorySearch.sync.watchDebounceMs` | number | `1500` | zod int `>= 0` | Watch debounce. |
| `agents.defaults.memorySearch.sync.intervalMinutes` | number | `0` | zod int `>= 0` | Periodic sync interval; 0 disables interval timer. |
| `agents.defaults.memorySearch.sync.sessions.deltaBytes` | number | `100000` | zod int `>= 0` | Session transcript byte threshold before reindex. |
| `agents.defaults.memorySearch.sync.sessions.deltaMessages` | number | `50` | zod int `>= 0` | Session message threshold before reindex. |
| `agents.defaults.memorySearch.query.maxResults` | number | `6` | zod int `> 0` | Max returned results. |
| `agents.defaults.memorySearch.query.minScore` | number | `0.35` | zod `0..1` | Min accepted score. |
| `agents.defaults.memorySearch.query.hybrid.enabled` | boolean | `true` | zod boolean | Hybrid BM25 + vector merge. |
| `agents.defaults.memorySearch.query.hybrid.vectorWeight` | number | `0.7` (normalized with textWeight) | zod `0..1` | Vector weight in hybrid merge. |
| `agents.defaults.memorySearch.query.hybrid.textWeight` | number | `0.3` (normalized with vectorWeight) | zod `0..1` | Text weight in hybrid merge. |
| `agents.defaults.memorySearch.query.hybrid.candidateMultiplier` | number | `4` | zod int `> 0`, clamped `1..20` | Candidate expansion factor. |
| `agents.defaults.memorySearch.cache.enabled` | boolean | `true` | zod boolean | Embedding cache toggle. |
| `agents.defaults.memorySearch.cache.maxEntries` | number | unset | zod int `> 0` | Best-effort cache cap. |

### 1.3 Internal memory types (`src/memory/types.ts`)

| Type | Fields |
|---|---|
| `MemorySearchResult` | `path`, `startLine`, `endLine`, `score`, `snippet`, `source`, `citation?` |
| `MemoryProviderStatus` | backend/provider/model/requestedProvider; corpus stats (`files`, `chunks`); feature status (`cache`, `fts`, `vector`, `batch`); fallback info; paths and source counts |
| `MemorySearchManager` | `search`, `readFile`, `status`, optional `sync`, probe methods |

## 2) Compaction Configuration (`memoryFlush`)

| Path | Type | Default (resolved) | Validation / rules | Description |
|---|---|---|---|---|
| `agents.defaults.compaction.mode` | `"default"\|"safeguard"` | unset | zod enum | Compaction mode. |
| `agents.defaults.compaction.reserveTokensFloor` | number | `20000` | zod int `>= 0` | Reserve token floor used by compaction + memory flush threshold math. |
| `agents.defaults.compaction.maxHistoryShare` | number | unset | zod `0.1..0.9` | Safeguard history cap ratio. |
| `agents.defaults.compaction.memoryFlush` | object | enabled object | strict object | Pre-compaction memory flush turn config. |
| `agents.defaults.compaction.memoryFlush.enabled` | boolean | `true` | zod boolean | Enable/disable memory flush turn. |
| `agents.defaults.compaction.memoryFlush.softThresholdTokens` | number | `4000` | zod int `>= 0` | Trigger when nearing compaction threshold. |
| `agents.defaults.compaction.memoryFlush.prompt` | string | default flush prompt | zod string | User prompt for silent flush turn. |
| `agents.defaults.compaction.memoryFlush.systemPrompt` | string | default system prompt | zod string | System append prompt for flush turn. |

Default `prompt` and `systemPrompt` are from `src/auto-reply/reply/memory-flush.ts` and always forced to include `NO_REPLY` guidance.

Flush threshold formula:

```text
run when totalTokens >= contextWindow - reserveTokensFloor - softThresholdTokens
```

## 3) Memory Search Configuration

### 3.1 Provider/backend selection

| Setting | Behavior |
|---|---|
| `memory.backend` | Chooses retrieval engine for memory tools: `builtin` (SQLite index manager) or `qmd` (QMD sidecar with fallback to builtin on failure). |
| `agents.defaults.memorySearch.provider` | Chooses embedding provider for builtin engine (`openai`, `gemini`, `local`, `voyage`; runtime also supports auto when unset). |
| `agents.defaults.memorySearch.fallback` | Fallback embedding provider when primary fails. |
| `agents.defaults.memorySearch.remote.*` | API endpoint/key/header controls for remote embeddings. |

### 3.2 Hybrid search weights

| Path | Default | Notes |
|---|---|---|
| `agents.defaults.memorySearch.query.hybrid.enabled` | `true` | Enables BM25 + vector merge. |
| `agents.defaults.memorySearch.query.hybrid.vectorWeight` | `0.7` | Combined with `textWeight`, then normalized to sum=1 if both set. |
| `agents.defaults.memorySearch.query.hybrid.textWeight` | `0.3` | Combined with `vectorWeight`, then normalized. |
| `agents.defaults.memorySearch.query.hybrid.candidateMultiplier` | `4` | Final candidates: `maxResults * multiplier` (clamped and capped). |

## 4) QMD Configuration

### 4.1 Sidecar runtime behavior

| Aspect | Behavior |
|---|---|
| State location | `<resolveStateDir>/agents/<agentId>/qmd/` |
| XDG override | QMD spawned with `XDG_CONFIG_HOME=<...>/xdg-config` and `XDG_CACHE_HOME=<...>/xdg-cache` |
| Collections | Default memory collections + optional `memory.qmd.paths[]`; optional sessions collection when enabled |
| Boot sync | Controlled by `memory.qmd.update.onBoot` and `waitForBootSync` |
| Periodic sync | Controlled by `memory.qmd.update.interval` |
| Embed cadence | Controlled by `memory.qmd.update.embedInterval` |
| Failure mode | QMD manager logs and built-in memory manager is used as fallback |

### 4.2 QMD defaults summary

| Setting | Default |
|---|---|
| `memory.backend` | `builtin` |
| `memory.citations` | `auto` |
| `memory.qmd.command` | `qmd` |
| `memory.qmd.includeDefaultMemory` | `true` |
| `memory.qmd.update.interval` | `5m` |
| `memory.qmd.update.debounceMs` | `15000` |
| `memory.qmd.update.onBoot` | `true` |
| `memory.qmd.update.waitForBootSync` | `false` |
| `memory.qmd.update.embedInterval` | `60m` |
| `memory.qmd.update.commandTimeoutMs` | `30000` |
| `memory.qmd.update.updateTimeoutMs` | `120000` |
| `memory.qmd.update.embedTimeoutMs` | `120000` |
| `memory.qmd.limits.maxResults` | `6` |
| `memory.qmd.limits.maxSnippetChars` | `700` |
| `memory.qmd.limits.maxInjectedChars` | `4000` |
| `memory.qmd.limits.timeoutMs` | `4000` |

## 5) Memory-LanceDB Plugin Config

### 5.1 Activation path

| Path | Type | Default | Notes |
|---|---|---|---|
| `plugins.slots.memory` | string | `"memory-core"` | Set to `"memory-lancedb"` to activate LanceDB plugin for memory slot. |
| `plugins.entries.memory-lancedb.enabled` | boolean | plugin loader default behavior | Per-plugin enable/disable. |
| `plugins.entries.memory-lancedb.config` | object | required for plugin use | Must satisfy plugin schema below. |

### 5.2 Plugin config schema (`plugins.entries.memory-lancedb.config`)

| Path | Type | Default (resolved) | Validation / rules | Description |
|---|---|---|---|---|
| `embedding` | object (required) | none | required | Embedding settings. |
| `embedding.provider` | fixed `"openai"` | `"openai"` | implied by parser | Provider is fixed to OpenAI in current plugin. |
| `embedding.apiKey` | string (required) | none | required; `${ENV}` substitution supported | OpenAI key or env placeholder like `${OPENAI_API_KEY}`. |
| `embedding.model` | `"text-embedding-3-small"\|"text-embedding-3-large"` | `"text-embedding-3-small"` | validated against known dims | Embedding model. |
| `dbPath` | string | `~/.openclaw/memory/lancedb` (or existing legacy path) | optional | LanceDB storage path. |
| `autoCapture` | boolean | `true` | optional | Auto-store memories from conversation hooks. |
| `autoRecall` | boolean | `true` | optional | Auto-inject relevant memories before model call. |

## 6) Environment Variables Affecting Memory

| Env var | Affects | Notes |
|---|---|---|
| `OPENAI_API_KEY` | Built-in OpenAI embeddings; LanceDB plugin (via `${OPENAI_API_KEY}`) | Resolved via provider auth when `memorySearch.provider=openai` or plugin config uses env interpolation. |
| `GEMINI_API_KEY` | Built-in Gemini embeddings | Resolved by provider auth for `models.providers.google` / memory embeddings. |
| `GOOGLE_API_KEY` | Built-in Gemini embeddings (special case) | Used when `memorySearch.remote.apiKey` is literally `"GOOGLE_API_KEY"`. |
| `VOYAGE_API_KEY` | Built-in Voyage embeddings | Resolved by provider auth. |
| `OPENCLAW_STATE_DIR` | Built-in memory DB path defaults; QMD state dirs | Primary state dir override. |
| `CLAWDBOT_STATE_DIR` | Same as above (legacy alias) | Legacy state dir override honored by path resolver. |
| `OPENCLAW_HOME` | Home resolution for default state paths and `~` expansion | Indirectly changes memory storage defaults. |
| `XDG_CACHE_HOME` | QMD shared-model reuse lookup | Read to locate default `qmd/models` for symlink into agent cache. |
| `LOCALAPPDATA` | Windows fallback for QMD shared-model lookup | Used when `XDG_CACHE_HOME` not set on Windows. |
| `OPENCLAW_DEBUG_MEMORY_EMBEDDINGS` | Memory embedding debug logging | Enables verbose embedding debug logs. |

## 7) Example Configurations

### 7.1 Built-in memory search + pre-compaction flush tuning

```json5
{
  agents: {
    defaults: {
      compaction: {
        reserveTokensFloor: 20000,
        memoryFlush: {
          enabled: true,
          softThresholdTokens: 4000,
          systemPrompt: "Session nearing compaction. Store durable memories now.",
          prompt: "Write lasting notes to memory/YYYY-MM-DD.md; reply NO_REPLY if nothing to store."
        }
      },
      memorySearch: {
        provider: "openai",
        model: "text-embedding-3-small",
        fallback: "none",
        query: {
          maxResults: 6,
          hybrid: { enabled: true, vectorWeight: 0.7, textWeight: 0.3, candidateMultiplier: 4 }
        }
      }
    }
  }
}
```

### 7.2 QMD backend with extra paths + session indexing

```json5
{
  memory: {
    backend: "qmd",
    citations: "auto",
    qmd: {
      command: "qmd",
      includeDefaultMemory: true,
      paths: [
        { name: "team-docs", path: "~/notes/team", pattern: "**/*.md" }
      ],
      sessions: {
        enabled: true,
        retentionDays: 14
      },
      update: {
        interval: "5m",
        debounceMs: 15000,
        onBoot: true,
        waitForBootSync: false,
        embedInterval: "60m",
        commandTimeoutMs: 30000,
        updateTimeoutMs: 120000,
        embedTimeoutMs: 120000
      },
      limits: {
        maxResults: 6,
        maxSnippetChars: 700,
        maxInjectedChars: 4000,
        timeoutMs: 4000
      },
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }]
      }
    }
  }
}
```

### 7.3 Local embeddings (built-in backend)

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "local",
        local: {
          modelPath: "hf:ggml-org/embeddinggemma-300M-GGUF/embeddinggemma-300M-Q8_0.gguf",
          modelCacheDir: "~/.cache/openclaw/models"
        },
        fallback: "none",
        store: {
          driver: "sqlite",
          path: "~/.openclaw/memory/{agentId}.sqlite",
          vector: { enabled: true }
        }
      }
    }
  }
}
```

### 7.4 Memory (LanceDB) plugin slot config

```json5
{
  plugins: {
    slots: {
      memory: "memory-lancedb"
    },
    entries: {
      "memory-lancedb": {
        enabled: true,
        config: {
          embedding: {
            apiKey: "${OPENAI_API_KEY}",
            model: "text-embedding-3-small"
          },
          dbPath: "~/.openclaw/memory/lancedb",
          autoCapture: true,
          autoRecall: true
        }
      }
    }
  }
}
```

## Notes on Type/Schema/Runtime drift

| Area | Observation |
|---|---|
| `memorySearch.provider` | `types.tools.ts` excludes `"auto"`, but runtime resolver (`agents/memory-search.ts`) uses `"auto"` when unset. |
| `memorySearch.remote.batch` defaults | `types.tools.ts` comments mention defaults that differ from runtime (`enabled` is `false` in runtime, poll interval `2000ms`). |
| `memorySearch.store.cache` | Present in `types.tools.ts`, but absent from Zod `MemorySearchSchema` and not used by runtime resolver; active cache config is top-level `memorySearch.cache`. |
