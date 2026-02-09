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

# UV Hook Template

## 1. Overview

Use this skill when creating or migrating Python hooks to UV single-file scripts. Each hook is self-contained, declares dependencies inline, and runs with `uv run` without manual virtual environment setup.

Claude Code hook scripts should read JSON from `stdin` with:
- `session_id`
- `tool_name`
- `tool_input`

All hooks must fail open on internal errors: catch broad exceptions and exit `0`.

## 2. PEP 723 Syntax

Use this header in every Python hook:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

Add dependencies as package strings in the `dependencies` array. UV installs and caches them automatically on first execution.

## 3. Exit Code Semantics

Use these semantics consistently:
- `0`: allow/pass
- `2`: block/reject (for blocking hook events)

For `PostToolUse`, return JSON decisions on stdout:
- Allow: `{}`
- Block: `{"decision": "block", "reason": "..."}`

For blocking hooks (`PreToolUse`, `UserPromptSubmit`), print a human-readable warning to `stderr` before `sys.exit(2)`.

## 4. Hook Event Templates

Templates are in `.claude/skills/uv-hook-template/templates/`:
- `pre-tool-use.py`: Blocking skeleton with exit code `2`
- `post-tool-use.py`: JSON decision skeleton (`{}` or block object)
- `user-prompt-submit.py`: Prompt validation/blocking skeleton
- `session-start.py`: Session bootstrap/injection skeleton
- `notification-status-line.py`: Notification/status line output skeleton

Each template includes:
- UV shebang + PEP 723 metadata
- Provenance comment header
- Input parsing (`session_id`, `tool_name`, `tool_input`)
- Session state file pattern: `/tmp/claude-<hook>-<session_id>.json`
- Fail-open exception handling (`exit 0`)

## 5. Migration Guide

### Legacy `python3` -> UV script

1. Replace shebang with `#!/usr/bin/env -S uv run --script`.
2. Add PEP 723 metadata block with `requires-python` and `dependencies`.
3. Update hook command in `.claude/hooks/hooks.json`:
   - From: `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/<hook>.py`
   - To: `uv run ${CLAUDE_PLUGIN_ROOT}/hooks/<hook>.py`
4. Keep exit semantics unchanged:
   - Blocking hooks still use `2`
   - `PostToolUse` still emits JSON decision
5. Add defensive `except Exception: sys.exit(0)` to avoid blocking on hook runtime failures.

### UV script -> Legacy `python3` (fallback)

Use only when UV is unavailable:
1. Replace shebang with `#!/usr/bin/env python3`.
2. Remove or ignore PEP 723 metadata block.
3. Install dependencies externally (venv/requirements).
4. Update `.claude/hooks/hooks.json` command back to `python3 ...`.
5. Preserve identical hook logic, state paths, and exit code behavior.

## 6. Best Practices

- Prefer zero dependencies for hook startup speed.
- Keep dependency lists explicit and minimal.
- Expect first run to be slower while UV resolves/caches dependencies.
- Pre-warm in CI/dev bootstrap by running hooks once.
- Scope state to session files in `/tmp`:
  - `/tmp/claude-<hook>-<session_id>.json`
- Never block on internal errors:
  - Catch exceptions and exit `0`
  - Reserve block behavior for explicit policy failures only
- Emit concise block reasons to help users remediate quickly.
