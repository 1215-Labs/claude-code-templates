# OpenClaw Plugin API Reference

## 1) OpenClawPluginApi Methods

| Method Name | Signature | Description |
|---|---|---|
| `registerTool` | `(tool: AnyAgentTool \| OpenClawPluginToolFactory, opts?: { name?: string; names?: string[]; optional?: boolean }) => void` | Registers a tool instance or tool factory. Non-function tools auto-add `tool.name`; optional tools are policy-gated at resolve time. |
| `registerHook` | `(events: string \| string[], handler: InternalHookHandler, opts?: OpenClawPluginHookOptions) => void` | Registers legacy internal hook entries (`HookEntry`) and optional runtime registration into internal hook system (`config.hooks.internal.enabled`). |
| `registerHttpHandler` | `(handler: OpenClawPluginHttpHandler) => void` | Registers a catch-all HTTP handler for plugin HTTP processing. |
| `registerHttpRoute` | `(params: { path: string; handler: OpenClawPluginHttpRouteHandler }) => void` | Registers a normalized HTTP route path; duplicate paths are rejected with diagnostics. |
| `registerChannel` | `(registration: OpenClawPluginChannelRegistration \| ChannelPlugin) => void` | Registers a channel plugin (+ optional dock). Channel id is required. |
| `registerGatewayMethod` | `(method: string, handler: GatewayRequestHandler) => void` | Registers gateway RPC method; collisions with core or existing methods are rejected. |
| `registerCli` | `(registrar: OpenClawPluginCliRegistrar, opts?: { commands?: string[] }) => void` | Registers CLI extender callback and optional declared command names for collision pre-check. |
| `registerService` | `(service: OpenClawPluginService) => void` | Registers background service (`start`, optional `stop`) for managed lifecycle start/stop. |
| `registerProvider` | `(provider: ProviderPlugin) => void` | Registers model/provider integration; provider id must be unique. |
| `registerCommand` | `(command: OpenClawPluginCommandDefinition) => void` | Registers plugin slash-like command handled before built-in/agent command flow. |
| `resolvePath` | `(input: string) => string` | Resolves user paths via `resolveUserPath`. |
| `on` | `<K extends PluginHookName>(hookName: K, handler: PluginHookHandlerMap[K], opts?: { priority?: number }) => void` | Registers typed lifecycle hooks into `registry.typedHooks` with optional priority. |

## 2) Hook Points

| Hook Event | When Fired | Handler Signature | Return Type |
|---|---|---|---|
| `before_agent_start` | Before agent start prompt/context composition (`runBeforeAgentStart`) | `(event: { prompt: string; messages?: unknown[] }, ctx: { agentId?: string; sessionKey?: string; workspaceDir?: string; messageProvider?: string })` | `PluginHookBeforeAgentStartResult \| void` (`{ systemPrompt?: string; prependContext?: string }`) |
| `agent_end` | After agent run completes (`runAgentEnd`) | `(event: { messages: unknown[]; success: boolean; error?: string; durationMs?: number }, ctx: PluginHookAgentContext)` | `void` |
| `before_compaction` | Before transcript compaction (`runBeforeCompaction`) | `(event: { messageCount: number; tokenCount?: number }, ctx: PluginHookAgentContext)` | `void` |
| `after_compaction` | After transcript compaction (`runAfterCompaction`) | `(event: { messageCount: number; tokenCount?: number; compactedCount: number }, ctx: PluginHookAgentContext)` | `void` |
| `message_received` | On inbound message received (`runMessageReceived`) | `(event: { from: string; content: string; timestamp?: number; metadata?: Record<string, unknown> }, ctx: { channelId: string; accountId?: string; conversationId?: string })` | `void` |
| `message_sending` | Before outbound message send (`runMessageSending`) | `(event: { to: string; content: string; metadata?: Record<string, unknown> }, ctx: PluginHookMessageContext)` | `PluginHookMessageSendingResult \| void` (`{ content?: string; cancel?: boolean }`) |
| `message_sent` | After outbound message send (`runMessageSent`) | `(event: { to: string; content: string; success: boolean; error?: string }, ctx: PluginHookMessageContext)` | `void` |
| `before_tool_call` | Before tool invocation (`runBeforeToolCall`) | `(event: { toolName: string; params: Record<string, unknown> }, ctx: { agentId?: string; sessionKey?: string; toolName: string })` | `PluginHookBeforeToolCallResult \| void` (`{ params?: Record<string, unknown>; block?: boolean; blockReason?: string }`) |
| `after_tool_call` | After tool invocation (`runAfterToolCall`) | `(event: { toolName: string; params: Record<string, unknown>; result?: unknown; error?: string; durationMs?: number }, ctx: PluginHookToolContext)` | `void` |
| `tool_result_persist` | Right before tool result message is appended to transcript (`runToolResultPersist`) | `(event: { toolName?: string; toolCallId?: string; message: AgentMessage; isSynthetic?: boolean }, ctx: { agentId?: string; sessionKey?: string; toolName?: string; toolCallId?: string })` | `PluginHookToolResultPersistResult \| void` (`{ message?: AgentMessage }`) |
| `session_start` | Session start (`runSessionStart`) | `(event: { sessionId: string; resumedFrom?: string }, ctx: { agentId?: string; sessionId: string })` | `void` |
| `session_end` | Session end (`runSessionEnd`) | `(event: { sessionId: string; messageCount: number; durationMs?: number }, ctx: PluginHookSessionContext)` | `void` |
| `gateway_start` | Gateway start (`runGatewayStart`) | `(event: { port: number }, ctx: { port?: number })` | `void` |
| `gateway_stop` | Gateway shutdown (`runGatewayStop`) | `(event: { reason?: string }, ctx: PluginHookGatewayContext)` | `void` |

| Hook Execution Behavior | Details |
|---|---|
| Ordering | All hooks are sorted by `priority` descending (default `0`). |
| Parallel hooks | `agent_end`, `before_compaction`, `after_compaction`, `message_received`, `message_sent`, `after_tool_call`, `session_start`, `session_end`, `gateway_start`, `gateway_stop` run in parallel (`Promise.all`). |
| Sequential/merging hooks | `before_agent_start`, `message_sending`, `before_tool_call` run sequentially; results are merged. |
| Sync-only hook | `tool_result_persist` is synchronous; Promise returns are warned/ignored. |
| Error model | By default errors are caught and logged (`catchErrors: true`). |

## 3) Tool Registration

| Aspect | Behavior |
|---|---|
| Registration API | Plugin calls `api.registerTool(toolOrFactory, opts)`; registry stores `{ pluginId, factory, names, optional, source }`. |
| Tool factory contract | `OpenClawPluginToolFactory(ctx)` returns `AnyAgentTool \| AnyAgentTool[] \| null \| undefined`. |
| Name handling | For direct tool objects, `tool.name` is auto-added. Optional `opts.name`/`opts.names` are normalized and recorded. |
| Resolution flow | `resolvePluginTools(...)` loads registry, executes each factory, flattens arrays, and collects tools. |
| Conflict checks | Blocks plugin if plugin id conflicts with core tool name; rejects duplicate tool names against existing/core tools; records diagnostics. |
| Policy integration | Optional tools only included if allowlist contains normalized tool name, plugin id, or `group:plugins`. |
| Metadata | Selected tools get WeakMap metadata `{ pluginId, optional }` via `getPluginToolMeta`. |

## 4) Service Registration

| Aspect | Behavior |
|---|---|
| Registration API | Plugin calls `api.registerService({ id, start, stop? })`. |
| Start lifecycle | `startPluginServices(...)` iterates `registry.services` and awaits each `service.start(ctx)` with `{ config, workspaceDir, stateDir: STATE_DIR, logger }`. |
| Failure handling | Start errors are logged and do not abort other services. |
| Stop lifecycle | Returned handle `stop()` stops in reverse registration order (`toReversed()`), awaiting each optional `service.stop(ctx)`. |
| Stop error handling | Stop failures are logged as warnings and continue. |

## 5) CLI Registration

| Aspect | Behavior |
|---|---|
| Registration API | Plugin calls `api.registerCli(registrar, { commands?: string[] })`. |
| Registry storage | Stored in `registry.cliRegistrars` with plugin id, callback, declared command names, source. |
| Activation point | `registerPluginCliCommands(program, cfg?)` loads plugin registry and executes each registrar. |
| Collision control | If plugin declares `commands`, overlaps with existing Commander command names cause registrar skip. |
| Async registrar behavior | Promise-returning registrars are supported; rejection logged via `.catch`. |
| Registrar context | Callback receives `{ program, config, workspaceDir, logger }`. |

## 6) Config Schema API

| Aspect | Behavior |
|---|---|
| Manifest-required schema | `openclaw.plugin.json` requires `configSchema` object; missing schema prevents plugin load (`status: error`). |
| Validation path | Loader validates `plugins.entries[pluginId].config` against manifest `configSchema` via `validateJsonSchemaValue(...)`. |
| Plugin-facing config | Validated value is exposed as `api.pluginConfig`. |
| Code-level schema type | `OpenClawPluginConfigSchema` supports `safeParse`, `parse`, `validate`, `uiHints`, `jsonSchema` (type exists for plugin code/API typing). |
| UI hints | Manifest `uiHints` are captured into registry record `configUiHints`; schema itself captured as `configJsonSchema`. |
| Default empty schema helper | `emptyPluginConfigSchema()` provides an object-only-empty validator + equivalent JSON schema. |

## 7) Plugin Slot System

| Aspect | Behavior |
|---|---|
| Slot keys | `PluginSlotKey = keyof PluginSlotsConfig`; current implemented slot mapping is only `memory`. |
| Kind-to-slot mapping | `PluginKind` currently only `"memory"`; `slotKeyForPluginKind("memory") => "memory"`. |
| Default slot selection | `defaultSlotIdForKey("memory") => "memory-core"`; normalized config defaults memory slot to this value unless explicitly set. |
| Explicit disable | `plugins.slots.memory: "none"` normalizes to `null`, disabling memory slot plugins. |
| Loader enforcement | `resolveMemorySlotDecision(...)` ensures only one memory plugin is enabled for the slot; others disabled with reason. |
| Exclusive selection utility | `applyExclusiveSlotSelection(...)` updates slot id and auto-disables same-kind plugins in config entries, returning warnings/changed flag. |
| Other slot types | None in current source; only memory slot is implemented. |

## 8) Plugin Manifest Schema (`openclaw.plugin.json`)

| Field | Required | Type | Notes |
|---|---|---|---|
| `id` | Yes | `string` | Trimmed; must be non-empty. |
| `configSchema` | Yes | `object` | Must be record/object; used for plugin config validation. |
| `kind` | No | `PluginKind` | Current value set supports `"memory"`. |
| `channels` | No | `string[]` | Normalized list of non-empty trimmed strings. |
| `providers` | No | `string[]` | Normalized list of non-empty trimmed strings. |
| `skills` | No | `string[]` | Normalized list of non-empty trimmed strings. |
| `name` | No | `string` | Trimmed. |
| `description` | No | `string` | Trimmed. |
| `version` | No | `string` | Trimmed. |
| `uiHints` | No | `Record<string, PluginConfigUiHint>` | Optional UI metadata for config fields. |

| Manifest Loading Rules | Behavior |
|---|---|
| Filename | Resolved as `openclaw.plugin.json` (`PLUGIN_MANIFEST_FILENAME`). |
| Parse errors | Missing file, invalid JSON, non-object root, missing `id`, or missing `configSchema` return load errors. |
| Discovery integration | Manifest records are combined with discovery candidate metadata (origin/source/package labels). |
| Duplicate ids | Duplicate manifest ids are diagnosed as warnings; later candidates may be overridden by origin resolution in loader. |
