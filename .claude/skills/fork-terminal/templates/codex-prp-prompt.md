# PRP Execution Task

You are executing a PRP (Prompt Request Protocol) document. Implement everything specified, run the test plan, and report results as structured JSON.

## Execution Protocol

1. **Read** the full PRP below — understand context, source code, adaptation requirements, and destination
2. **Implement** all files specified in the Destination section
3. **Apply** every adaptation requirement listed
4. **Update hooks.json** if the PRP specifies a hooks.json entry — read the file first, add to existing arrays
5. **Run** every command in the Test Plan section and record the exit code + output
6. **Verify** every Acceptance Criterion — mark each as met or not met
7. **Output** your final message as JSON matching the output schema

## Critical Conventions

- Python hooks MUST use UV shebang: `#!/usr/bin/env -S uv run --script`
- PEP 723 inline deps in `# /// script` block (even if no external deps)
- hooks.json commands use: `uv run ${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py`
- Hook exit codes: 0 = allow, 2 = block
- Provenance header as Python comment: `# Adapted from: <source> on <date>`
- Per-session state files: `/tmp/claude-<hook>-<session_id>.json`
- Error handling: catch all exceptions, exit 0 (never block on internal error)

## Important

- Read `.claude/hooks/hooks.json` BEFORE modifying it — add entries, don't overwrite
- Match the coding style of existing hooks in `.claude/hooks/`
- Test commands may use `python3` or `uv run` — both work for our UV-shebanged scripts
- Your final message MUST be valid JSON — no markdown, no commentary, just the JSON object

---

## PRP Content

{PRP_CONTENT}
