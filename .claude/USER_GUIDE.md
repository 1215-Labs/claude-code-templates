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
| `context-manager` | Managing conversation context |

**Example**: "Use the `debugger` agent to investigate this error..."

## Skills

Skills provide reusable expertise. Key skills:

| Skill | Purpose |
|-------|---------|
| `lsp-symbol-navigation` | Go-to-definition, find-references |
| `lsp-dependency-analysis` | Map module dependencies |
| `lsp-type-safety-check` | Verify type safety |
| `n8n-*` | n8n workflow development |

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

These run automatically on git commit:

| Hook | Action |
|------|--------|
| `lsp-reference-checker` | Warns about high-impact changes |
| `lsp-type-validator` | Blocks commits with type errors |

## Quick Reference Card

```
┌─────────────────────────────────────────────────┐
│  COMMANDS (invoke directly)                     │
│  /onboarding  /quick-prime  /deep-prime         │
│  /code-review  /ui-review  /rca                 │
├─────────────────────────────────────────────────┤
│  AGENTS (ask to use)                            │
│  codebase-analyst  code-reviewer  debugger      │
│  test-automator  type-checker  dependency-analyzer│
├─────────────────────────────────────────────────┤
│  SKILLS (reference for patterns)                │
│  lsp-symbol-navigation  lsp-dependency-analysis │
│  lsp-type-safety-check  n8n-*                   │
├─────────────────────────────────────────────────┤
│  WORKFLOWS (follow for processes)               │
│  feature-development  bug-investigation         │
│  code-quality  new-developer                    │
└─────────────────────────────────────────────────┘
```

## Tips

1. **Start with commands** - They're the quickest entry point
2. **Use agents for complex tasks** - They have specialized knowledge
3. **Follow workflows** - For multi-step processes, don't skip steps
4. **Trust the hooks** - They catch issues before commit
5. **Check REGISTRY.md** - Full component catalog with cross-references

## See Also

- [REGISTRY.md](REGISTRY.md) - Complete component catalog
- [CLAUDE.md](CLAUDE.md) - Configuration overview
