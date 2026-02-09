# PRP: UV Hook Template Skill

**Source**: Pattern from `references/claude-code-hooks-mastery` (UV single-file script architecture)
**Extraction ID**: EXT-003
**Priority**: 1 (Core)
**Adaptation**: full-rewrite
**Estimated Effort**: 4 points

## Context

The `claude-code-hooks-mastery` repo uses UV single-file scripts (`#!/usr/bin/env -S uv run --script` with PEP 723 inline deps) for all hooks. This solves hook portability — hooks are self-contained with no venv management required.

UV single-file scripts with PEP 723 inline deps are our **preferred convention** for all Python hooks. This skill documents the pattern and provides templates for each hook event type.

### What Is UV Single-File Script?

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "requests",
#     "python-dotenv",
# ]
# ///
```

PEP 723 inline metadata allows declaring Python version and pip dependencies directly in the script. UV reads this metadata and auto-installs dependencies on first run.

## Adaptation Requirements

This is a **full-rewrite** — no single source file to copy. Generate a new skill that:

1. **Documents the UV pattern** — PEP 723 syntax, exit code semantics, stdin JSON format
2. **Provides hook skeleton templates** for each event type:
   - PreToolUse (blocking)
   - PostToolUse (JSON decision)
   - UserPromptSubmit
   - SessionStart
   - Notification (status line)
3. **Includes a migration guide** — how to convert legacy `python3` hooks to UV
4. **Documents best practices** — dependency declaration, caching, first-run behavior

## Destination

- **Skill directory**: `.claude/skills/uv-hook-template/`
- **Main file**: `.claude/skills/uv-hook-template/SKILL.md`
- **Templates subdirectory**: `.claude/skills/uv-hook-template/templates/`
  - `pre-tool-use.py` — PreToolUse skeleton
  - `post-tool-use.py` — PostToolUse skeleton with JSON decision
  - `user-prompt-submit.py` — UserPromptSubmit skeleton
  - `session-start.py` — SessionStart skeleton
  - `notification-status-line.py` — Notification/status line skeleton

## SKILL.md Structure

```yaml
---
name: uv-hook-template
description: UV single-file script templates for Claude Code hooks with PEP 723 inline dependencies
version: 1.0.0
category: development
user-invocable: false
related:
  skills: [reference-distill]
  commands: []
  hooks: [ruff-validator, ty-validator, security-check, lsp-type-validator]
---
```

### Sections

1. **Overview** — What UV hooks are, when to use them
2. **PEP 723 Syntax** — The `# /// script` metadata format
3. **Exit Code Semantics** — 0=allow, 2=block, JSON decision format for PostToolUse
4. **Hook Event Templates** — Link to each template with usage notes
5. **Migration Guide** — converting legacy python3 hooks to UV
6. **Best Practices** — dependency caching, first-run warmup, error handling

## Acceptance Criteria

- [ ] SKILL.md with proper frontmatter and all sections
- [ ] 5 template files in `templates/` subdirectory
- [ ] Each template is a complete, runnable hook skeleton
- [ ] Templates use the `# /// script` PEP 723 format
- [ ] Conversion guide covers both directions
- [ ] MANIFEST.json entry added
- [ ] REGISTRY.md updated

## Test Plan

```bash
# Verify templates are syntactically valid Python
python3 -c "import py_compile; py_compile.compile('.claude/skills/uv-hook-template/templates/pre-tool-use.py', doraise=True)"
# Repeat for each template

# Verify SKILL.md frontmatter
head -10 .claude/skills/uv-hook-template/SKILL.md
# Should show valid YAML frontmatter
```
