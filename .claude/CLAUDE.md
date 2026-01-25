# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repository Is

This is a **Claude Code configuration template library** - a collection of reusable `.claude/` folder components that can be copied into other projects. It provides pre-built agents, commands, skills, hooks, and workflows for LSP-aware development.

## Using These Templates

To use in your project:
1. Copy the entire `.claude/` folder to your project root
2. Edit component files to match your project's needs
3. Update paths and conventions in command/agent prompts
4. Remove components you don't need (e.g., n8n skills if not using n8n)

See [REGISTRY.md](REGISTRY.md) for complete component catalog and [USER_GUIDE.md](USER_GUIDE.md) for usage instructions.

## Quick Start (When Working in This Repo)

| Task | Command/Agent |
|------|---------------|
| New to project | `/onboarding` |
| Quick context | `/quick-prime` |
| Deep context | `/deep-prime "area" "focus"` |
| Code review | `/code-review` |
| Debug issue | `/rca "error"` |
| Find patterns | `codebase-analyst` agent |
| Check types | `type-checker` agent |

## LSP Usage

When working with code, prefer LSP-based navigation:
- Use **go-to-definition** to jump to symbol definitions
- Use **find-references** to see all usages of a symbol
- Use **hover** to get type signatures and documentation

## Directory Structure

```
.claude/
├── agents/      # Sub-agents for specialized tasks
├── commands/    # Slash commands for workflows
├── skills/      # Reusable patterns and expertise
├── rules/       # Development rules
├── hooks/       # Automated checks
└── workflows/   # Multi-step workflow chains
```

## Workflow Chains

For complex tasks, follow workflow chains in `.claude/workflows/`:
- `feature-development.md` - End-to-end feature development
- `bug-investigation.md` - Systematic debugging
- `code-quality.md` - Pre-merge validation
- `new-developer.md` - Onboarding process

## Agents

See `.claude/agents/` for LSP-aware sub-agents.

## Skills

See `.claude/skills/` for reusable LSP patterns.

## Hooks

See `.claude/hooks/` for automated LSP-based checks.

## Component File Conventions

**Agents** (`.claude/agents/*.md`): YAML frontmatter with `name`, `description`, `model`, `color`, `tools`, `category`, `related` fields, followed by system prompt.

**Skills** (`.claude/skills/*/SKILL.md`): YAML frontmatter with `name`, `description`, `version`, `category`, `user-invocable`, `related` fields, followed by usage instructions.

**Commands** (`.claude/commands/**/*.md`): Can use `$ARGUMENTS` to receive user input. Support single or multiple quoted arguments.

**Hooks** (`.claude/hooks/hooks.json`): Define `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop` events with command or prompt-based hooks.

**Workflows** (`.claude/workflows/*.md`): Multi-step sequences combining commands, agents, and decision points.
