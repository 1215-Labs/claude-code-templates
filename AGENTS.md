# AGENTS.md

Project instructions for Codex CLI when working in this repository.

## Repository

Claude Code configuration template library — reusable `.claude/` folder components (agents, commands, skills, hooks, workflows) that can be copied into other projects.

## Python Hook Conventions

All Python hooks live in `.claude/hooks/` and follow these rules:

- **Shebang**: `#!/usr/bin/env -S uv run --script`
- **Dependencies**: PEP 723 inline metadata (`# /// script` block)
- **Input**: JSON from stdin with fields: `session_id`, `tool_name`, `tool_input`
- **Exit codes**: `0` = allow/pass, `2` = block/reject
- **Warnings**: Print to stderr before `sys.exit(2)`
- **Session state**: `/tmp/claude-{hook-name}-{session_id}.json` (no disk logging)
- **Error handling**: Catch all exceptions, exit 0 (never block on error)

### PEP 723 Template

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
```

## hooks.json Format

Path: `.claude/hooks/hooks.json`

- Commands use `uv run` (not `python3`): `uv run ${CLAUDE_PLUGIN_ROOT}/hooks/<name>.py`
- `${CLAUDE_PLUGIN_ROOT}` resolves to `.claude/`
- Matchers: `Bash`, `Edit`, `Write`, `Read`, `MultiEdit`, or pipe-separated: `Bash|Read|Edit|Write|MultiEdit`
- Hook types: `command` (shell execution) or `prompt` (text injection)

### Entry Pattern

```json
{
  "matcher": "Bash|Read|Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "uv run ${CLAUDE_PLUGIN_ROOT}/hooks/<hook-name>.py",
      "timeout": 10
    }
  ]
}
```

**Important**: Read `.claude/hooks/hooks.json` before modifying. Add entries to existing arrays — never overwrite.

## Component Registration

After creating new components:

1. **MANIFEST.json** (repo root): Add entry with `name`, `path`, `deployment`, `status`, `description`
2. **REGISTRY.md** (`.claude/REGISTRY.md`): Add Quick Lookup row and category section entry

## Testing & Validation

After implementation:

1. Run test commands from the PRP Test Plan section
2. Run: `python3 scripts/validate-docs.py` (must exit 0)
3. Run: `python3 scripts/install-global.py --dry-run` (verify symlinks)

## Directory Structure

```
.claude/
├── agents/       # Sub-agent definitions (YAML frontmatter + system prompt)
├── commands/     # Slash commands (markdown with $ARGUMENTS)
├── skills/       # Reusable knowledge (SKILL.md + subdirectories)
├── hooks/        # Automated checks (hooks.json + Python scripts)
├── workflows/    # Multi-step sequences
└── rules/        # Development rules

scripts/          # Repo management scripts
PRPs/             # Prompt Request Protocol documents
references/       # Git submodules (read-only reference)
```

## Coding Style

- Prefer editing existing files over creating new ones
- Match the style of neighboring code
- No unnecessary abstractions — keep it simple
- No docstrings/comments on code you didn't change
