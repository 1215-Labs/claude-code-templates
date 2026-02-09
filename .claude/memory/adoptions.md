# Adoptions

Provenance tracking for components adopted from evaluated reference submodules.

## How This File Is Used

- **Written by**: `/reference-distill` (evaluation-to-integration engine)
- **Read by**: `/repo-equip` and `/repo-optimize` to propagate adopted patterns to other repos
- **Propagation**: After successful propagation, the `Propagated To` field is updated with the target repo name

## ADO Numbering

- Sequential: ADO-001, ADO-002, etc.
- Never reuse numbers even if records are deleted
- Parse this file for the highest existing number before appending

## Status Values

| Status | Meaning |
|--------|---------|
| `adopted` | Component extracted and integrated directly |
| `deferred-to-prp` | Complex adaptation; PRP generated for later execution |
| `propagated` | Successfully propagated to at least one other repo |

## Records

### ADO-001: dangerous-command-blocker (PRP)

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/hooks/pre_tool_use.py
- **Target Location**: .claude/hooks/dangerous-command-blocker.py
- **Adaptation**: convention-convert
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 1
- **Status**: deferred-to-prp
- **PRP**: PRPs/distill-dangerous-command-blocker.md
- **Propagated To**: []

### ADO-002: prompt-validator (PRP)

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/hooks/user_prompt_submit.py
- **Target Location**: .claude/hooks/prompt-validator.py
- **Adaptation**: convention-convert
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 1
- **Status**: deferred-to-prp
- **PRP**: PRPs/distill-prompt-validator.md
- **Propagated To**: []

### ADO-003: uv-hook-template (PRP)

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: (pattern — no single source file)
- **Target Location**: .claude/skills/uv-hook-template/
- **Adaptation**: full-rewrite
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 1
- **Status**: deferred-to-prp
- **PRP**: PRPs/distill-uv-hook-template.md
- **Propagated To**: []

### ADO-004: ruff-validator

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/hooks/validators/ruff_validator.py
- **Target Location**: .claude/hooks/ruff-validator.py
- **Adaptation**: frontmatter (UV shebang removed, hooks.json entry added)
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 2
- **Status**: adopted
- **Propagated To**: []

### ADO-005: ty-validator

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/hooks/validators/ty_validator.py
- **Target Location**: .claude/hooks/ty-validator.py
- **Adaptation**: frontmatter (UV shebang removed, hooks.json entry added)
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 2
- **Status**: adopted
- **Propagated To**: []

### ADO-006: status-line-context (PRP)

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/status_lines/status_line_v6.py
- **Target Location**: .claude/hooks/status-line-context.py
- **Adaptation**: convention-convert
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 3
- **Status**: deferred-to-prp
- **PRP**: PRPs/distill-status-line-context.md
- **Propagated To**: []

### ADO-007: meta-agent

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/agents/meta-agent.md
- **Target Location**: .claude/agents/meta-agent.md
- **Adaptation**: frontmatter (added category, related, updated tools and description)
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 3
- **Status**: adopted
- **Propagated To**: []

### ADO-008: team-builder

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/agents/team/builder.md
- **Target Location**: .claude/agents/team-builder.md
- **Adaptation**: frontmatter (added category, related, tools list; removed hooks section)
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 3
- **Status**: adopted
- **Propagated To**: []

### ADO-009: team-validator

- **Date**: 2026-02-09
- **Source Repo**: references/claude-code-hooks-mastery
- **Source File**: .claude/agents/team/validator.md
- **Target Location**: .claude/agents/team-validator.md
- **Adaptation**: frontmatter (added category, related; converted disallowedTools to tools allow-list)
- **Evaluation**: claude-code-hooks-mastery (3.50/5)
- **Priority**: 3
- **Status**: adopted
- **Propagated To**: []
