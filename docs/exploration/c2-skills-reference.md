# OpenClaw Skills System Reference

## 1) Skill Types

| Type | Source | Description |
| --- | --- | --- |
| `bundled` | `references/openclaw/skills/*` loaded via `loadSkillsFromDir({ source: "openclaw-bundled" })` in `src/agents/skills/workspace.ts` | Built-in skills shipped with OpenClaw. Bundled directory is resolved by `resolveBundledSkillsDir()` (env override, app sibling `skills/`, or package-root lookup). |
| `managed` | `~/.openclaw/skills` (`CONFIG_DIR/skills`) loaded with source `openclaw-managed` | User-managed shared skills for all agents on a machine. |
| `workspace` | `<workspace>/skills` loaded with source `openclaw-workspace` | Highest-precedence, per-workspace (often per-agent) skills. |
| `plugin` | Paths from enabled plugins (`openclaw.plugin.json` `skills` entries) via `resolvePluginSkillDirs()` | Plugin-provided skill folders. Internally merged into `extraDirs` and loaded with source label `openclaw-extra`. |
| `extra` | `config.skills.load.extraDirs[]` loaded with source `openclaw-extra` | Additional user-configured skill packs. Lowest precedence in resolution. |

## 2) YAML Frontmatter Schema

| Field | Type | Description |
| --- | --- | --- |
| `name` | `string` | Skill name (also key used in merge/conflict resolution). |
| `description` | `string` | Skill summary for prompt/commands/UI status. |
| `metadata` | `string` (JSON5 payload) | Parsed by `resolveOpenClawMetadata()`. Expected shape: object containing `openclaw` key. |
| `homepage` | `string` | Optional website URL surfaced in skill status/UI. |
| `website` | `string` | Alternate website key accepted in status fallback. |
| `url` | `string` | Alternate website key accepted in status fallback. |
| `emoji` | `string` | Optional emoji fallback when `metadata.openclaw.emoji` is absent. |
| `user-invocable` | `boolean-like string` | Parsed via `parseBooleanValue`; default `true`. Controls whether slash/native skill command is registered. |
| `disable-model-invocation` | `boolean-like string` | Parsed via `parseBooleanValue`; default `false`. If `true`, skill is excluded from model prompt but can remain user-invocable. |
| `command-dispatch` / `command_dispatch` | `string` | If `tool`, skill command bypasses model and calls a named tool directly. |
| `command-tool` / `command_tool` | `string` | Tool name used when `command-dispatch: tool`. |
| `command-arg-mode` / `command_arg_mode` | `string` | Dispatch arg mode. Current supported value: `raw` (default fallback). |

| `metadata.openclaw` Field | Type | Description |
| --- | --- | --- |
| `always` | `boolean` | Force-eligible skill (bypasses normal requirement checks). |
| `skillKey` | `string` | Config key override for `skills.entries.<key>`. |
| `primaryEnv` | `string` | Env var bound to `skills.entries.<key>.apiKey`. |
| `emoji` | `string` | UI emoji. |
| `homepage` | `string` | UI homepage URL. |
| `os` | `string[]` | Allowed runtime platforms (`darwin`, `linux`, `win32`, etc.). |
| `requires.bins` | `string[]` | All binaries must be present (host PATH or remote eligibility hook). |
| `requires.anyBins` | `string[]` | At least one binary must be present. |
| `requires.env` | `string[]` | Required env vars (process env or `skills.entries.*.env` / `apiKey` mapping). |
| `requires.config` | `string[]` | Required truthy config paths (`dot.path`). |
| `install` | `SkillInstallSpec[]` | Optional installer options surfaced by skills status/install flow. |

| `SkillInstallSpec` Field | Type | Description |
| --- | --- | --- |
| `kind` | `"brew" \| "node" \| "go" \| "uv" \| "download"` | Installer kind. |
| `id` | `string` | Stable install option ID (fallback: `<kind>-<index>`). |
| `label` | `string` | UI label for installer action. |
| `bins` | `string[]` | Binaries expected after install. |
| `os` | `string[]` | Installer OS filter. |
| `formula` | `string` | Brew formula (brew kind). |
| `package` | `string` | NPM/UV package (node/uv kinds). |
| `module` | `string` | Go module (`go install`). |
| `url` | `string` | Download URL (download kind). |
| `archive` | `string` | Explicit archive type (`tar.gz`, `tar.bz2`, `zip`). |
| `extract` | `boolean` | Whether to extract download artifact. |
| `stripComponents` | `number` | Tar extraction strip components value. |
| `targetDir` | `string` | Download target directory (default `~/.openclaw/tools/<skillKey>`). |

## 3) Skill Discovery & Resolution

| Stage | Behavior |
| --- | --- |
| Directory discovery | `workspace.ts` resolves: bundled dir (`resolveBundledSkillsDir()`), managed dir (`CONFIG_DIR/skills`), workspace dir (`<workspace>/skills`), extra dirs (`config.skills.load.extraDirs`), plugin dirs (`resolvePluginSkillDirs()`). |
| Plugin integration | Plugin dirs are appended to `extraDirs` (`mergedExtraDirs = [...extraDirs, ...pluginSkillDirs]`) and loaded as `openclaw-extra`. |
| Loading | Each directory is loaded with `loadSkillsFromDir({ dir, source })`. |
| Merge key | Skills are merged by `skill.name` in a `Map<string, Skill>`. Later writes override earlier entries. |
| Precedence order | Merge order is `extra` -> `bundled` -> `managed` -> `workspace`; therefore effective priority is `workspace > managed > bundled > extra/plugin`. |
| Eligibility filtering | `shouldIncludeSkill()` enforces config disabled state, bundled allowlist, OS, required bins/anyBins/env/config, with `always: true` override. |
| Prompt inclusion | Prompt builders exclude skills where `disable-model-invocation === true`; all eligible skills may still appear in status/command paths. |
| User command inclusion | Command spec builder excludes skills where `user-invocable === false`; command names are sanitized/deduped/reserved-name-safe. |
| Watch/refresh | `refresh.ts` watches workspace/managed/extra/plugin dirs and bumps snapshot version for hot reload behavior. |

## 4) Bundled Skills Catalog

| Directory | Frontmatter `name` | Description |
| --- | --- | --- |
| 1password | 1password | Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single or multi-account), or reading/injecting/running secrets via op. |
| apple-notes | apple-notes | Manage Apple Notes via the `memo` CLI on macOS (create, view, edit, delete, search, move, and export notes). Use when a user asks OpenClaw to add a note, list notes, search notes, or manage note folders. |
| apple-reminders | apple-reminders | Manage Apple Reminders via the `remindctl` CLI on macOS (list, add, edit, complete, delete). Supports lists, date filters, and JSON/plain output. |
| bear-notes | bear-notes | Create, search, and manage Bear notes via grizzly CLI. |
| blogwatcher | blogwatcher | Monitor blogs and RSS/Atom feeds for updates using the blogwatcher CLI. |
| blucli | blucli | BluOS CLI (blu) for discovery, playback, grouping, and volume. |
| bluebubbles | bluebubbles | Use when you need to send or manage iMessages via BlueBubbles (recommended iMessage integration). Calls go through the generic message tool with channel="bluebubbles". |
| camsnap | camsnap | Capture frames or clips from RTSP/ONVIF cameras. |
| canvas |  | No YAML frontmatter in current bundled file; markdown-only skill document. |
| clawhub | clawhub | Use the ClawHub CLI to search, install, update, and publish agent skills from clawhub.com. Use when you need to fetch new skills on the fly, sync installed skills to latest or a specific version, or publish new/updated skill folders with the npm-installed clawhub CLI. |
| coding-agent | coding-agent | Run Codex CLI, Claude Code, OpenCode, or Pi Coding Agent via background process for programmatic control. |
| discord | discord | Use when you need to control Discord from OpenClaw via the discord tool: send messages, react, post or upload stickers, upload emojis, run polls, manage threads/pins/search, create/edit/delete channels and categories, fetch permissions or member/role/channel info, set bot presence/activity, or handle moderation actions in Discord DMs or channels. |
| eightctl | eightctl | Control Eight Sleep pods (status, temperature, alarms, schedules). |
| food-order | food-order | Reorder Foodora orders + track ETA/status with ordercli. Never confirm without explicit user approval. Triggers: order food, reorder, track ETA. |
| gemini | gemini | Gemini CLI for one-shot Q&A, summaries, and generation. |
| gifgrep | gifgrep | Search GIF providers with CLI/TUI, download results, and extract stills/sheets. |
| github | github | "Interact with GitHub using the `gh` CLI. Use `gh issue`, `gh pr`, `gh run`, and `gh api` for issues, PRs, CI runs, and advanced queries." |
| gog | gog | Google Workspace CLI for Gmail, Calendar, Drive, Contacts, Sheets, and Docs. |
| goplaces | goplaces | Query Google Places API (New) via the goplaces CLI for text search, place details, resolve, and reviews. Use for human-friendly place lookup or JSON output for scripts. |
| healthcheck | healthcheck | Host security hardening and risk-tolerance configuration for OpenClaw deployments. Use when a user asks for security audits, firewall/SSH/update hardening, risk posture, exposure review, OpenClaw cron scheduling for periodic checks, or version status checks on a machine running OpenClaw (laptop, workstation, Pi, VPS). |
| himalaya | himalaya | "CLI to manage emails via IMAP/SMTP. Use `himalaya` to list, read, write, reply, forward, search, and organize emails from the terminal. Supports multiple accounts and message composition with MML (MIME Meta Language)." |
| imsg | imsg | iMessage/SMS CLI for listing chats, history, watch, and sending. |
| local-places | local-places | Search for places (restaurants, cafes, etc.) via Google Places API proxy on localhost. |
| mcporter | mcporter | Use the mcporter CLI to list, configure, auth, and call MCP servers/tools directly (HTTP or stdio), including ad-hoc servers, config edits, and CLI/type generation. |
| model-usage | model-usage | Use CodexBar CLI local cost usage to summarize per-model usage for Codex or Claude, including the current (most recent) model or a full model breakdown. Trigger when asked for model-level usage/cost data from codexbar, or when you need a scriptable per-model summary from codexbar cost JSON. |
| nano-banana-pro | nano-banana-pro | Generate or edit images via Gemini 3 Pro Image (Nano Banana Pro). |
| nano-pdf | nano-pdf | Edit PDFs with natural-language instructions using the nano-pdf CLI. |
| notion | notion | Notion API for creating and managing pages, databases, and blocks. |
| obsidian | obsidian | Work with Obsidian vaults (plain Markdown notes) and automate via obsidian-cli. |
| openai-image-gen | openai-image-gen | Batch-generate images via OpenAI Images API. Random prompt sampler + `index.html` gallery. |
| openai-whisper | openai-whisper | Local speech-to-text with the Whisper CLI (no API key). |
| openai-whisper-api | openai-whisper-api | Transcribe audio via OpenAI Audio Transcriptions API (Whisper). |
| openhue | openhue | Control Philips Hue lights/scenes via the OpenHue CLI. |
| oracle | oracle | Best practices for using the oracle CLI (prompt + file bundling, engines, sessions, and file attachment patterns). |
| ordercli | ordercli | Foodora-only CLI for checking past orders and active order status (Deliveroo WIP). |
| peekaboo | peekaboo | Capture and automate macOS UI with the Peekaboo CLI. |
| sag | sag | ElevenLabs text-to-speech with mac-style say UX. |
| session-logs | session-logs | Search and analyze your own session logs (older/parent conversations) using jq. |
| sherpa-onnx-tts | sherpa-onnx-tts | Local text-to-speech via sherpa-onnx (offline, no cloud) |
| skill-creator | skill-creator | Create or update AgentSkills. Use when designing, structuring, or packaging skills with scripts, references, and assets. |
| slack | slack | Use when you need to control Slack from OpenClaw via the slack tool, including reacting to messages or pinning/unpinning items in Slack channels or DMs. |
| songsee | songsee | Generate spectrograms and feature-panel visualizations from audio with the songsee CLI. |
| sonoscli | sonoscli | Control Sonos speakers (discover/status/play/volume/group). |
| spotify-player | spotify-player | Terminal Spotify playback/search via spogo (preferred) or spotify_player. |
| summarize | summarize | Summarize or extract text/transcripts from URLs, podcasts, and local files (great fallback for "transcribe this YouTube/video"). |
| things-mac | things-mac | Manage Things 3 via the `things` CLI on macOS (add/update projects+todos via URL scheme; read/search/list from the local Things database). Use when a user asks OpenClaw to add a task to Things, list inbox/today/upcoming, search tasks, or inspect projects/areas/tags. |
| tmux | tmux | Remote-control tmux sessions for interactive CLIs by sending keystrokes and scraping pane output. |
| trello | trello | Manage Trello boards, lists, and cards via the Trello REST API. |
| video-frames | video-frames | Extract frames or short clips from videos using ffmpeg. |
| voice-call | voice-call | Start voice calls via the OpenClaw voice-call plugin. |
| wacli | wacli | Send WhatsApp messages to other people or search/sync WhatsApp history via the wacli CLI (not for normal user chats). |
| weather | weather | Get current weather and forecasts (no API key required). |

## 5) Skill-to-Tool Adapter

| Layer | Mechanism | Result |
| --- | --- | --- |
| Skill -> model behavior | `buildWorkspaceSkillSnapshot()` / `buildWorkspaceSkillsPrompt()` formats eligible skills into system prompt text via `formatSkillsForPrompt(...)` | Skills primarily influence model behavior by prompt injection, not by adding new low-level runtime tools. |
| Skill -> command surface | `buildWorkspaceSkillCommandSpecs()` creates command specs for user-invocable skills (`name`, `description`, optional `dispatch`) | Skills become slash/native commands in chat providers (`/skill-name`). |
| Command -> direct tool execution | If frontmatter sets `command-dispatch: tool` and `command-tool: <toolName>`, auto-reply handler resolves tool from `createOpenClawTools(...)` and executes it directly with `{ command, commandName, skillName }` | Deterministic command routing bypassing model turn for that command. |
| OpenClaw tools -> PI ToolDefinition | `toToolDefinitions()` in `pi-tool-definition-adapter.ts` wraps each `AnyAgentTool` into PI `ToolDefinition` (`name`, `description`, `parameters`, guarded `execute`) | Unified tool schema for PI runner plus normalized error handling. |
| Client-hosted tools -> PI ToolDefinition | `toClientToolDefinitions()` wraps client tools and returns pending results after optional `beforeToolCall` hook | Tool calls can be delegated to external client executors while preserving tool definition compatibility. |

## 6) Skill Installation

| Operation | Implemented by | Behavior |
| --- | --- | --- |
| Install/remove/update skill folders (managed/workspace content) | ClawHub CLI (`clawhub install`, `clawhub update`, `clawhub sync`) | OpenClaw core references ClawHub for skill package lifecycle. ClawHub typically installs into `./skills` (workspace skills), while shared skills can live in `~/.openclaw/skills`. |
| Load managed skills | `loadSkillEntries()` | Reads managed folder from `CONFIG_DIR/skills` (`~/.openclaw/skills`) as `openclaw-managed` source. |
| Remove managed skill | Filesystem / external tooling (e.g., ClawHub/manual deletion) | No dedicated core `openclaw skills remove` API in these agent modules; skill disappears on next load/watch refresh when folder is removed. |
| Install skill dependencies (not skill package itself) | `installSkill()` in `src/agents/skills-install.ts` via gateway method `skills.install` | Executes installer specs from `metadata.openclaw.install` (`brew/node/go/uv/download`), with safety scan warnings and platform filtering. |
| Watch-based refresh after install/remove | `ensureSkillsWatcher()` (`src/agents/skills/refresh.ts`) | Watches workspace/managed/extra/plugin dirs and bumps snapshot version so new/removed skills are picked up. |

