# User Guide

Quick reference for using the `.claude` folder components.

## Getting Started

| Goal | Command |
|------|---------|
| First time here? | `/onboarding` |
| Quick context refresh | `/quick-prime` |
| Deep dive into area | `/deep-prime "frontend" "components"` |

## Common Tasks

### Code Review & Quality

```
/code-review              # Review current changes
/ui-review                # Review UI components
```

### Debugging

```
/rca "error message"      # Root cause analysis
```

### Orchestration

```
/orchestrate "task"       # Delegate to Gemini/Codex via forked terminals
```

### Agent Teams (Experimental)

```
/spawn-team "task"        # Create agent team for parallel work
```

Coordinate multiple Claude Code instances for parallel review, investigation, or cross-layer implementation. Requires `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.

**Tip**: Start with review teams (security + performance + tests) before attempting implementation teams.

### Understanding Code

| Need | Use |
|------|-----|
| Find patterns | `codebase-analyst` agent |
| Trace dependencies | `lsp-dependency-analysis` skill |
| Navigate symbols | `lsp-symbol-navigation` skill |

## Agents

Invoke agents by name when you need specialized help:

| Agent | Use For |
|-------|---------|
| `codebase-analyst` | Finding patterns, conventions |
| `code-reviewer` | Detailed code review |
| `debugger` | Systematic debugging |
| `test-automator` | Writing/improving tests |
| `type-checker` | Type safety verification |
| `dependency-analyzer` | Impact analysis |
| `lsp-navigator` | LSP-based code navigation |
| `context-manager` | Managing conversation context |
| `library-researcher` | External library docs and patterns |
| `technical-researcher` | Deep technical research |
| `deployment-engineer` | CI/CD, containers, cloud deployments |
| `mcp-backend-engineer` | MCP server implementation |
| `n8n-mcp-tester` | n8n MCP tool testing |
| `meta-agent` | Generate new sub-agent configs from descriptions |
| `team-builder` | Single-task engineering execution in agent teams |
| `team-validator` | Read-only task validation in agent teams |

**Example**: "Use the `debugger` agent to investigate this error..."

## Skills

Skills provide reusable expertise. Key skills:

| Skill | Purpose |
|-------|---------|
| `lsp-symbol-navigation` | Go-to-definition, find-references |
| `lsp-dependency-analysis` | Map module dependencies |
| `lsp-type-safety-check` | Verify type safety |
| `fork-terminal` | Fork terminal to new window with Claude/Codex/Gemini |
| `agent-browser` | Headless browser automation with Playwright |
| `agent-sandboxes` | E2B sandbox CLI for isolated code execution |
| `multi-model-orchestration` | Delegate tasks across Gemini/Codex |
| `skill-evaluator` | Evaluate external skills/plugins before adoption |
| `reference-distill` | Extract and integrate patterns from evaluated references |
| `uv-hook-template` | UV single-file script hook templates with PEP 723 metadata |
| `youtube-transcript` | Standalone YouTube transcript downloader/transformer with skill-evaluator integration |
| `repo-equip-engine` | Matching heuristics and templates for `/repo-equip` |
| `repo-optimize-engine` | Scoring rubrics and task graph generation for `/repo-optimize` |
| `mac-manage-context` | Shared knowledge base for `/mac-*` commands |
| `cbass-context` | Shared knowledge base for `/cbass-*` commands |
| `obsidian-context` | Shared knowledge base for `/obsidian-*` commands |
| `skill-router` | Proactive skill invocation with per-repo priority lists |
| `agent-teams` | Best practices for agent team coordination (reference) |
| `n8n-*` | n8n workflow development (7 skills in templates/n8n/) |

## Commands

| Command | Purpose |
|---------|---------|
| `/onboarding` | Full interactive intro |
| `/quick-prime` | Quick 4-point context |
| `/prime` | Alias for /quick-prime |
| `/deep-prime` | Deep area analysis |
| `/code-review` | Comprehensive code review |
| `/ui-review` | UI consistency check |
| `/rca` | Root cause analysis |
| `/orchestrate` | Delegate to Gemini/Codex |
| `/spawn-team` | Create agent team for parallel work |
| `/sync-reference` | Compare against claude-code reference |
| `/reference-distill` | Extract high-ROI patterns from evaluated references |
| `/repo-equip` | Equip any repo with matching components |
| `/repo-optimize` | Deep multi-model repo optimization with agent team |
| `/all_skills` | List available skills |
| `/coderabbit-helper` | Analyze CodeRabbit suggestions |

### PRP Commands

| Command | Purpose |
|---------|---------|
| `/prp-claude-code-create` | Create PRP for Claude Code |
| `/prp-claude-code-execute` | Execute PRP with Claude Code |
| `/prp-story-task-create` | Create PRP from user story |
| `/prp-story-task-execute` | Execute story PRP |
| `/prp-any-cli-create` | Create PRP for any CLI agent |
| `/prp-any-cli-execute` | Execute PRP with any CLI agent |

### Mac Management Commands

| Command | Purpose |
|---------|---------|
| `/mac-health` | Health check triage with remediation |
| `/mac-diff` | Snapshot diff with change interpretation |
| `/mac-status` | Snapshot management and weekly reviews |
| `/mac-discover` | Find untracked config and apps |
| `/mac-restore` | Safe restore with validation |

### cbass Commands

| Command | Purpose |
|---------|---------|
| `/cbass-status` | Service status with health interpretation |
| `/cbass-logs` | Log analysis with error interpretation |
| `/cbass-deploy` | Guided deployment with pre-flight checks |

## Workflows

For multi-step processes, follow workflow chains:

| Workflow | When |
|----------|------|
| `feature-development` | Building new features |
| `bug-investigation` | Debugging issues |
| `code-quality` | Before merge/deploy |
| `new-developer` | Onboarding |
| `agent-team-coordination` | Parallel team work |

**View workflow**: Read `.claude/workflows/<name>.md`

## Hooks (Automatic)

These are Claude Code hooks that run automatically during tool use and session events (not git hooks):

| Hook | Event | Action |
|------|-------|--------|
| `lsp-reference-checker` | PostToolUse | Warns about high-impact changes |
| `lsp-type-validator` | PreToolUse | Blocks edits with type errors |
| `session-init` | SessionStart | Initialize session context, check references |
| `uncommitted-check` | Stop | Warn about uncommitted/unpushed changes |
| `teammate-idle-gate` | TeammateIdle | Check for uncommitted changes + pending tasks |
| `task-completed-gate` | TaskCompleted | Run build/lint before task completion |

## Quick Reference Card

```
┌──────────────────────────────────────────────────────────┐
│  COMMANDS (invoke directly)                              │
│  /onboarding  /quick-prime  /deep-prime  /repo-equip     │
│  /code-review  /ui-review  /rca  /orchestrate            │
│  /spawn-team  /repo-optimize                             │
│  /sync-reference  /coderabbit-helper  /all_skills        │
│  /remember  /forget  /memory                             │
│  /mac-health  /mac-diff  /mac-status  /mac-discover      │
│  /mac-restore  /cbass-status  /cbass-logs  /cbass-deploy │
├──────────────────────────────────────────────────────────┤
│  AGENTS (ask to use)                                     │
│  codebase-analyst  code-reviewer  debugger               │
│  test-automator  type-checker  dependency-analyzer       │
│  lsp-navigator  context-manager  library-researcher      │
│  technical-researcher  deployment-engineer               │
│  mcp-backend-engineer  n8n-mcp-tester                    │
│  meta-agent  team-builder  team-validator                 │
├──────────────────────────────────────────────────────────┤
│  SKILLS (reference for patterns)                         │
│  lsp-symbol-navigation  lsp-dependency-analysis          │
│  lsp-type-safety-check  fork-terminal  agent-browser     │
│  agent-sandboxes  multi-model-orchestration              │
│  skill-evaluator                                         │
│  reference-distill  uv-hook-template                     │
│  youtube-transcript                                      │
│  repo-equip-engine                                       │
│  repo-optimize-engine                                    │
│  mac-manage-context  cbass-context  obsidian-context      │
│  skill-router  agent-teams                               │
│  n8n-* (7 template skills)                               │
├──────────────────────────────────────────────────────────┤
│  WORKFLOWS (follow for processes)                        │
│  feature-development  bug-investigation                  │
│  code-quality  new-developer  agent-team-coordination    │
└──────────────────────────────────────────────────────────┘
```

## Persistent Memory

Claude Code sessions are stateless by default. The persistent memory system saves facts, decisions, and preferences to markdown files that load automatically at session start.

**Key commands:**

| Command | Purpose |
|---------|---------|
| `/memory "init"` | Set up memory directories and starter files |
| `/remember "fact"` | Save a fact (auto-classified to the right file) |
| `/forget "term"` | Remove entries by keyword or decision ID |
| `/memory` | Check what's stored, token usage, health |

Memory is two-tiered: **project memory** (`.claude/memory/`, git-tracked) for architecture and decisions, and **global memory** (`~/.claude/memory/`) for personal preferences that follow you across projects.

See [MEMORY_GUIDE.md](MEMORY_GUIDE.md) for the full guide — architecture, token budgets, security, hooks, and maintenance.

## Tips

1. **Start with commands** - They're the quickest entry point
2. **Use agents for complex tasks** - They have specialized knowledge
3. **Follow workflows** - For multi-step processes, don't skip steps
4. **Trust the hooks** - They catch issues automatically
5. **Check REGISTRY.md** - Full component catalog with cross-references

## See Also

- [REGISTRY.md](REGISTRY.md) - Complete component catalog
- [CLAUDE.md](CLAUDE.md) - Configuration overview
