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

## Reference Submodules

This repo includes reference submodules in `references/` for learning from other Claude Code projects:

| Submodule | Source | Purpose |
|-----------|--------|---------|
| claude-code | anthropics/claude-code | Official Claude Code reference |
| opencode | opencode-ai/opencode | Terminal-based AI coding agent |
| oh-my-opencode | code-yeongyu/oh-my-opencode | Agent harness patterns |
| openclaw | openclaw/openclaw | OpenClaw project |
| last30days-skill | mvanhorn/last30days-skill | Skill implementation example |
| compound-engineering-plugin | mdc159/compound-engineering-plugin | Plugin patterns |
| agent-zero | mdc159/agent-zero | Agent architecture |

**On Session Start:** The session hook checks for updates to these references. When updates are available:
1. **Ask the user** if they want to update (don't auto-update)
2. If yes, run: `./scripts/update-references.sh`
3. After updating, briefly summarize what changed in each updated repo (check recent commits)

**Manual commands:**
- `./scripts/update-references.sh --status-only` - Check status without updating
- `./scripts/update-references.sh` - Update all references

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

references/      # Git submodules for learning/reference (not for copying)
├── claude-code/
├── opencode/
├── oh-my-opencode/
├── openclaw/
├── last30days-skill/
├── compound-engineering-plugin/
└── agent-zero/
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

**Hooks** (`.claude/hooks/hooks.json`): Define hook events with command or prompt-based hooks. Supported events: `PreToolUse`, `PostToolUse`, `SessionStart`, `SessionEnd`, `Stop`, `SubagentStop`, `PreCompact`, `UserPromptSubmit`, `Notification`.

**Workflows** (`.claude/workflows/*.md`): Multi-step sequences combining commands, agents, and decision points.
