# PRP: Dangerous Command Blocker Hook

**Source**: `references/claude-code-hooks-mastery/.claude/hooks/pre_tool_use.py`
**Extraction ID**: EXT-001
**Priority**: 1 (Core)
**Adaptation**: convention-convert
**Estimated Effort**: 4 points

## Context

The source `pre_tool_use.py` (139 lines) implements two PreToolUse protections:
1. **Dangerous `rm` command blocking** — comprehensive regex detection of `rm -rf` variants targeting dangerous paths
2. **`.env` file access protection** — blocks Read/Edit/Write/Bash access to `.env` files (allows `.env.sample`)

It also logs all tool calls to `logs/pre_tool_use.json` (not needed for our use case).

### Relationship to Our Existing Components

We already have `security-check.py` (163 lines) which is a PreToolUse hook that:
- Checks for 9 code-level security anti-patterns (eval, exec, XSS, pickle, etc.)
- Tracks warned patterns per session to avoid repetition
- Blocks on first occurrence, allows on repeat

**There is NO overlap** between the two hooks:
- `security-check.py` → scans **code content** being written/edited for security anti-patterns
- `pre_tool_use.py` → scans **tool commands** for dangerous operations (rm -rf, .env access)

These are complementary and should both run as PreToolUse hooks.

## Source Code

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

import json
import sys
import re
from pathlib import Path

def is_dangerous_rm_command(command):
    """Comprehensive detection of dangerous rm commands."""
    normalized = ' '.join(command.lower().split())

    patterns = [
        r'\brm\s+.*-[a-z]*r[a-z]*f',
        r'\brm\s+.*-[a-z]*f[a-z]*r',
        r'\brm\s+--recursive\s+--force',
        r'\brm\s+--force\s+--recursive',
        r'\brm\s+-r\s+.*-f',
        r'\brm\s+-f\s+.*-r',
    ]

    for pattern in patterns:
        if re.search(pattern, normalized):
            return True

    dangerous_paths = [
        r'/', r'/\*', r'~', r'~/', r'\$HOME',
        r'\.\.', r'\*', r'\.', r'\.\s*$',
    ]

    if re.search(r'\brm\s+.*-[a-z]*r', normalized):
        for path in dangerous_paths:
            if re.search(path, normalized):
                return True

    return False

def is_env_file_access(tool_name, tool_input):
    """Check if any tool is trying to access .env files."""
    if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write', 'Bash']:
        if tool_name in ['Read', 'Edit', 'MultiEdit', 'Write']:
            file_path = tool_input.get('file_path', '')
            if '.env' in file_path and not file_path.endswith('.env.sample'):
                return True
        elif tool_name == 'Bash':
            command = tool_input.get('command', '')
            env_patterns = [
                r'\b\.env\b(?!\.sample)',
                r'cat\s+.*\.env\b(?!\.sample)',
                r'echo\s+.*>\s*\.env\b(?!\.sample)',
                r'touch\s+.*\.env\b(?!\.sample)',
                r'cp\s+.*\.env\b(?!\.sample)',
                r'mv\s+.*\.env\b(?!\.sample)',
            ]
            for pattern in env_patterns:
                if re.search(pattern, command):
                    return True
    return False

def main():
    try:
        input_data = json.load(sys.stdin)
        tool_name = input_data.get('tool_name', '')
        tool_input = input_data.get('tool_input', {})

        if is_env_file_access(tool_name, tool_input):
            print("BLOCKED: Access to .env files containing sensitive data is prohibited", file=sys.stderr)
            print("Use .env.sample for template files instead", file=sys.stderr)
            sys.exit(2)

        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            if is_dangerous_rm_command(command):
                print("BLOCKED: Dangerous rm command detected and prevented", file=sys.stderr)
                sys.exit(2)

        # [logging to logs/ removed — not needed]
        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == '__main__':
    main()
```

## Target Conventions

### Our Hook Convention (exemplar: `security-check.py`)
- Shebang: `#!/usr/bin/env -S uv run --script` with PEP 723 inline deps
- Reads JSON from stdin: `session_id`, `tool_name`, `tool_input`
- Exit code 0 = allow, exit code 2 = block
- Print warning/error message to stdout before blocking
- Per-session state tracking in `/tmp/claude-*-{session_id}.json`
- No file logging (we don't log tool calls to disk)
- Uses `${CLAUDE_PLUGIN_ROOT}` in hooks.json paths
- hooks.json commands use `uv run` instead of `python3`

### hooks.json Entry Pattern
```json
{
  "matcher": "Bash|Read|Edit|Write|MultiEdit",
  "hooks": [
    {
      "type": "command",
      "command": "uv run ${CLAUDE_PLUGIN_ROOT}/hooks/dangerous-command-blocker.py",
      "timeout": 10
    }
  ]
}
```

## Adaptation Requirements

1. **Keep UV shebang** → Use `#!/usr/bin/env -S uv run --script` with PEP 723 inline deps (no external deps needed for this hook)
2. **Remove file logging** → Strip the entire `logs/` directory creation and JSON logging block
3. **Add session state tracking** → Track which warnings have been shown (like security-check.py) to avoid blocking the same pattern twice per session
4. **Add proper docstring** → Match security-check.py format (Input/Output/Exit codes documentation)
5. **Add provenance comment** → `<!-- Adapted from: references/claude-code-hooks-mastery/.claude/hooks/pre_tool_use.py on YYYY-MM-DD -->`
6. **Widen matcher** → This hook should run on `Bash|Read|Edit|Write|MultiEdit` (not just Bash) since .env protection covers file tools too
7. **Add hooks.json entry** → New PreToolUse entry using `uv run` in hooks.json

## Destination

- **File**: `.claude/hooks/dangerous-command-blocker.py`
- **hooks.json**: New PreToolUse entry with matcher `Bash|Read|Edit|Write|MultiEdit`

## Acceptance Criteria

- [ ] Hook blocks `rm -rf /` and variants (test with stdin JSON)
- [ ] Hook blocks `.env` file access (test with Read tool input)
- [ ] Hook allows `.env.sample` access
- [ ] Hook allows normal Bash commands
- [ ] Exit code 2 on block, 0 on allow
- [ ] Uses UV shebang with PEP 723 inline deps
- [ ] hooks.json updated with new entry
- [ ] Per-session state tracking prevents duplicate blocks

## Test Plan

```bash
# Test dangerous rm blocking
echo '{"session_id":"test","tool_name":"Bash","tool_input":{"command":"rm -rf /"}}' | python3 .claude/hooks/dangerous-command-blocker.py
# Expected: exit code 2

# Test .env blocking
echo '{"session_id":"test","tool_name":"Read","tool_input":{"file_path":".env"}}' | python3 .claude/hooks/dangerous-command-blocker.py
# Expected: exit code 2

# Test .env.sample allowed
echo '{"session_id":"test","tool_name":"Read","tool_input":{"file_path":".env.sample"}}' | python3 .claude/hooks/dangerous-command-blocker.py
# Expected: exit code 0

# Test normal command allowed
echo '{"session_id":"test","tool_name":"Bash","tool_input":{"command":"ls -la"}}' | python3 .claude/hooks/dangerous-command-blocker.py
# Expected: exit code 0
```
