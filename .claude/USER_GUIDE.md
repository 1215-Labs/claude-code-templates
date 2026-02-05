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
| `multi-model-orchestration` | Delegate tasks across Gemini/Codex |
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
| `/sync-reference` | Compare against claude-code reference |
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

## Workflows

For multi-step processes, follow workflow chains:

| Workflow | When |
|----------|------|
| `feature-development` | Building new features |
| `bug-investigation` | Debugging issues |
| `code-quality` | Before merge/deploy |
| `new-developer` | Onboarding |

**View workflow**: Read `.claude/workflows/<name>.md`

## Hooks (Automatic)

These are Claude Code hooks that run automatically during tool use and session events (not git hooks):

| Hook | Event | Action |
|------|-------|--------|
| `lsp-reference-checker` | PostToolUse | Warns about high-impact changes |
| `lsp-type-validator` | PreToolUse | Blocks edits with type errors |
| `session-init` | SessionStart | Initialize session context, check references |
| `uncommitted-check` | Stop | Warn about uncommitted/unpushed changes |

## Quick Reference Card

```
┌─────────────────────────────────────────────────────┐
│  COMMANDS (invoke directly)                         │
│  /onboarding  /quick-prime  /deep-prime             │
│  /code-review  /ui-review  /rca  /orchestrate       │
│  /sync-reference  /coderabbit-helper  /all_skills   │
├─────────────────────────────────────────────────────┤
│  AGENTS (ask to use)                                │
│  codebase-analyst  code-reviewer  debugger          │
│  test-automator  type-checker  dependency-analyzer  │
│  lsp-navigator  context-manager  library-researcher │
│  technical-researcher  deployment-engineer          │
│  mcp-backend-engineer  n8n-mcp-tester               │
├─────────────────────────────────────────────────────┤
│  SKILLS (reference for patterns)                    │
│  lsp-symbol-navigation  lsp-dependency-analysis     │
│  lsp-type-safety-check  fork-terminal               │
│  agent-browser  multi-model-orchestration  n8n-*    │
├─────────────────────────────────────────────────────┤
│  WORKFLOWS (follow for processes)                   │
│  feature-development  bug-investigation             │
│  code-quality  new-developer                        │
└─────────────────────────────────────────────────────┘
```

## Tips

1. **Start with commands** - They're the quickest entry point
2. **Use agents for complex tasks** - They have specialized knowledge
3. **Follow workflows** - For multi-step processes, don't skip steps
4. **Trust the hooks** - They catch issues automatically
5. **Check REGISTRY.md** - Full component catalog with cross-references

## See Also

- [REGISTRY.md](REGISTRY.md) - Complete component catalog
- [CLAUDE.md](CLAUDE.md) - Configuration overview
