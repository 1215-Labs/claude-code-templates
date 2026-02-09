# AGENTS.md — PRP Execution Context

## Active PRP

**Name**: {PRP_NAME}
**Source**: {SOURCE_FILE_PATH}
**Destination**: {DESTINATION_PATH}
**Adaptation Type**: {ADAPTATION_TYPE}

## Exemplar Files

Match your implementation style to these existing hooks:

- `.claude/hooks/security-check.py` — PreToolUse hook with session state tracking
- `.claude/hooks/ruff-validator.py` — PostToolUse hook with UV shebang + PEP 723

## Checklist

Before outputting your final JSON:

1. Created all files listed in the PRP Destination section
2. Updated `.claude/hooks/hooks.json` (if applicable) — added to existing array
3. Used UV shebang: `#!/usr/bin/env -S uv run --script`
4. Added PEP 723 `# /// script` block
5. Added provenance comment: `# Adapted from: ... on YYYY-MM-DD`
6. Ran every test from the Test Plan
7. Verified every Acceptance Criterion
