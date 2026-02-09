# Reference Sync Report

**Generated**: 2026-02-09
**claude-code version**: v2.1.31 (`bd78b21`)
**skillz commit**: `d80249e`
**Mode**: quick

## Executive Summary

The official claude-code plugin repository (13 plugins) has adopted a standardized **plugin architecture** using `.claude-plugin/plugin.json` manifests, which differs fundamentally from skillz's flat `.claude/` directory structure. Key gaps include: missing plugin manifest support, no `hooks-handlers/` pattern, absence of several high-value plugins (pr-review-toolkit, security-guidance, ralph-wiggum, frontend-design), and outdated hook patterns compared to reference implementations. The most impactful improvement would be migrating to the official plugin structure for better portability and ecosystem compatibility.

## What's New Since Last Sync

Previous sync: 2026-02-07 (same claude-code version v2.1.31). No upstream changes since last sync. This report reflects an updated analysis with deeper discovery.

## Recommended Updates

### Critical Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| Plugin manifest | skillz has no `.claude-plugin/plugin.json` | Add plugin.json manifest to enable plugin discovery and versioning |
| Hook events | skillz hooks don't use official 9-event API | Align hooks.json with official format: PreToolUse, PostToolUse, Stop, SubagentStop, UserPromptSubmit, SessionStart, SessionEnd, PreCompact, Notification |
| `${CLAUDE_PLUGIN_ROOT}` | skillz hooks use hardcoded paths | Replace hardcoded paths with `${CLAUDE_PLUGIN_ROOT}` for portability |

### High Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| pr-review-toolkit | No equivalent in skillz | Adopt 6-agent PR review system: code-reviewer, code-simplifier, comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer |
| security-guidance | skillz has basic security-check.py | Adopt official security-guidance plugin with 9+ pattern detections (GH Actions injection, eval, XSS, etc.) |
| frontend-design skill | Not in skillz | Adopt for projects needing UI work - provides distinctive design guidance |
| Agent descriptions | skillz uses basic text descriptions | Adopt `<example>` blocks with Context/User/Assistant/Commentary pattern for agent trigger descriptions |
| Command `allowed-tools` | skillz commands lack tool restrictions | Add `allowed-tools` frontmatter to commands (e.g., `Bash(gh pr view:*)`) for security |

### Medium Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| plugin-dev skills | No plugin development guidance | Adopt plugin-dev toolkit with 7 skills: hook-development, skill-development, command-development, agent-development, plugin-structure, plugin-settings, mcp-integration |
| ralph-wiggum loop | No autonomous loop pattern | Adopt Stop-hook-based iteration pattern for autonomous refinement tasks |
| explanatory-output-style | No equivalent | Consider adopting SessionStart hook pattern for loading contextual style guidance |
| Skill `references/` dirs | skillz skills lack reference docs | Add `references/` and `examples/` subdirectories to skills for deep-dive documentation |
| README per plugin | skillz lacks component READMEs | Add README.md to each major component group |
| Code review command | skillz has its own code-review | Compare against official code-review plugin which uses parallel multi-model agents (haiku screening, sonnet compliance, opus bug hunting) |

### Low Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| commit-commands | skillz has no commit helper | Consider adopting structured commit workflow commands |
| claude-opus-4-5-migration | Not in skillz | Reference skill for model migration patterns |
| learning-output-style | Not in skillz | Alternative to explanatory-output for interactive learning |
| Agent `color` field | Some skillz agents lack color | Add `color` field to agent frontmatter for visual distinction |

## Pattern Comparison

### Frontmatter Conventions

#### Agents

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `name` | Required | Required | Match |
| `description` | Uses `<example>` blocks | Plain text | **Differs** - claude-code uses structured examples |
| `model` | `sonnet`, `inherit`, etc. | Present in some | Partial match |
| `color` | Required (magenta, yellow, green) | Sometimes present | **Differs** |
| `tools` | Array: `["Write", "Read"]` | Array format | Match |

#### Commands

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `description` | Required | Present | Match |
| `argument-hint` | Used in feature-dev, hookify | Rarely used | **Differs** |
| `allowed-tools` | Granular: `Bash(gh pr view:*)` | Not used | **Differs** - security gap |

#### Skills

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| `name` | Required | Required | Match |
| `description` | Uses trigger phrases | Uses trigger phrases | Match |
| `version` | Used in some | Used in some | Match |
| `license` | Used in frontend-design | Not used | Differs |
| Subdirectories | `references/`, `examples/`, `scripts/` | None | **Differs** |

### Directory Structure

| Aspect | claude-code | skillz | Status |
|--------|-------------|--------|--------|
| Root structure | `plugin-name/.claude-plugin/plugin.json` | `.claude/` flat structure | **Differs** |
| Manifest | `.claude-plugin/plugin.json` | None | **Differs** |
| Commands | `commands/*.md` | `commands/**/*.md` (nested) | Differs (skillz uses namespaces) |
| Agents | `agents/*.md` | `agents/*.md` | Match |
| Skills | `skills/*/SKILL.md` | `skills/*/SKILL.md` | Match |
| Hooks | `hooks/hooks.json` + scripts | `hooks/hooks.json` + scripts | Match |
| Hook handlers | `hooks-handlers/*.sh` | Not present | **Differs** |
| Infrastructure | `core/`, `matchers/`, `utils/` | Not present | **Differs** |
| Examples | `examples/` in plugins | Not present | **Differs** |
| Documentation | `README.md` per plugin | One main CLAUDE.md | **Differs** |

### Naming Conventions

| Aspect | claude-code | skillz | Status |
|--------|-------------|--------|--------|
| Plugin names | kebab-case | N/A (no plugins) | N/A |
| Command files | kebab-case `.md` | kebab-case `.md` | Match |
| Agent files | kebab-case `.md` | kebab-case `.md` | Match |
| Skill dirs | kebab-case | kebab-case | Match |
| Hook scripts | snake_case `.py`/`.sh` | kebab-case `.py`/`.sh` | **Differs** |

## Plugins Worth Adopting

### Tier 1 - High Value

1. **pr-review-toolkit** - 6 specialized review agents with parallel multi-model execution. Significantly more sophisticated than skillz's single code-reviewer agent. Commands: `/review-pr`.

2. **security-guidance** - Python hook detecting 9+ security anti-patterns (GH Actions injection, eval, XSS, child_process.exec, pickle, os.system). More comprehensive than skillz's `security-check.py`.

3. **plugin-dev** - 7 skills covering plugin development with examples, references, and scripts. Essential for maintaining and extending skillz itself.

### Tier 2 - Moderate Value

4. **frontend-design** - Distinctive UI design skill avoiding "AI slop" aesthetics. Useful for projects with frontend work.

5. **feature-dev** - Structured multi-phase feature development with agents for codebase exploration, architecture design, and implementation.

6. **ralph-wiggum** - Autonomous iteration pattern using Stop hooks. Novel approach for test-driven or iterative refinement tasks.

### Tier 3 - Niche Value

7. **explanatory-output-style** / **learning-output-style** - SessionStart hooks that inject behavioral guidance. Pattern is useful even if specific styles aren't needed.

8. **commit-commands** - Git workflow automation. Skillz has similar via workflow commands.

9. **agent-sdk-dev** - Agent SDK development kit. Only relevant if building custom agents outside Claude Code.

## Hook Patterns

### Official Hook Events (9 types)

| Event | Purpose | skillz Support |
|-------|---------|----------------|
| PreToolUse | Validate/modify before tool runs | Partial (pretooluse.py) |
| PostToolUse | React after tool completes | Partial (posttooluse.py) |
| Stop | Validate before session stops | Not implemented |
| SubagentStop | Validate before subagent stops | Not implemented |
| UserPromptSubmit | Process user input | Partial |
| SessionStart | Load context/environment | Implemented (session-init.py) |
| SessionEnd | Cleanup/save state | Implemented (session-summary.py) |
| PreCompact | Preserve info before compaction | Not implemented |
| Notification | React to notifications | Not implemented |

### Key Hook Patterns from Reference

1. **Command hooks** with `${CLAUDE_PLUGIN_ROOT}` paths and JSON stdin
2. **Prompt-based hooks** using LLM for context-aware validation (recommended for complex decisions)
3. **Matcher patterns**: exact (`"Write"`), OR (`"Read|Write|Edit"`), wildcard (`"*"`), regex (`"mcp__.*"`)
4. **Hook output format**: `{ "continue": true, "suppressOutput": false, "systemMessage": "..." }`
5. **PreToolUse decisions**: `{ "hookSpecificOutput": { "permissionDecision": "allow|deny|ask" } }`
6. **Stop hook blocking**: Exit code 2 + stderr for blocking, enabling iteration loops

## Action Items

### Immediate (Critical)
- [ ] Add `.claude-plugin/plugin.json` manifest with name, version, description
- [ ] Audit hooks.json format against official schema (wrapper `{ "hooks": { ... } }` format)
- [ ] Replace hardcoded paths in hook scripts with `${CLAUDE_PLUGIN_ROOT}`

### Short-term (High Priority)
- [ ] Adopt pr-review-toolkit agents (code-simplifier, silent-failure-hunter, type-design-analyzer, comment-analyzer, pr-test-analyzer)
- [ ] Upgrade security-check.py to match security-guidance plugin patterns (9+ detections)
- [ ] Add `allowed-tools` to command frontmatter for security boundaries
- [ ] Update agent descriptions to use `<example>` block format with Context/User/Assistant/Commentary
- [ ] Add Stop and SubagentStop hooks for completion validation

### Long-term (Medium/Low)
- [ ] Add `references/` and `examples/` subdirectories to skills
- [ ] Consider adopting ralph-wiggum autonomous loop pattern
- [ ] Add README.md to each major component directory
- [ ] Evaluate frontend-design skill adoption for UI-focused projects
- [ ] Implement PreCompact hook for context preservation
- [ ] Add plugin-dev skills for self-documentation
- [ ] Standardize hook script naming to snake_case (match reference)
