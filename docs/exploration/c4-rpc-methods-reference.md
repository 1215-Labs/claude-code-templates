# OpenClaw Gateway RPC Method Catalog

Derived from:
- `references/openclaw/src/gateway/server-methods-list.ts`
- `references/openclaw/src/gateway/server-methods.ts`
- `references/openclaw/src/gateway/protocol/index.ts`
- Handler modules under `references/openclaw/src/gateway/server-methods/*.ts`

Notes:
- `server-methods-list.ts` advertises base methods and channel plugin methods.
- `server.impl.ts` also injects `exec.approval.*` plus plugin-defined gateway handlers at runtime.
- Parameter names below use protocol schema type names where available (for example `SessionsPatchParams`).

| Method Name | Category | Parameters | Description |
|---|---|---|---|
| **Connection** ||||
| `connect` | connection | `ConnectParams` (handshake frame; not handled via normal request path) | Initial WebSocket handshake request; normal handler returns invalid when called after handshake. |
| **Health & System** ||||
| `health` | health-system | `{ probe?: boolean }` | Returns gateway health snapshot; may use cache unless probing. |
| `status` | health-system | none | Returns high-level runtime status summary. |
| `logs.tail` | health-system | `LogsTailParams` | Returns rolling log tail with cursor/limit semantics. |
| `last-heartbeat` | health-system | none | Returns last emitted heartbeat payload. |
| `set-heartbeats` | health-system | `{ enabled: boolean }` | Enables or disables heartbeat runner. |
| `system-presence` | health-system | none | Returns current system presence entries. |
| `system-event` | health-system | `{ text: string, deviceId?, instanceId?, host?, ip?, mode?, version?, platform?, deviceFamily?, modelIdentifier?, lastInputSeconds?, reason?, roles?: string[], scopes?: string[], tags?: string[] }` | Ingests a system event/presence update and broadcasts presence changes. |
| **Agents** ||||
| `agent` | agents | `AgentParams` | Starts an agent run (deduped by idempotency key) and manages delivery/session context. |
| `agent.identity.get` | agents | `AgentIdentityParams` | Resolves assistant identity metadata for an agent/session. |
| `agent.wait` | agents | `AgentWaitParams` | Waits for an agent run to finish or timeout. |
| `agents.list` | agents | `AgentsListParams` | Lists configured agents for gateway UI/API. |
| `agents.create` | agents | `AgentsCreateParams` | Creates a new agent config/workspace entry. |
| `agents.update` | agents | `AgentsUpdateParams` | Updates agent metadata/config fields. |
| `agents.delete` | agents | `AgentsDeleteParams` | Deletes an agent and optionally related files. |
| `agents.files.list` | agents | `AgentsFilesListParams` | Lists managed bootstrap/memory files for an agent workspace. |
| `agents.files.get` | agents | `AgentsFilesGetParams` | Reads a managed agent workspace file. |
| `agents.files.set` | agents | `AgentsFilesSetParams` | Writes a managed agent workspace file. |
| **Messaging & Chat** ||||
| `send` | messaging | `SendParams` | Sends a direct outbound channel message. |
| `poll` | messaging | `PollParams` | Sends a poll via channel outbound integration. |
| `wake` | messaging | `WakeParams` | Triggers wake flow for runtime/session. |
| `chat.history` | messaging | `ChatHistoryParams` | Returns sanitized session chat history. |
| `chat.send` | messaging | `ChatSendParams` | Starts/streams a chat run tied to a session key. |
| `chat.abort` | messaging | `ChatAbortParams` | Aborts in-flight chat run(s). |
| `chat.inject` | messaging | `ChatInjectParams` | Injects assistant text into transcript/session state. |
| `browser.request` | messaging | `{ method: "GET"|"POST"|"DELETE", path: string, query?: object, body?: unknown, timeoutMs?: number }` | Proxies browser-control requests to node/browser control service. |
| **Channels & Web Login** ||||
| `channels.status` | channels | `ChannelsStatusParams` | Returns channel/account status, optionally probing providers. |
| `channels.logout` | channels | `ChannelsLogoutParams` | Logs out a channel account and stops channel runtime. |
| `web.login.start` | channels | `WebLoginStartParams` | Starts QR/web login flow for provider exposing web-login methods. |
| `web.login.wait` | channels | `WebLoginWaitParams` | Waits for QR/web login completion and starts channel when connected. |
| **Config, Wizard & Update** ||||
| `config.get` | config | `ConfigGetParams` | Returns redacted config snapshot and metadata. |
| `config.schema` | config | `ConfigSchemaParams` | Returns generated config JSON schema (core + plugin/channel schema). |
| `config.set` | config | `ConfigSetParams` | Replaces config using provided raw config text (base-hash guarded). |
| `config.patch` | config | `ConfigPatchParams` | Applies merge-patch update to config (base-hash guarded). |
| `config.apply` | config | `ConfigApplyParams` | Applies/writes config and restart-sentinel behavior for runtime changes. |
| `wizard.start` | config | `WizardStartParams` | Starts interactive setup wizard session. |
| `wizard.next` | config | `WizardNextParams` | Advances wizard, optionally submitting step answer. |
| `wizard.cancel` | config | `WizardCancelParams` | Cancels active wizard session. |
| `wizard.status` | config | `WizardStatusParams` | Gets current wizard session status. |
| `update.run` | config | `UpdateRunParams` | Triggers update workflow execution. |
| **Models & Skills** ||||
| `models.list` | models-skills | `ModelsListParams` | Returns gateway model catalog. |
| `skills.status` | models-skills | `SkillsStatusParams` | Returns installed skill status snapshot. |
| `skills.bins` | models-skills | `SkillsBinsParams` | Returns skill binary/tool information. |
| `skills.install` | models-skills | `SkillsInstallParams` | Installs a skill package/source. |
| `skills.update` | models-skills | `SkillsUpdateParams` | Updates an installed skill package/source. |
| **Sessions & Usage** ||||
| `sessions.list` | sessions-usage | `SessionsListParams` | Lists sessions from session stores with filtering/paging. |
| `sessions.preview` | sessions-usage | `SessionsPreviewParams` | Returns short transcript previews for session keys. |
| `sessions.resolve` | sessions-usage | `SessionsResolveParams` | Resolves canonical session key from key/sessionId/label inputs. |
| `sessions.patch` | sessions-usage | `SessionsPatchParams` | Applies patch updates to session entry metadata/settings. |
| `sessions.reset` | sessions-usage | `SessionsResetParams` | Resets session with new sessionId while preserving selected metadata. |
| `sessions.delete` | sessions-usage | `SessionsDeleteParams` | Deletes session entry and archives transcript when present. |
| `sessions.compact` | sessions-usage | `SessionsCompactParams` | Compacts transcript/session history. |
| `usage.status` | sessions-usage | none | Returns provider usage status summary. |
| `usage.cost` | sessions-usage | `{ startDate?: string, endDate?: string, days?: number }` | Returns aggregated cost summary for requested date range. |
| `sessions.usage` | sessions-usage | `SessionsUsageParams` | Returns per-session usage/cost analytics and aggregates. |
| `sessions.usage.timeseries` | sessions-usage | `{ key: string }` | Returns session usage timeseries for a resolved session key. |
| `sessions.usage.logs` | sessions-usage | `{ key: string, limit?: number }` | Returns detailed session usage log entries. |
| **Cron** ||||
| `cron.list` | cron | `CronListParams` | Lists configured cron jobs. |
| `cron.status` | cron | `CronStatusParams` | Returns cron subsystem status. |
| `cron.add` | cron | `CronAddParams` | Adds a cron job. |
| `cron.update` | cron | `CronUpdateParams` | Updates existing cron job by id/jobId. |
| `cron.remove` | cron | `CronRemoveParams` | Removes cron job by id/jobId. |
| `cron.run` | cron | `CronRunParams` | Executes cron job immediately (`force`/`due` mode). |
| `cron.runs` | cron | `CronRunsParams` | Returns run history entries for a cron job. |
| **Nodes & Devices** ||||
| `node.pair.request` | nodes-devices | `NodePairRequestParams` | Requests a node pairing token/challenge flow. |
| `node.pair.list` | nodes-devices | `NodePairListParams` | Lists pending/paired nodes. |
| `node.pair.approve` | nodes-devices | `NodePairApproveParams` | Approves pending node pairing request. |
| `node.pair.reject` | nodes-devices | `NodePairRejectParams` | Rejects pending node pairing request. |
| `node.pair.verify` | nodes-devices | `NodePairVerifyParams` | Verifies node pairing credentials/challenge. |
| `node.rename` | nodes-devices | `NodeRenameParams` | Updates node display name/alias. |
| `node.list` | nodes-devices | `NodeListParams` | Lists nodes with connection/pairing details. |
| `node.describe` | nodes-devices | `NodeDescribeParams` | Returns detail for one node. |
| `node.invoke` | nodes-devices | `NodeInvokeParams` | Sends command invocation to a connected node. |
| `node.invoke.result` | nodes-devices | `NodeInvokeResultParams` | Node role callback for invocation result payload. |
| `node.event` | nodes-devices | `NodeEventParams` | Node role callback for node-originated events. |
| `device.pair.list` | nodes-devices | `DevicePairListParams` | Lists pending/paired device-auth requests. |
| `device.pair.approve` | nodes-devices | `DevicePairApproveParams` | Approves pending device pairing. |
| `device.pair.reject` | nodes-devices | `DevicePairRejectParams` | Rejects pending device pairing. |
| `device.token.rotate` | nodes-devices | `DeviceTokenRotateParams` | Rotates/creates a device token for role/scopes. |
| `device.token.revoke` | nodes-devices | `DeviceTokenRevokeParams` | Revokes a device token for role. |
| **Approvals** ||||
| `exec.approvals.get` | approvals | `ExecApprovalsGetParams` | Reads local exec approvals policy snapshot/hash. |
| `exec.approvals.set` | approvals | `ExecApprovalsSetParams` | Writes local exec approvals policy (base-hash guarded). |
| `exec.approvals.node.get` | approvals | `ExecApprovalsNodeGetParams` | Reads exec approvals policy from a remote node. |
| `exec.approvals.node.set` | approvals | `ExecApprovalsNodeSetParams` | Writes exec approvals policy on a remote node. |
| `exec.approval.request` | approvals | `ExecApprovalRequestParams` | Creates pending one-off exec approval request and waits for decision. |
| `exec.approval.resolve` | approvals | `ExecApprovalResolveParams` | Resolves pending exec approval (`allow-once`, `allow-always`, `deny`). |
| **Talk, TTS & Voicewake** ||||
| `talk.mode` | voice-tts | `TalkModeParams` | Broadcasts talk mode enable/phase state. |
| `tts.status` | voice-tts | none | Returns TTS status/provider/prefs capabilities. |
| `tts.providers` | voice-tts | none | Returns available TTS providers, models, voices, active provider. |
| `tts.enable` | voice-tts | none | Enables TTS output. |
| `tts.disable` | voice-tts | none | Disables TTS output. |
| `tts.convert` | voice-tts | `{ text: string, channel?: string }` | Converts text to speech and returns generated audio metadata/path. |
| `tts.setProvider` | voice-tts | `{ provider: "openai"|"elevenlabs"|"edge" }` | Sets active TTS provider. |
| `voicewake.get` | voice-tts | none | Returns voice wake trigger configuration. |
| `voicewake.set` | voice-tts | `{ triggers: string[] }` | Updates voice wake triggers and broadcasts change event. |
| **Plugins (Dynamic)** ||||
| `<plugin-handler-method>` | plugins | plugin-defined | Runtime plugin gateway handler method from `pluginRegistry.gatewayHandlers` (merged via `extraHandlers`). |
| `<channel-plugin-method>` | plugins | plugin-defined | Channel plugin method(s) from `listChannelPlugins().gatewayMethods`. |

## Method Count Summary

| Category | Method Count |
|---|---:|
| `connection` | 1 |
| `health-system` | 7 |
| `agents` | 10 |
| `messaging` | 8 |
| `channels` | 4 |
| `config` | 10 |
| `models-skills` | 5 |
| `sessions-usage` | 12 |
| `cron` | 7 |
| `nodes-devices` | 16 |
| `approvals` | 6 |
| `voice-tts` | 9 |
| `plugins` | dynamic |
| **Total explicit methods (non-dynamic)** | **95** |
