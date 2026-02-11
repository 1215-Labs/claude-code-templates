# Project Context

## Architecture
- **Template library** — reusable `.claude/` folder components (agents, commands, skills, hooks, workflows)
- **Reference submodules** in `references/` — evaluated and selectively adopted via `/skill-evaluator` + `/reference-distill`
- **Multi-model delegation** — Codex for implementation, Gemini for exploration/validation, Opus for orchestration

## Stack
- Markdown-based configs (agents, commands, skills, workflows)
- Python (UV + PEP 723) for hooks and executors
- Bash for install scripts and git operations
- Git submodules for reference repos

## Conventions
- Agents: YAML frontmatter (`name`, `description`, `model`, `tools`, `category`, `related`)
- Skills: YAML frontmatter + `SKILL.md` per skill directory
- Commands: `$ARGUMENTS` for user input, support quoted args
- Hooks: `hooks.json` event-based (PreToolUse, PostToolUse, etc.)
- Adoptions tracked in `adoptions.md` with ADO-NNN numbering
- Decisions tracked in `decisions.md` with DEC-NNN numbering

## Key Pipelines
- **Evaluate → Distill → Adopt**: `/skill-evaluator` scores reference → `/reference-distill` extracts → components land in `.claude/`
- **Equip → Optimize**: `/repo-equip` detects gaps in target repos → `/repo-optimize` generates fix plans
- **Delegate**: `/codex` and `/gemini` fork terminals with task executors for parallel work
