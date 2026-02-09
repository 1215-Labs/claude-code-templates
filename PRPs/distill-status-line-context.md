# PRP: Context Window Status Line Hook

**Source**: `references/claude-code-hooks-mastery/.claude/status_lines/status_line_v6.py`
**Extraction ID**: EXT-006
**Priority**: 3 (Enhanced)
**Adaptation**: convention-convert
**Estimated Effort**: 4 points

## Context

The source `status_line_v6.py` (143 lines) is a UV single-file script that displays a context window usage progress bar in the Claude Code status line:

```
[Claude Opus 4] # [#######--------] | 42.5% used | ~115k left | session_id
```

It uses ANSI color codes (green/yellow/red based on usage percentage), reads `context_window` data from stdin JSON, and produces a formatted status line on stdout.

### How Status Lines Work in Claude Code

Status lines use the `Notification` hook event. Claude Code sends JSON with:
- `model.display_name` — current model name
- `session_id` — session identifier
- `context_window.used_percentage` — how much context is consumed
- `context_window.context_window_size` — total context size

The hook prints a formatted line to stdout, which Claude Code displays in its status area.

### Relationship to Our Existing Components

- We have **zero status line implementations** — this is a complete gap
- Our `Notification` hook array in hooks.json doesn't exist yet (we have an empty array)
- This would be our first status line component

## Source Code

See full source at: `references/claude-code-hooks-mastery/.claude/status_lines/status_line_v6.py` (143 lines)

Key functions:
- `get_usage_color(percentage)` — returns ANSI color code based on usage level
- `create_progress_bar(percentage, width)` — builds `[####----]` style bar
- `format_tokens(tokens)` — human-readable token count (1.5k, 2.3M)
- `generate_status_line(input_data)` — assembles the full status line
- `main()` — reads stdin JSON, outputs formatted line

## Target Conventions

### Our Hook Convention
- Shebang: `#!/usr/bin/env -S uv run --script` with PEP 723 inline deps
- Reads JSON from stdin
- Prints output to stdout
- Exit code 0 on success
- hooks.json commands use `uv run` instead of `python3`

### Notification Hook stdin format
```json
{
  "session_id": "abc-123",
  "model": {
    "display_name": "Claude Opus 4"
  },
  "context_window": {
    "used_percentage": 42.5,
    "context_window_size": 200000
  }
}
```

## Adaptation Requirements

1. **Keep UV shebang** → Use `#!/usr/bin/env -S uv run --script` with PEP 723 deps (python-dotenv optional)
2. **Add provenance comment** → `<!-- Adapted from: ... -->`
3. **Add proper docstring** — Document the Notification hook interface
4. **Add hooks.json entry** → New Notification entry using `uv run`
5. **Consider WSL2 ANSI support** → ANSI codes work in WSL2 terminals, so keep them
6. **Add to MANIFEST/REGISTRY** → New hook component

## Destination

- **File**: `.claude/hooks/status-line-context.py`
- **hooks.json**: New Notification entry

### hooks.json Entry
```json
{
  "matcher": "",
  "hooks": [
    {
      "type": "command",
      "command": "uv run ${CLAUDE_PLUGIN_ROOT}/hooks/status-line-context.py",
      "timeout": 5
    }
  ]
}
```

Note: Notification hooks may not use a matcher — check Claude Code docs for exact format. The hook should run on every notification event.

## Acceptance Criteria

- [ ] Hook reads Notification stdin JSON
- [ ] Outputs formatted status line with model name, progress bar, percentage, tokens left, session ID
- [ ] ANSI colors work correctly (green < 50%, yellow < 75%, red < 90%, bright red >= 90%)
- [ ] Progress bar width is configurable
- [ ] Uses UV shebang with PEP 723 inline deps
- [ ] hooks.json Notification array updated
- [ ] Graceful error handling (prints error status line on exception, exits 0)

## Test Plan

```bash
# Test normal usage
echo '{"session_id":"test-123","model":{"display_name":"Claude Opus 4"},"context_window":{"used_percentage":42.5,"context_window_size":200000}}' | python3 .claude/hooks/status-line-context.py
# Expected: colored status line with progress bar

# Test high usage
echo '{"session_id":"test-123","model":{"display_name":"Claude Opus 4"},"context_window":{"used_percentage":92.0,"context_window_size":200000}}' | python3 .claude/hooks/status-line-context.py
# Expected: red/critical colored status line

# Test empty input
echo '{}' | python3 .claude/hooks/status-line-context.py
# Expected: default status line, exit 0

# Test invalid JSON
echo 'not json' | python3 .claude/hooks/status-line-context.py
# Expected: error status line, exit 0
```
