# PRP: Prompt Validator Hook

**Source**: `references/claude-code-hooks-mastery/.claude/hooks/user_prompt_submit.py`
**Extraction ID**: EXT-002
**Priority**: 1 (Core)
**Adaptation**: convention-convert
**Estimated Effort**: 5 points

## Context

The source `user_prompt_submit.py` (192 lines) implements a UserPromptSubmit hook with:
1. **Prompt logging** — logs all user prompts to `logs/user_prompt_submit.json`
2. **Session data management** — tracks prompts per session in `.claude/data/sessions/<id>.json`
3. **Agent naming** — generates agent names via Ollama/Anthropic API calls
4. **Prompt validation** — validates prompts against blocked patterns (framework exists, patterns empty)

The session tracking and agent naming features are heavily coupled to their ecosystem (Ollama, Anthropic direct calls, dotenv, argparse). The core value for us is the **prompt validation framework** and the **session activity tracking** pattern.

### Relationship to Our Existing Components

- Our `UserPromptSubmit` hook array in hooks.json is currently **empty** (`[]`) — this is a complete gap
- We have `memory/sessions/` for session summaries (written at Stop), but no real-time prompt tracking
- We have no prompt validation layer

## Source Code

See full source at: `references/claude-code-hooks-mastery/.claude/hooks/user_prompt_submit.py` (192 lines)

Key functions:
- `log_user_prompt()` — logs to `logs/user_prompt_submit.json`
- `manage_session_data()` — tracks prompts in `.claude/data/sessions/<id>.json`, optional agent naming via Ollama/Anthropic
- `validate_prompt()` — checks against blocked patterns (currently empty pattern list)
- `main()` — argparse with `--validate`, `--log-only`, `--store-last-prompt`, `--name-agent` flags

## Target Conventions

### Our Hook Convention
- Shebang: `#!/usr/bin/env -S uv run --script` with PEP 723 inline deps
- Reads JSON from stdin: `session_id`, `prompt`
- Exit code 0 = allow prompt, exit code 2 = block prompt
- Print additional context to stdout (appended to prompt)
- No external API dependencies (no Ollama, no direct Anthropic calls)
- No argparse — hooks receive input via stdin JSON only
- hooks.json commands use `uv run` instead of `python3`

### UserPromptSubmit stdin format
```json
{
  "session_id": "abc-123",
  "prompt": "the user's prompt text"
}
```

## Adaptation Requirements

1. **Keep UV shebang** → Use `#!/usr/bin/env -S uv run --script` with PEP 723 inline deps (dotenv can be listed as optional dep)
2. **Remove argparse** → Hooks don't receive CLI args; all input comes via stdin JSON
3. **Remove Ollama/Anthropic agent naming** → Not applicable to our ecosystem
4. **Remove file logging to `logs/`** → We don't log prompts to disk
5. **Simplify session tracking** → Track prompt count per session in `/tmp/claude-prompt-state-{session_id}.json` (like our security-check.py pattern). Don't create `.claude/data/sessions/` directory.
6. **Expand validation patterns** → Add useful blocked patterns:
   - Extremely long prompts (>50,000 chars) — likely accidental paste
   - Prompts containing only whitespace
   - Known injection attempts (e.g., "ignore previous instructions")
7. **Add context injection** → Print useful context to stdout:
   - Prompt number in session (e.g., "Prompt #5 in this session")
   - Session duration if available
8. **Add provenance comment** → `<!-- Adapted from: ... -->`
9. **Add hooks.json entry** → New UserPromptSubmit entry using `uv run`

## Destination

- **File**: `.claude/hooks/prompt-validator.py`
- **hooks.json**: New UserPromptSubmit entry (currently empty array)

## Acceptance Criteria

- [ ] Hook reads stdin JSON with `session_id` and `prompt`
- [ ] Hook validates prompt (blocks empty/whitespace-only, extremely long)
- [ ] Hook tracks prompt count per session
- [ ] Exit code 2 on block, 0 on allow
- [ ] Uses UV shebang with PEP 723 inline deps; no Ollama/Anthropic/argparse dependencies
- [ ] hooks.json UserPromptSubmit array updated
- [ ] Graceful error handling (exit 0 on any exception)

## Test Plan

```bash
# Test normal prompt
echo '{"session_id":"test","prompt":"Hello, help me with this code"}' | python3 .claude/hooks/prompt-validator.py
# Expected: exit code 0

# Test empty prompt
echo '{"session_id":"test","prompt":""}' | python3 .claude/hooks/prompt-validator.py
# Expected: exit code 2

# Test whitespace-only prompt
echo '{"session_id":"test","prompt":"   \n  "}' | python3 .claude/hooks/prompt-validator.py
# Expected: exit code 2

# Test extremely long prompt (>50k chars)
python3 -c "import json; print(json.dumps({'session_id':'test','prompt':'x'*60000}))" | python3 .claude/hooks/prompt-validator.py
# Expected: exit code 2 with warning
```
