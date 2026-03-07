# Claude Code Reference Plugin Structure Analysis

**Date**: 2026-03-05
**Source**: `/home/mdc159/projects/claude-code-templates/references/claude-code/plugins/`
**Scope**: Structural patterns only (hooks excluded per task scope)
**Plugins analyzed**: 13 (12 with `plugin.json`, 1 without)

---

## 1. Plugin Manifest Structure (`plugin.json`)

All plugin manifests live at `.claude-plugin/plugin.json` (the `.claude-plugin/` subdirectory is required).

### Core Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `name` | string | YES | kebab-case only; regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`; must be unique |
| `version` | string | NO (default: `"0.1.0"`) | Semantic versioning `MAJOR.MINOR.PATCH`; pre-release allowed (`1.0.0-beta.1`) |
| `description` | string | NO | 50-200 chars recommended; active voice; focus on what, not how |
| `author` | object or string | NO | Object: `{name, email?, url?}`; string: `"Name <email> (url)"` |

### Optional Metadata Fields

| Field | Type | Notes |
|-------|------|-------|
| `homepage` | string (URL) | Plugin docs/landing page; NOT source code |
| `repository` | string or object | `{type, url, directory?}`; source code link |
| `license` | string | SPDX identifier (e.g., `"MIT"`, `"Apache-2.0"`) |
| `keywords` | string[] | 5-10 tags for discovery; include functionality + tech stack |

### Component Path Override Fields

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `commands` | string or string[] | `["./commands"]` | Supplements (does not replace) default `commands/` dir |
| `agents` | string or string[] | `["./agents"]` | Supplements default `agents/` dir |
| `hooks` | string or object | `"./hooks/hooks.json"` | Path to JSON file OR inline object |
| `mcpServers` | string or object | `"./.mcp.json"` | Path to JSON file OR inline object |

### Observed in Practice (all 12 plugin.json files)

| Plugin | name | version | description | author.name | author.email |
|--------|------|---------|-------------|-------------|--------------|
| agent-sdk-dev | yes | `1.0.0` | yes | Ashwin Bhat | yes |
| claude-opus-4-5-migration | yes | `1.0.0` | yes | William Hu | yes |
| code-review | yes | `1.0.0` | yes | Boris Cherny | yes |
| commit-commands | yes | `1.0.0` | yes | Anthropic | yes |
| explanatory-output-style | yes | `1.0.0` | yes | Dickson Tsai | yes |
| feature-dev | yes | `1.0.0` | yes | Sid Bidasaria | yes |
| frontend-design | yes | `1.0.0` | yes | Prithvi Rajasekaran, Alexander Bricken | yes (multi) |
| hookify | yes | `0.1.0` | yes | Daisy Hollman | yes |
| learning-output-style | yes | `1.0.0` | yes | Boris Cherny | yes |
| pr-review-toolkit | yes | `1.0.0` | yes | Daisy | yes |
| ralph-wiggum | yes | `1.0.0` | yes | Daisy Hollman | yes |
| security-guidance | yes | `1.0.0` | yes | David Dworken | yes |

**Findings**: Every observed `plugin.json` includes exactly `name`, `version`, `description`, and `author` (with both `name` and `email`). No plugin uses `homepage`, `repository`, `license`, `keywords`, or component path overrides in practice — they rely entirely on auto-discovery via conventional directory layout.

---

## 2. Directory Organization

### Per-Plugin Directory Presence

| Plugin | `.claude-plugin/` | `commands/` | `agents/` | `skills/` | `hooks/` | `hooks-handlers/` | `scripts/` | Other |
|--------|------------------|-------------|-----------|-----------|----------|-------------------|------------|-------|
| agent-sdk-dev | yes | yes | yes | — | — | — | — | — |
| claude-opus-4-5-migration | yes | — | — | yes | — | — | — | — |
| code-review | yes | yes | — | — | — | — | — | — |
| commit-commands | yes | yes | — | — | — | — | — | — |
| explanatory-output-style | yes | — | — | — | yes | yes | — | — |
| feature-dev | yes | yes | yes | — | — | — | — | — |
| frontend-design | yes | — | — | yes | — | — | — | — |
| hookify | yes | yes | yes | yes | yes | — | — | `core/`, `examples/`, `matchers/`, `utils/` |
| learning-output-style | yes | — | — | — | yes | yes | — | — |
| plugin-dev | NO | yes | yes | yes | — | — | — | — |
| pr-review-toolkit | yes | yes | yes | — | — | — | — | — |
| ralph-wiggum | yes | yes | — | — | yes | — | yes | — |
| security-guidance | yes | — | — | — | yes | — | — | — |

**Findings**:
- `plugin-dev` is the only plugin missing `.claude-plugin/plugin.json` (it appears to be a development/template plugin that is itself incomplete or intentionally treated as an internal tool).
- `hooks-handlers/` is a sibling of `hooks/` used for shell scripts that hooks invoke (seen in `explanatory-output-style` and `learning-output-style`).
- `hookify` is the most complex plugin, adding Python modules (`core/`, `matchers/`, `utils/`) alongside standard dirs.
- Plugins with only one component type still follow the standard single-dir layout (no collapsing to flat files).

### Skill Subdirectory Structure

Skills use a named subdirectory inside `skills/` (i.e., `skills/{skill-name}/`):

| Skill Subdir Level | Subdirs Observed | Purpose |
|--------------------|-----------------|---------|
| `skills/{name}/SKILL.md` | (required) | Main skill definition + frontmatter |
| `skills/{name}/references/` | optional | Docs loaded on demand into context |
| `skills/{name}/examples/` | optional | Example prompts, complete walkthroughs |
| `skills/{name}/scripts/` | optional | Executable shell/Python scripts |
| `skills/{name}/assets/` | optional (spec only) | Output files (templates, images, fonts) |

---

## 3. Frontmatter Conventions

### 3a. Command Frontmatter

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `description` | NO | string | Under 60 chars; shown in `/help`; start with verb |
| `allowed-tools` | NO | string or array | Comma-separated or YAML array; use `Bash(cmd:*)` filter syntax |
| `model` | NO | string | `haiku`, `sonnet`, `opus`; omit to inherit from conversation |
| `argument-hint` | NO | string | `[arg-name]` bracket syntax; documents expected `$ARGUMENTS` |
| `disable-model-invocation` | NO | boolean | `true` = manual-only; prevents SlashCommand tool from calling it |
| `hide-from-slash-command-tool` | NO | string `"true"` | Hides command from slash command tool picker (observed as string, not boolean) |

**Description phrasing pattern**: Verb-first, imperative, no "This command" prefix.
- "Create a git commit"
- "Code review a pull request"
- "Cleans up all git branches marked as [gone]..."
- "Comprehensive PR review using specialized agents"

**Tool allowlist patterns observed**:

| Pattern | Example | Usage |
|---------|---------|-------|
| Named tool | `Read` | Simple tool inclusion |
| Bash with glob filter | `Bash(git:*)` | Restrict to specific binary |
| Bash with exact command | `Bash(git status:*)` | Restrict to specific invocation |
| Mixed comma-separated | `Bash(git add:*), Bash(git status:*), Read` | Multiple tools inline |
| JSON array string | `["Glob", "Read", "Edit", "AskUserQuestion", "Skill"]` | Array format (hookify plugin) |
| MCP tool | `mcp__github_inline_comment__create_inline_comment` | MCP tool inclusion |

**Argument hint format**: `[descriptive-name]` in brackets; multiple args space-separated.
- `[project-name]`
- `Optional feature description`
- `[review-aspects]`
- `PROMPT [--max-iterations N] [--completion-promise TEXT]`

### 3b. Agent Frontmatter

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | YES | string | kebab-case identifier |
| `description` | YES | string | Triggering condition + examples block; verbose |
| `model` | NO | string | `haiku`, `sonnet`, `opus`, `inherit`; `inherit` = match parent |
| `color` | NO | string | Terminal color; no quotes needed |
| `tools` | NO | string or array | Space/comma-separated or JSON array |

**Description phrasing patterns** (two distinct styles observed):

| Style | Pattern | Example plugin |
|-------|---------|----------------|
| "Use this agent when..." | Starts with triggering condition, ends with `<example>` blocks | pr-review-toolkit, hookify, plugin-dev |
| Short declarative | One sentence describing what agent does; no examples | feature-dev, agent-sdk-dev |

**Example block format** (in agent descriptions):
```
<example>
Context: [situation]
user: "[user message]"
assistant: "[response]"
<commentary>[explanation]</commentary>
</example>
```

**Model usage across all 15 observed agents**:

| Model Value | Count | Usage pattern |
|-------------|-------|---------------|
| `inherit` | 7 | Lightweight agents (analyzers, validators, reviewers) |
| `sonnet` | 6 | Standard capability agents |
| `opus` | 2 | High-complexity agents (pr-review-toolkit: code-reviewer, code-simplifier) |

**Color usage across all 12 agents with color field**:

| Color | Count | Typical role |
|-------|-------|--------------|
| `yellow` | 4 | Analyzers, explorers |
| `green` | 3 | Code-related, reviewers |
| `cyan` | 2 | Specialized analyzers |
| `red` | 1 | Critical reviewer |
| `pink` | 1 | Type analyzer |
| `magenta` | 1 | Creator agent |

**Tools field formats observed**:
- Space-separated: `Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch, KillShell, BashOutput`
- JSON array: `["Read", "Grep", "Glob", "Bash"]`
- Both are valid; feature-dev uses comma+space-separated, plugin-dev uses JSON array

### 3c. Skill Frontmatter (SKILL.md)

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `name` | YES | string | Display name; can include spaces and Title Case |
| `description` | YES | string | Verbose; lists exact trigger phrases; third-person phrasing |
| `version` | NO | string | Semantic versioning; `0.1.0` common; not present in all skills |
| `license` | NO | string | Seen in `frontend-design` as "Complete terms in LICENSE.txt" (non-SPDX) |

**Description phrasing pattern**: "This skill should be used when the user asks to [quoted trigger phrases]..." followed by comma-separated list of exact trigger phrases in quotes.

Example:
> "This skill should be used when the user asks to 'create an agent', 'add an agent', 'write a subagent', 'agent frontmatter', 'when to use description', 'agent examples', 'agent tools', 'agent colors', 'autonomous agent', or needs guidance on agent structure..."

**Version field usage**:

| Skill | Version present |
|-------|----------------|
| hookify: writing-rules | `0.1.0` |
| plugin-dev: agent-development | `0.1.0` |
| plugin-dev: command-development | `0.2.0` |
| plugin-dev: hook-development | `0.1.0` |
| plugin-dev: mcp-integration | `0.1.0` |
| plugin-dev: plugin-settings | `0.1.0` |
| plugin-dev: plugin-structure | `0.1.0` |
| plugin-dev: skill-development | `0.1.0` |
| claude-opus-4-5-migration | none |
| frontend-design | none |

Pattern: `plugin-dev` skills consistently use version; others omit it.

---

## 4. Naming Conventions

### File Naming

| Component | Convention | Examples |
|-----------|-----------|---------|
| Command files | `kebab-case.md` | `code-review.md`, `commit-push-pr.md`, `feature-dev.md` |
| Agent files | `kebab-case.md` | `code-architect.md`, `conversation-analyzer.md` |
| Skill entry point | `SKILL.md` (UPPERCASE) | Always exactly `SKILL.md` |
| Hooks config | `hooks.json` | Always exactly `hooks.json` inside `hooks/` |
| Hook handler scripts | `kebab-case.sh` or `event-name.py` | `session-start.sh`, `pretooluse.py`, `stop.py` |

**Exception**: `clean_gone.md` uses `snake_case` (only instance; appears to be an error vs. convention).

### Directory Naming

| Directory | Convention | Notes |
|-----------|-----------|-------|
| Plugin root | `kebab-case` | Matches `name` field in `plugin.json` |
| Manifest dir | `.claude-plugin` | Fixed; always this exact name |
| Component dirs | `kebab-case` | `commands/`, `agents/`, `skills/`, `hooks/` |
| Skill named subdir | `kebab-case` | `skills/frontend-design/`, `skills/writing-rules/` |
| Resource subdirs | `kebab-case` | `references/`, `examples/`, `scripts/`, `assets/` |
| Hook handler dir | `hooks-handlers` | Hyphenated; sibling of `hooks/` |
| Python module dirs | `kebab-case` | `core/`, `matchers/`, `utils/` (hookify) |

### Agent `name` Field vs. File Name

| Practice | Observed |
|----------|---------|
| `name` field matches filename (sans `.md`) | Consistent across all agents |
| Both use kebab-case | Consistent |

### Command `name` Field

Commands do NOT have a `name` frontmatter field. The slash command name is derived from the filename (e.g., `code-review.md` → `/code-review`).

---

## 5. Notable Patterns Worth Adopting

| Pattern | Location | Description | Adoptability |
|---------|----------|-------------|--------------|
| `references/` subdirs in skills | `plugin-dev/skills/*/references/` | Supplementary docs loaded on demand; keeps SKILL.md lean; reduces context window use | HIGH — adopt immediately |
| `examples/` subdirs in skills | `plugin-dev/skills/*/examples/` | Concrete worked examples separate from reference docs | HIGH — adopt immediately |
| `scripts/` subdirs in skills | `plugin-dev/skills/*/scripts/` | Executable validation/helper scripts bundled with skill | MEDIUM — when deterministic execution needed |
| Three-level progressive disclosure | Skills design | Level 1: SKILL.md core; Level 2: `references/`; Level 3: `examples/` | HIGH — explicit design principle |
| `argument-hint` field | Commands | Documents `$ARGUMENTS` format for UX; shown in autocomplete | HIGH — low cost, high value |
| `hide-from-slash-command-tool: "true"` | ralph-wiggum commands | Hides internal/helper commands from command picker | MEDIUM — useful for internal commands |
| `disable-model-invocation: true` | command frontmatter spec | Prevents automated invocation; manual-only safety gate | MEDIUM — destructive/approval commands |
| `model: inherit` in agents | hookify, pr-review-toolkit, plugin-dev | Lightweight agents inherit parent model instead of pinning | HIGH — reduces cost for simple agents |
| `<example>` blocks in agent descriptions | pr-review-toolkit, hookify, plugin-dev | Structured trigger examples improve agent routing accuracy | HIGH — best practice per spec |
| `${CLAUDE_PLUGIN_ROOT}` variable | hooks, scripts | Portable path reference avoids hardcoded paths | HIGH — required for hooks referencing plugin files |
| `.claude-plugin/` manifest isolation | all plugins | Manifest in hidden subdir keeps plugin root clean | ALREADY ADOPTED (`.claude/`) |
| `hooks-handlers/` sibling dir | explanatory-output-style, learning-output-style | Shell scripts in separate dir from hooks config JSON | LOW — only needed for script-based hooks |
| `core/`, `matchers/`, `utils/` Python modules | hookify | Full Python package structure inside plugin | LOW — only for complex plugins with runtime code |
| Skill name in `skills/{name}/` | all plugins with skills | Skill lives in named subdirectory, not flat in `skills/` | ALREADY ADOPTED |
| Description verb-first for commands | all command files | "Create a commit" not "This command creates a commit" | ALREADY ADOPTED |
| Version `0.1.0` as initial skill version | plugin-dev skills | Signals pre-stable; bump to `1.0.0` when stable | MEDIUM — signals maturity |

---

## 6. Summary: Key Differences vs. Current Template Conventions

| Aspect | Reference Plugin Convention | Current Template Convention | Action |
|--------|---------------------------|----------------------------|--------|
| Skill resource dirs | `references/`, `examples/`, `scripts/`, `assets/` | Minimal — no consistent subdir pattern | Add `references/` and `examples/` subdirs to complex skills |
| Agent description format | Verbose triggering conditions + `<example>` blocks | Short one-liner | Expand to include triggering conditions + examples |
| Agent `model: inherit` | Used for lightweight agents | Not consistently used | Adopt `model: inherit` for simple/helper agents |
| Command `argument-hint` | Consistently used when `$ARGUMENTS` present | Inconsistent | Add to all commands accepting arguments |
| Skill `version` field | Present in plugin-dev skills | Present per SKILL.md template | Keep — already aligned |
| Skill description phrasing | Third-person "This skill should be used when..." | Variable | Standardize to third-person pattern |
| `plugin.json` location | `.claude-plugin/plugin.json` | N/A (no plugin system yet) | Reference for future plugin system |
| `hide-from-slash-command-tool` | Used for internal helper commands | Not used | Add to internal commands (e.g., sub-workflow steps) |
