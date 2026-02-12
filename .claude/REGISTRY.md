# Claude Components Registry

Central index of all .claude components for quick discovery.

## Quick Lookup

| Task | Use |
|------|-----|
| New to project | `/onboarding` |
| Quick context | `/quick-prime` |
| Deep dive into area | `/deep-prime "area" "focus"` |
| Review code | `/code-review` or `code-reviewer` agent |
| Debug issue | `/rca "error"` or `debugger` agent |
| Sync with reference | `/sync-reference` |
| Check types | `type-checker` agent |
| Map dependencies | `dependency-analyzer` agent |
| Find patterns | `codebase-analyst` agent |
| Create tests | `test-automator` agent |
| Browser automation | `agent-browser` skill |
| Sandbox execution | `agent-sandboxes` skill |
| Fork terminal | `fork-terminal` skill |
| Orchestrate tasks | `/orchestrate "task"` |
| Delegate to Codex | `/codex "task"` or `codex-delegator` agent |
| Delegate to Gemini | `/gemini "task"` or `gemini-delegator` agent |
| Spawn agent team | `/spawn-team "task"` |
| Evaluate a skill/plugin | `skill-evaluator` skill |
| Equip a repo with components | `/repo-equip "/path/to/repo"` |
| Distill eval into components | `/reference-distill "eval-name"` |
| Build UV hooks | `uv-hook-template` skill |
| View context usage in status line | `status-line-context` hook (Notification) |
| Optimize a repo (deep) | `/repo-optimize "/path/to/repo"` |
| Generate a new agent | `meta-agent` agent |
| Skill priorities (auto) | `skill-router` skill (SessionStart) |
| Remember a fact | `/remember "fact"` |
| Forget a fact | `/forget "term"` |
| Memory status/search | `/memory "status"` |
| n8n workflows | n8n-* skills |
| Mac health check | `/mac-health` |
| Mac snapshot diff | `/mac-diff` |
| Mac snapshot/status | `/mac-status` |
| Mac config discovery | `/mac-discover` |
| Mac safe restore | `/mac-restore "latest"` |
| Mac weekly review | `/mac-status "weekly"` |
| cbass service status | `/cbass-status` |
| cbass log analysis | `/cbass-logs "service"` |
| cbass deploy | `/cbass-deploy "gpu-nvidia"` |
| Obsidian VPS status | `/obsidian-status` |
| Obsidian service health | `/obsidian-health "service"` |
| Obsidian restart service | `/obsidian-restart "service"` |
| Obsidian service logs | `/obsidian-logs "service"` |
| Obsidian env validation | `/obsidian-env-check` |
| Obsidian Caddy reload | `/obsidian-caddy-reload` |
| Obsidian vault sync | `/obsidian-vault-sync "push"` |
| Obsidian deploy | `/obsidian-deploy "obsidian-agent"` |

## By Category

### Analysis & Exploration
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `codebase-analyst` | Pattern discovery, conventions |
| Agent | `dependency-analyzer` | Map code dependencies |
| Agent | `lsp-navigator` | LSP-based navigation |
| Agent | `context-manager` | Track context across sessions |
| Command | `/quick-prime` | Fast 4-point context |
| Command | `/deep-prime` | Deep area analysis |
| Command | `/sync-reference` | Compare against claude-code reference |
| Skill | `lsp-symbol-navigation` | Symbol lookup patterns |
| Skill | `lsp-dependency-analysis` | Dependency mapping |

### Code Quality
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `code-reviewer` | Quality, security review |
| Agent | `type-checker` | Type safety verification |
| Agent | `test-automator` | Test creation |
| Command | `/code-review` | Comprehensive review + report |
| Command | `/ui-review` | UI consistency check |
| Skill | `lsp-type-safety-check` | Type validation patterns |
| Hook | `lsp-type-validator` | Pre-commit type check |
| Hook | `ruff-validator` | PostToolUse Python lint check (blocks on ruff failures) |
| Hook | `ty-validator` | PostToolUse Python type check (blocks on ty failures) |
| Hook | `dangerous-command-blocker` | PreToolUse guard for dangerous `rm -rf` and `.env` access |

### Debugging
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `debugger` | Root cause analysis |
| Command | `/rca` | Error investigation |
| Hook | `lsp-reference-checker` | Reference impact warning |

### Session Management & Memory
| Type | Component | Purpose |
|------|-----------|---------|
| Hook | `session-init` | Initialize session context |
| Hook | `memory-loader` | Load persistent memory into context on session start |
| Hook | `skill-router-loader` | Inject skill priorities and enforcement at session start |
| Hook | `status-line-context` | Notification status line: model, context usage progress bar, percent used, tokens left, session ID |
| Skill | `skill-router` | Proactive skill invocation engine with 1% threshold |
| Hook | `memory-distill` | Create session log stub on session end |
| Hook | `uncommitted-check` | Warn about uncommitted/unpushed changes on stop |
| Hook | `security-guidance` | Scan edits for security anti-patterns (PreToolUse prompt) |
| Hook | `subagent-verify` | Verify subagent completed its task (SubagentStop prompt) |
| Hook | `precompact-guard` | Skip memory flush if one happened within 60s cooldown |
| Hook | `memory-flush` | Flush unsaved memories to disk before compaction (PreCompact prompt) |
| Util | `memory-search.py` | SQLite FTS5 ranked search sidecar for memory files |
| Command | `/remember` | Store facts, preferences, decisions in memory |
| Command | `/forget` | Remove entries from memory |
| Command | `/memory` | Status, search, init, prune memory |
| Util | `memory.py` | Core memory functions (load, classify, secrets) |

### Onboarding
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/onboarding` | Full interactive intro |
| Command | `/quick-prime` | Quick refresher |
| Command | `/deep-prime` | Before working on area |

### n8n Development
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `n8n-code-javascript` | JS in Code nodes |
| Skill | `n8n-code-python` | Python in Code nodes |
| Skill | `n8n-expression-syntax` | Expression patterns |
| Skill | `n8n-mcp-tools-expert` | MCP tool usage |
| Skill | `n8n-node-configuration` | Node setup |
| Skill | `n8n-validation-expert` | Validation errors |
| Skill | `n8n-workflow-patterns` | Workflow architecture |
| Agent | `n8n-mcp-tester` | n8n MCP testing |

### Mac Management
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/mac-health` | Health check triage with remediation guidance |
| Command | `/mac-diff` | Snapshot diff with change interpretation |
| Command | `/mac-status` | Snapshot management and weekly reviews |
| Command | `/mac-discover` | Find untracked config, apps, and domains |
| Command | `/mac-restore` | Safe restore with validation and confirmation |
| Skill | `mac-manage-context` | Shared knowledge base (paths, glossaries, formats) |

### cbass (Self-Hosted AI Stack)
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/cbass-status` | Service status with AI health interpretation |
| Command | `/cbass-logs` | Log analysis with AI error interpretation |
| Command | `/cbass-deploy` | Guided deployment with pre-flight checks |
| Skill | `cbass-context` | Shared knowledge base (services, profiles, domains, glossary) |

### Obsidian Ecosystem Hub (VPS Deployment Stack)
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/obsidian-status` | Show all 16 Docker service statuses + Caddy health |
| Command | `/obsidian-health` | Deep health check with endpoint testing |
| Command | `/obsidian-restart` | Restart service(s) with pre-flight + post-restart verification |
| Command | `/obsidian-logs` | View and analyze service logs with error interpretation |
| Command | `/obsidian-env-check` | Validate required environment variables in .env |
| Command | `/obsidian-caddy-reload` | Reload Caddy reverse proxy configuration |
| Command | `/obsidian-vault-sync` | Sync Obsidian vault between local filesystem and MinIO S3 |
| Command | `/obsidian-deploy` | Guided deployment with pre-flight checks, rsync, deploy.sh, health verify |
| Skill | `obsidian-context` | Shared knowledge base (16 services, 8 domains, MinIO buckets, glossary) |

### Browser, Terminal & Sandbox Automation
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `agent-browser` | Vercel agent-browser CLI for headless automation |
| Skill | `agent-sandboxes` | E2B sandbox CLI for isolated code execution in agent workflows |
| Skill | `fork-terminal` | Fork terminal to new window with Claude/Codex/Gemini (dual-mode) |

### Orchestration
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `multi-model-orchestration` | Delegate tasks across Gemini/Codex via forked terminals |
| Skill | `skill-evaluator` | Evaluate external skills/plugins before adoption (parallel agents) |
| Skill | `repo-equip-engine` | Matching heuristics and templates for automated repo equipment |
| Skill | `reference-distill` | Evaluation-to-integration engine: parse evals, extract, adapt, track provenance |
| Skill | `repo-optimize-engine` | Freshness scoring, task graph generation for multi-model repo optimization |
| Skill | `skill-router` | Proactive skill invocation with per-repo priority lists |
| Command | `/orchestrate` | Quick orchestration via forked terminals |
| Command | `/reference-distill` | Extract and integrate high-ROI patterns from evaluated references |
| Command | `/repo-equip` | Analyze a repo and equip it with matching Claude Code components |
| Command | `/repo-optimize` | Multi-model repo optimization with agent team execution |
| Agent | `codex-delegator` | Delegate tasks to Codex CLI with monitoring, sandbox validation, and result summarization |
| Agent | `gemini-delegator` | Delegate exploration/analysis tasks to Gemini CLI with structured JSON parsing |
| Command | `/codex` | Delegate tasks to Codex CLI via slash command with monitoring |
| Command | `/gemini` | Delegate exploration/analysis tasks to Gemini CLI with monitoring |

### Hook Development
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `uv-hook-template` | UV + PEP 723 templates for PreToolUse, PostToolUse, UserPromptSubmit, SessionStart, and Notification hooks |

### Agent Teams (Experimental)
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/spawn-team` | Create and coordinate an agent team for parallel work |
| Skill | `agent-teams` | Best practices for team coordination (reference, not user-invocable) |
| Agent | `meta-agent` | Generate new sub-agent configs from descriptions |
| Agent | `team-builder` | Focused engineering agent for single-task execution in teams |
| Agent | `team-validator` | Read-only validation agent for verifying task completion |
| Workflow | `agent-team-coordination` | End-to-end team coordination workflow |
| Hook | `teammate-idle-gate` | Quality gate: check uncommitted changes + pending tasks (TeammateIdle) |
| Hook | `task-completed-gate` | Quality gate: run build/lint before task completion (TaskCompleted) |
| Hook | `prompt-validator` | UserPromptSubmit validator for empty/oversized/injection-like prompts with session prompt-count context |
| Example | `settings-agent-teams.json` | Settings template with feature flag + teammate mode |

### Research
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `library-researcher` | External library docs |
| Agent | `technical-researcher` | Technical research |

### Infrastructure
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `deployment-engineer` | CI/CD, containerization |
| Agent | `mcp-backend-engineer` | MCP implementation |

### Configuration Templates
| Type | Component | Purpose |
|------|-----------|---------|
| Example | `.mcp.json` | MCP server config template (stdio, SSE, streamable-HTTP) |
| Example | `settings-strict.json` | Strict security settings (deny web, managed hooks only) |
| Example | `settings-permissive.json` | Permissive development settings |
| Example | `settings-agent-teams.json` | Agent teams config (feature flag + teammate mode) |

## Workflow Chains

Multi-step workflows for complex tasks:

| Workflow | Start | Purpose |
|----------|-------|---------|
| [feature-development](workflows/feature-development.md) | `/onboarding` | End-to-end feature implementation |
| [bug-investigation](workflows/bug-investigation.md) | `/rca` | Systematic debugging |
| [code-quality](workflows/code-quality.md) | `/code-review` | Pre-merge validation |
| [new-developer](workflows/new-developer.md) | `/onboarding` | Onboarding progression |
| [agent-team-coordination](workflows/agent-team-coordination.md) | `/spawn-team` | Parallel team coordination |

### PRP (Prompt Request Protocol)
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/prp-any-cli-create` | Create PRP for any CLI agent |
| Command | `/prp-any-cli-execute` | Execute PRP with any CLI agent |
| Command | `/prp-claude-code-create` | Create PRP for Claude Code |
| Command | `/prp-claude-code-execute` | Execute PRP with Claude Code |
| Command | `/prp-story-task-create` | Create PRP from user story/task |
| Command | `/prp-story-task-execute` | Execute story-based PRP |

## Component Counts

| Type | Count | Location |
|------|-------|----------|
| Agents | 18 | `.claude/agents/` |
| Commands | 43 | `.claude/commands/` |
| Skills | 17 global + 7 template | `.claude/skills/` + `templates/n8n/skills/` |
| Rules | 1 | `.claude/rules/` |
| Hooks | 20 (16 command + 4 prompt) | `.claude/hooks/` |
| Examples | 4 | `.mcp.json` + `examples/settings/` |
| Workflows | 5 | `.claude/workflows/` |

## Cross-Reference Map

### Visual Overview

```
                    ANALYSIS & CONTEXT
                    ==================
    /onboarding ──→ /quick-prime ──→ /deep-prime
         │              │                 │
         ↓              ↓                 ↓
    context-manager ←─→ codebase-analyst ←─→ lsp-symbol-navigation
                              │
                              ↓
                    CODE QUALITY & REVIEW
                    =====================
    /code-review ←──────────→ code-reviewer
         │                         │
         ↓                         ↓
    /ui-review              test-automator ←─→ lsp-type-safety-check
                                   │
                                   ↓
                    DEBUGGING & TESTING
                    ===================
    /rca ←─────────────────→ debugger
         │                      │
         ↓                      ↓
    dependency-analyzer ←─→ lsp-dependency-analysis

                    EVALUATION & ADOPTION PIPELINE
                    ================================
    /sync-reference ──→ skill-evaluator ──→ /reference-distill
                                                    │
                                    ┌───────────────┤
                                    ↓               ↓
                              adoptions.md    PRPs/distill-*.md
                                    │               │
                                    ↓               ↓
                              /repo-equip    /prp-claude-code-execute
                                    │
                                    ↓
                              /repo-optimize

                    AGENT TEAMS (EXPERIMENTAL)
                    ==========================
    /spawn-team ──→ agent-teams skill ──→ agent-team-coordination
         │                                       │
         ├──→ teammate-idle-gate (hook)          │
         ├──→ task-completed-gate (hook)         │
         └──→ /code-review (final validation)  ←─┘
```

### Component Relationships Table

| Component | Related Agents | Related Commands | Related Skills |
|-----------|---------------|------------------|----------------|
| **Agents** |
| `codebase-analyst` | context-manager, debugger | /deep-prime, /quick-prime | lsp-symbol-navigation, lsp-dependency-analysis |
| `code-reviewer` | test-automator, codebase-analyst | /code-review, /ui-review | lsp-type-safety-check |
| `context-manager` | codebase-analyst | /deep-prime, /onboarding | — |
| `debugger` | codebase-analyst, dependency-analyzer | /rca | lsp-dependency-analysis |
| `deployment-engineer` | — | — | — |
| `library-researcher` | technical-researcher | — | — |
| `mcp-backend-engineer` | — | — | — |
| `n8n-mcp-tester` | — | — | n8n-* skills |
| `technical-researcher` | library-researcher | — | — |
| `test-automator` | code-reviewer, debugger | /code-review | — |
| `meta-agent` | code-reviewer, debugger, test-automator | /repo-equip | reference-distill |
| `team-builder` | team-validator | /spawn-team | agent-teams |
| `team-validator` | team-builder | /spawn-team | agent-teams |
| `codex-delegator` | code-reviewer, debugger, test-automator | /codex, /orchestrate | fork-terminal, agent-sandboxes, multi-model-orchestration |
| `gemini-delegator` | codebase-analyst, code-reviewer, codex-delegator | /gemini, /orchestrate | fork-terminal, multi-model-orchestration |
| **Skills** |
| `agent-browser` | — | — | fork-terminal, agent-sandboxes |
| `agent-sandboxes` | test-automator, debugger, deployment-engineer | — | fork-terminal, agent-browser |
| `fork-terminal` | context-manager | /orchestrate | agent-browser, agent-sandboxes, multi-model-orchestration |
| `multi-model-orchestration` | — | /orchestrate | fork-terminal, skill-evaluator |
| `skill-evaluator` | codebase-analyst | — | fork-terminal, multi-model-orchestration |
| `reference-distill` | — | /reference-distill | skill-evaluator, repo-equip-engine, repo-optimize-engine, fork-terminal |
| `repo-equip-engine` | — | /repo-equip | skill-evaluator, multi-model-orchestration, reference-distill |
| `repo-optimize-engine` | — | /repo-optimize | repo-equip-engine, multi-model-orchestration, agent-teams, fork-terminal |
| `agent-teams` | — | /spawn-team | multi-model-orchestration, fork-terminal |
| `lsp-symbol-navigation` | codebase-analyst | /deep-prime | lsp-dependency-analysis, lsp-type-safety-check |
| `lsp-type-safety-check` | code-reviewer | /code-review | lsp-symbol-navigation |
| `lsp-dependency-analysis` | debugger, dependency-analyzer | /rca | lsp-symbol-navigation |
| `n8n-*` (7 skills) | n8n-mcp-tester | — | (inter-related) |
| `mac-manage-context` | — | /mac-health, /mac-diff, /mac-status, /mac-discover, /mac-restore | — |
| `cbass-context` | — | /cbass-status, /cbass-logs, /cbass-deploy | — |
| `obsidian-context` | — | /obsidian-status, /obsidian-health, /obsidian-restart, /obsidian-logs, /obsidian-env-check, /obsidian-caddy-reload, /obsidian-vault-sync, /obsidian-deploy | — |

### n8n Skills Relationships

```
n8n-workflow-patterns ──→ Choose architecture
         │
         ↓
n8n-node-configuration ──→ Configure nodes
         │
         ├──→ n8n-code-javascript (complex logic)
         ├──→ n8n-code-python (stdlib needs)
         └──→ n8n-expression-syntax (dynamic fields)
         │
         ↓
n8n-mcp-tools-expert ──→ Use MCP tools
         │
         ↓
n8n-validation-expert ──→ Fix validation errors
```

### PRP Command Relationships

```
/prp-story-task-create ──→ /prp-story-task-execute
         │                          │
         │  (simpler tasks)         │
         ↓                          ↓
/prp-claude-code-create ──→ /prp-claude-code-execute
         │                          │
         │  (Claude Code)           │
         ↓                          ↓
/prp-any-cli-create ────→ /prp-any-cli-execute
                    (Codex/Gemini/other)
```

### Mac Management Command Relationships

```
/mac-status "weekly" ──→ (runs all four below in sequence)
         │
         ├──→ /mac-status "snapshot" ──→ snapshot + auto-diff
         ├──→ /mac-diff ──────────────→ interpret changes
         ├──→ /mac-health ────────────→ triage findings
         └──→ /mac-discover (abbreviated)
                    │
                    ↓
              /mac-restore ←── uses snapshot data
                    │
                    ↓
              /mac-health ←── post-restore verify

All commands reference: mac-manage-context skill
```

### cbass Command Relationships

```
/cbass-deploy ──→ start services with profile/environment
         │
         ↓
/cbass-status ──→ check all 28 services
         │
         ├──→ /cbass-logs "<service>" ──→ diagnose failures
         └──→ /rca "<issue>" ──→ deep root cause analysis

All commands reference: cbass-context skill
```

### Obsidian Command Relationships

```
/obsidian-status ──→ check all 16 services + Caddy
         │
         ├──→ /obsidian-health "<service>" ──→ deep endpoint test
         ├──→ /obsidian-logs "<service>" ──→ diagnose failures
         ├──→ /obsidian-restart "<service>" ──→ restart + verify
         └──→ /rca "<issue>" ──→ deep root cause analysis

/obsidian-deploy ──→ full deployment (rsync + deploy.sh + health)
         ├──→ /obsidian-env-check ──→ validate .env (pre-flight)
         └──→ /obsidian-health ──→ verify after deploy
/obsidian-env-check ──→ validate .env before deploy
/obsidian-caddy-reload ──→ reload Caddy after Caddyfile changes
/obsidian-vault-sync ──→ sync vault (push/pull/sync/watch)

All commands reference: obsidian-context skill
```

### Workflow Entry Points

| Starting Point | Leads To | Use When |
|----------------|----------|----------|
| `/onboarding` | feature-development, new-developer | New to project |
| `/quick-prime` | Any implementation task | Quick context refresh |
| `/deep-prime` | feature-development | Deep dive before coding |
| `/code-review` | code-quality | Pre-merge validation |
| `/rca` | bug-investigation | Debugging issues |
| `/spawn-team` | agent-team-coordination | Parallel team work |
