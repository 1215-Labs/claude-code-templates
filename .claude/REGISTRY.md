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
| Fork terminal | `fork-terminal` skill |
| Orchestrate tasks | `/orchestrate "task"` |
| Evaluate a skill/plugin | `skill-evaluator` skill |
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
| Hook | `memory-distill` | Create session log stub on session end |
| Hook | `uncommitted-check` | Warn about uncommitted/unpushed changes on stop |
| Hook | `security-guidance` | Scan edits for security anti-patterns (PreToolUse prompt) |
| Hook | `subagent-verify` | Verify subagent completed its task (SubagentStop prompt) |
| Hook | `context-preserve` | Preserve critical context before compaction (PreCompact prompt) |
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

### Browser & Terminal Automation
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `agent-browser` | Vercel agent-browser CLI for headless automation |
| Skill | `fork-terminal` | Fork terminal to new window with Claude/Codex/Gemini (dual-mode) |

### Orchestration
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `multi-model-orchestration` | Delegate tasks across Gemini/Codex via forked terminals |
| Skill | `skill-evaluator` | Evaluate external skills/plugins before adoption (parallel agents) |
| Command | `/orchestrate` | Quick orchestration via forked terminals |

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

## Workflow Chains

Multi-step workflows for complex tasks:

| Workflow | Start | Purpose |
|----------|-------|---------|
| [feature-development](workflows/feature-development.md) | `/onboarding` | End-to-end feature implementation |
| [bug-investigation](workflows/bug-investigation.md) | `/rca` | Systematic debugging |
| [code-quality](workflows/code-quality.md) | `/code-review` | Pre-merge validation |
| [new-developer](workflows/new-developer.md) | `/onboarding` | Onboarding progression |

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
| Agents | 13 | `.claude/agents/` |
| Commands | 25 | `.claude/commands/` |
| Skills | 8 global + 7 template | `.claude/skills/` + `templates/n8n/skills/` |
| Rules | 1 | `.claude/rules/` |
| Hooks | 12 (7 command + 5 prompt) | `.claude/hooks/` |
| Examples | 3 | `.mcp.json` + `examples/settings/` |
| Workflows | 4 | `.claude/workflows/` |

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
| **Skills** |
| `agent-browser` | — | — | fork-terminal |
| `fork-terminal` | context-manager | /orchestrate | agent-browser, multi-model-orchestration |
| `multi-model-orchestration` | — | /orchestrate | fork-terminal, skill-evaluator |
| `skill-evaluator` | codebase-analyst | — | fork-terminal, multi-model-orchestration |
| `lsp-symbol-navigation` | codebase-analyst | /deep-prime | lsp-dependency-analysis, lsp-type-safety-check |
| `lsp-type-safety-check` | code-reviewer | /code-review | lsp-symbol-navigation |
| `lsp-dependency-analysis` | debugger, dependency-analyzer | /rca | lsp-symbol-navigation |
| `n8n-*` (7 skills) | n8n-mcp-tester | — | (inter-related) |
| `mac-manage-context` | — | /mac-health, /mac-diff, /mac-status, /mac-discover, /mac-restore | — |

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

### Workflow Entry Points

| Starting Point | Leads To | Use When |
|----------------|----------|----------|
| `/onboarding` | feature-development, new-developer | New to project |
| `/quick-prime` | Any implementation task | Quick context refresh |
| `/deep-prime` | feature-development | Deep dive before coding |
| `/code-review` | code-quality | Pre-merge validation |
| `/rca` | bug-investigation | Debugging issues |
