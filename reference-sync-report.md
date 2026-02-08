# Reference Sync Report

**Generated**: 2026-02-07
**claude-code version**: v2.1.31 (bd78b216)
**skillz commit**: 0c784a8
**Mode**: quick

## Executive Summary

The official Claude Code reference (v2.1.31) now ships a **formal plugin system** with `.claude-plugin/plugin.json` manifests, 14 official plugins, and standardized component conventions. The skillz templates predate this plugin architecture and use a flat `.claude/` directory structure with custom frontmatter fields (`category`, `related`, `color`) that differ from the official conventions. Key gaps include: no `.claude-plugin/` manifest, missing `allowed-tools` frontmatter in commands, absence of several new hook events (`SubagentStop`, `SessionEnd`, `PreCompact`, `Notification`), and no MCP integration patterns (`.mcp.json`).

## What's New Since Last Sync

First sync - baseline established.

## Recommended Updates

### Critical Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| Plugin manifest | skillz has no `.claude-plugin/plugin.json` | Add a plugin manifest to make skillz installable as a proper Claude Code plugin via `/plugin install` |
| Hook events | skillz hooks only use `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop` | Add support for `SubagentStop`, `SessionEnd`, `PreCompact`, `Notification`, `UserPromptSubmit` events |
| `allowed-tools` in commands | skillz commands lack `allowed-tools` frontmatter | Add `allowed-tools` field to command frontmatter for proper permission scoping (e.g., code-review needs `Bash(gh pr *)`) |

### High Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| MCP integration | No `.mcp.json` or MCP patterns in skillz | Add `.mcp.json` configuration patterns and examples for external service integration |
| Agent `tools` field format | skillz agents use custom array syntax with `- Tool` items | Align with official format: either `tools: ["Read", "Grep"]` (JSON array) or `tools: Glob, Grep, LS, Read` (comma-separated string) |
| Hook JSON format | skillz uses direct format in `hooks.json` | Official plugins use wrapper format: `{ "description": "...", "hooks": { "PreToolUse": [...] } }` |
| Security guidance | No security-focused hook | Adopt the `security-guidance` plugin pattern: PreToolUse hook monitoring Edit/Write for 9 security patterns (XSS, injection, eval, etc.) |
| `${CLAUDE_PLUGIN_ROOT}` | Not used in skillz hooks/scripts | Use `${CLAUDE_PLUGIN_ROOT}` for portable paths in hook commands and scripts |

### Medium Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| Skill progressive disclosure | skillz skills have flat structure | Adopt 3-level disclosure: metadata (always loaded) → SKILL.md (~1500 words) → references/examples (on demand) |
| Agent `description` format | skillz uses multi-line examples | Official uses `<example>` blocks in descriptions for reliable triggering |
| Command `argument-hint` field | Not present in skillz commands | Add `argument-hint` frontmatter for better `/command` autocomplete UX |
| Plugin-dev toolkit | No equivalent in skillz | Consider adopting `plugin-dev` patterns for plugin creation guidance |
| Hookify patterns | No user-configurable hooks | Consider hookify's `.local.md` pattern for user-defined validation rules |
| Commit commands | No `/commit` or `/commit-push-pr` | Adopt `commit-commands` plugin patterns for git workflow automation |
| Feature-dev workflow | skillz has `feature-workflow.md` rule | Official `feature-dev` plugin has a full 7-phase command with 3 dedicated agents |
| Settings examples | No settings.json templates | Add example settings templates (strict, permissive, sandbox modes) from `examples/settings/` |

### Low Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| Agent colors | skillz uses custom colors (violet, pink, slate) | Official uses: blue, cyan, green, yellow, magenta, red |
| Model field | skillz uses `model: haiku` | Official prefers `model: inherit` (recommended) or explicit `model: sonnet` |
| README.md per plugin | skillz has project-level README only | Each plugin should have its own README.md with overview, commands, agents, and usage examples |
| Ralph-wiggum pattern | Not in skillz | Consider adopting self-referential iteration loops for autonomous long-running tasks |
| Frontend-design skill | Not in skillz | Adopt auto-invoked skill for frontend work guidance |
| claude-opus-4-5-migration | Not in skillz | Model migration skill for upgrading model strings and prompts |

## Pattern Comparison

### Frontmatter Conventions

#### Agent Frontmatter

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `name` | Required, kebab-case | Present | Match |
| `description` | Multi-line with `<example>` blocks | Multi-line with bullet examples | Differs |
| `model` | `inherit` (recommended), `sonnet`, `opus`, `haiku` | `haiku` (hardcoded) | Differs |
| `color` | blue, cyan, green, yellow, magenta, red | violet, pink, slate (custom) | Differs |
| `tools` | JSON array `["Read", "Grep"]` or comma string | YAML list `- Read`, `- Grep` | Differs |
| `category` | Not in official | Present (analysis, quality) | Extra field |
| `related` | Not in official | Present (agents, commands, skills, hooks, workflows) | Extra field |

#### Command Frontmatter

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `description` | Required | Present in some | Partial |
| `allowed-tools` | Present for permission scoping | Not used | Missing |
| `argument-hint` | Present for UX | Not used | Missing |
| `$ARGUMENTS` | Supported for user input | Used | Match |

#### Skill Frontmatter (SKILL.md)

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `name` | Required | Present | Match |
| `description` | Third-person trigger descriptions | Present | Match |
| `version` | Present | Present in some | Partial |
| `category` | Not standard | Present | Extra field |
| `user-invocable` | Present | Present in some | Partial |

### Directory Structure

| Aspect | claude-code (plugins) | skillz (.claude/) |
|--------|----------------------|-------------------|
| Root marker | `.claude-plugin/plugin.json` | No manifest |
| Commands | `commands/` | `.claude/commands/` (with subdirs) |
| Agents | `agents/` | `.claude/agents/` (flat + nested) |
| Skills | `skills/skill-name/SKILL.md` | `.claude/skills/skill-name/SKILL.md` |
| Hooks | `hooks/hooks.json` + `hooks-handlers/` | `.claude/hooks/hooks.json` + `.py`/`.sh` files |
| MCP | `.mcp.json` at plugin root | Not present |
| Workflows | Not in plugins (project-level) | `.claude/workflows/` |
| Rules | Not in plugins (project-level) | `.claude/rules/` |
| Utils | Not in plugins | `.claude/utils/` (Python modules) |
| Memory | Not in plugins | `.claude/memory/` |

### Naming Conventions

| Aspect | claude-code | skillz | Status |
|--------|-------------|--------|--------|
| Plugin names | kebab-case, start with letter | N/A | N/A |
| Agent files | `name.md` (flat) | `name.md` (flat) or `name/AGENT.md` (nested) | Differs |
| Command files | `name.md` or `namespace/name.md` | `name.md` or `namespace/name.md` | Match |
| Skill dirs | `skill-name/SKILL.md` | `skill-name/SKILL.md` | Match |
| Hook scripts | `hooks-handlers/script.sh` | Direct `.py`/`.sh` in hooks dir | Differs |

## Plugins Worth Adopting

### Immediate Value

1. **commit-commands** - `/commit`, `/commit-push-pr`, `/clean_gone` for git workflow
2. **security-guidance** - PreToolUse hook for real-time security pattern detection
3. **hookify** - User-configurable hooks from `.local.md` files

### High Value

4. **code-review** (official) - 5 parallel Sonnet agents with confidence scoring, GitHub integration
5. **feature-dev** - Full 7-phase workflow with `code-explorer`, `code-architect`, `code-reviewer` agents
6. **plugin-dev** - 7 expert skills for building Claude Code plugins

### Nice to Have

7. **ralph-wiggum** - Self-referential iteration loops for autonomous development
8. **frontend-design** - Auto-invoked skill for bold, production-grade UI
9. **pr-review-toolkit** - 6 specialized review agents (comments, tests, errors, types, quality, simplification)
10. **explanatory-output-style** - Educational context injection at SessionStart

## Hook Patterns

### Events Available (Reference)

| Event | Available in skillz | Notes |
|-------|-------------------|-------|
| `PreToolUse` | Yes | Used for LSP reference checking |
| `PostToolUse` | Yes | Used for LSP type validation |
| `SessionStart` | Yes | Used for session-init, memory-loader |
| `Stop` | Yes | Used for completion verification |
| `SubagentStop` | **No** | New - intercept subagent exits |
| `SessionEnd` | **No** | New - cleanup on session end |
| `PreCompact` | **No** | New - before context compaction |
| `Notification` | **No** | New - on Claude notifications |
| `UserPromptSubmit` | **No** | New - validate user prompts |

### Hook Type Patterns (Reference)

| Pattern | Description | Used in skillz |
|---------|-------------|----------------|
| Command hooks | Bash/script execution | Yes (Python scripts) |
| Prompt hooks | LLM-based decision making | Yes (Stop hook) |
| Matcher patterns | Tool filtering (`Write\|Edit`, `mcp__.*`) | Partial |
| `${CLAUDE_PLUGIN_ROOT}` | Portable path references | No |
| `$CLAUDE_ENV_FILE` | Persist env vars from SessionStart | No |
| Exit code semantics | 0=success, 2=blocking error | Not documented |

### Notable Hook Implementations

1. **Security guidance**: PreToolUse on `Edit|Write|MultiEdit` checking 9 security patterns
2. **Hookify**: User-defined rules in `.local.md` with conditions and actions
3. **Ralph-wiggum**: Stop hook that blocks exit to create iteration loops
4. **Learning mode**: SessionStart hook injecting educational context
5. **Explanatory mode**: SessionStart hook adding pattern insights

## Action Items

### Immediate (Critical)
- [ ] Create `.claude-plugin/plugin.json` manifest for skillz
- [ ] Add `allowed-tools` frontmatter to all commands that use restricted tools
- [ ] Update hooks.json to use wrapper format with `description` field

### Short-term (High Priority)
- [ ] Add `.mcp.json` template/pattern for MCP integration
- [ ] Adopt `${CLAUDE_PLUGIN_ROOT}` in hook scripts for portability
- [ ] Add security-guidance hook (PreToolUse monitoring Edit/Write for security patterns)
- [ ] Implement `SubagentStop` and `SessionEnd` hooks where beneficial
- [ ] Align agent `tools` field format with official convention
- [ ] Add `argument-hint` to commands that accept arguments

### Long-term (Medium/Low)
- [ ] Adopt 3-level progressive disclosure for skills (metadata → core → references)
- [ ] Align agent colors with official palette (blue, cyan, green, yellow, magenta, red)
- [ ] Prefer `model: inherit` over hardcoded `model: haiku` in agents
- [ ] Evaluate adopting `commit-commands`, `hookify`, and `feature-dev` plugins
- [ ] Add per-plugin README.md documentation
- [ ] Create example settings templates (strict, permissive, sandbox)
- [ ] Consider ralph-wiggum pattern for autonomous long-running tasks
