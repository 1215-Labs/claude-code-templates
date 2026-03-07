# Hook Implementations and New Features — claude-code plugins/
**Source**: `/home/mdc159/projects/claude-code-templates/references/claude-code/plugins/`
**Date**: 2026-03-05
**Scope**: Hooks and new API features only (frontmatter conventions excluded)

---

## 1. Hook Event Types Across All Plugins

| Event | Plugins Using It | Example Matchers Used |
|-------|-----------------|----------------------|
| `PreToolUse` | hookify, security-guidance | `*` (none), `Edit\|Write\|MultiEdit` |
| `PostToolUse` | hookify | `*` (none) |
| `Stop` | hookify, ralph-wiggum | `*` (none) |
| `UserPromptSubmit` | hookify | `*` (none) |
| `SessionStart` | explanatory-output-style, learning-output-style | `*` (none) |

**Notes**:
- `hookify` covers the widest surface: PreToolUse, PostToolUse, Stop, UserPromptSubmit
- `security-guidance` uses `matcher: "Edit|Write|MultiEdit"` on PreToolUse — the only plugin to use a non-wildcard matcher in production hooks
- `ralph-wiggum` uses Stop exclusively to implement a self-continuation loop
- `explanatory-output-style` and `learning-output-style` both use SessionStart exclusively
- Events defined in the official validator but **not used by any plugin** in this set: `SubagentStop`, `SessionEnd`, `PreCompact`, `Notification`

### Event Counts

| Event | # Plugins | Plugin Names |
|-------|-----------|-------------|
| PreToolUse | 2 | hookify, security-guidance |
| PostToolUse | 1 | hookify |
| Stop | 2 | hookify, ralph-wiggum |
| UserPromptSubmit | 1 | hookify |
| SessionStart | 2 | explanatory-output-style, learning-output-style |

---

## 2. New Hook API Features

### 2a. `updatedInput` Middleware

| Aspect | Detail |
|--------|--------|
| What it is | `hookSpecificOutput.updatedInput` field in PreToolUse response — lets a hook modify tool input before it executes |
| Plugins using it | Documented in SKILL.md and pattern references; no plugin in this set implements it yet |
| Where documented | `plugin-dev/skills/hook-development/SKILL.md` line 148 |

**Schema** (from SKILL.md):
```json
{
  "hookSpecificOutput": {
    "permissionDecision": "allow|deny|ask",
    "updatedInput": {"field": "modified_value"}
  },
  "systemMessage": "Explanation for Claude"
}
```

**Significance**: Enables hooks to act as input-sanitization middleware (e.g., strip secrets, normalize paths) before Claude executes the tool. Not yet used in any plugin implementation.

---

### 2b. `permissionDecision: "ask"` (PermissionRequest event)

| Aspect | Detail |
|--------|--------|
| What it is | Third option alongside `"allow"` and `"deny"` — surfaces a human confirmation dialog |
| Plugins implementing it | `plugin-dev/skills/hook-development/examples/validate-bash.sh`, `validate-write.sh` |
| Production plugins | None (only in example scripts) |

**Example from validate-bash.sh**:
```bash
# Privilege escalation → ask user, don't auto-deny
if [[ "$command" == sudo* ]] || [[ "$command" == su* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "ask"}, "systemMessage": "Command requires elevated privileges"}' >&2
  exit 2
fi
```

**Example from validate-write.sh**:
```bash
# Sensitive files → ask, not deny
if [[ "$file_path" == *.env ]] || [[ "$file_path" == *secret* ]]; then
  echo '{"hookSpecificOutput": {"permissionDecision": "ask"}, "systemMessage": "Writing to potentially sensitive file"}' >&2
  exit 2
fi
```

**Three-value permission model**:
| Value | Behavior |
|-------|----------|
| `"allow"` | Proceed without interruption |
| `"deny"` | Block operation, send `systemMessage` to Claude |
| `"ask"` | Pause and surface confirmation dialog to human |

---

### 2c. `once: true` (Run-once hooks)

| Aspect | Detail |
|--------|--------|
| What it is | A flag to make a hook fire only once per session |
| Plugins using it | None found in this plugin set |
| Status | Referenced in validator tooling but not in any hooks.json |

**Not observed in any plugin**. The `security_reminder_hook.py` achieves the same effect manually via session-scoped state files in `~/.claude/security_warnings_state_{session_id}.json`.

---

### 2d. `additionalContext` (SessionStart output)

| Aspect | Detail |
|--------|--------|
| What it is | `hookSpecificOutput.additionalContext` — string injected into Claude's system context at session start |
| Plugins using it | `explanatory-output-style`, `learning-output-style` |

**How explanatory-output-style uses it** (`hooks-handlers/session-start.sh`):
```bash
cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "You are in 'explanatory' output style mode ... ## Insights\n..."
  }
}
EOF
```

**How learning-output-style uses it**: Identical structure, larger prompt describing interactive learning mode (when to request user code contributions, how to frame requests, etc.).

**Key pattern**: These plugins use SessionStart + additionalContext to replace what were previously built-in "output style" modes in Claude Code (described as "deprecated" and "unshipped" respectively in the plugin.json descriptions). The hook mechanism is being used as a **backwards-compatibility shim** for removed product features.

**additionalContext vs systemMessage**:
| Field | Scope | Used in |
|-------|-------|---------|
| `systemMessage` | Shown as a feedback message to Claude mid-session | PreToolUse, PostToolUse, Stop responses |
| `additionalContext` | Injected into system prompt at session start | SessionStart `hookSpecificOutput` only |

---

### 2e. `Setup` Event (SessionStart as setup mechanism)

| Aspect | Detail |
|--------|--------|
| What it is | `SessionStart` hook with `$CLAUDE_ENV_FILE` for persisting env vars across the session |
| Plugins using it | explanatory-output-style, learning-output-style (additionalContext path); load-context.sh example (env-file path) |

**Two SessionStart output patterns observed**:

Pattern A — `additionalContext` (explanatory-output-style, learning-output-style):
```json
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "..."
  }
}
```

Pattern B — `$CLAUDE_ENV_FILE` (example scripts only):
```bash
# Detect project type and persist as env var for the session
echo "export PROJECT_TYPE=nodejs" >> "$CLAUDE_ENV_FILE"
```

No production plugin currently uses the `$CLAUDE_ENV_FILE` pattern.

---

## 3. Hookify Plugin — Markdown-Based Rule Engine

### Overview

| Attribute | Value |
|-----------|-------|
| Author | Daisy Hollman (daisy@anthropic.com) |
| Purpose | User-configurable hooks without writing Python/bash — rules defined as markdown files |
| Rule file format | `.claude/hookify.*.local.md` (YAML frontmatter + markdown body) |
| Events handled | PreToolUse, PostToolUse, Stop, UserPromptSubmit |

### Rule File Schema

Each rule is a single `.local.md` file with YAML frontmatter:

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `name` | string | any | Rule identifier shown in messages |
| `enabled` | bool | true/false | Toggle rule without deleting file |
| `event` | string | `bash`, `file`, `stop`, `prompt`, `all` | Which hook event to match |
| `action` | string | `warn`, `block` | warn = systemMessage only; block = deny operation |
| `pattern` | string (legacy) | regex | Simple mode: single regex applied to inferred field |
| `conditions` | list | see below | Advanced mode: explicit field/operator/pattern triples |
| `tool_matcher` | string | `Bash`, `Edit\|Write`, `*` | Override default tool matching |

**Condition object fields**:

| Field | Values | Description |
|-------|--------|-------------|
| `field` | `command`, `file_path`, `new_text`, `old_text`, `content`, `reason`, `transcript`, `user_prompt` | Which part of tool input to inspect |
| `operator` | `regex_match`, `contains`, `equals`, `not_contains`, `starts_with`, `ends_with` | Match strategy |
| `pattern` | string | The pattern to test against |

### Example Rules

**Block dangerous rm (simple/legacy pattern)**:
```markdown
---
name: block-dangerous-rm
enabled: true
event: bash
pattern: rm\s+-rf
action: block
---

Dangerous rm command detected! Please verify path, consider safer approach, make sure you have backups.
```

**Warn on sensitive files (advanced conditions)**:
```markdown
---
name: warn-sensitive-files
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: \.env$|\.env\.|credentials|secrets
---

Sensitive file detected — ensure credentials are not hardcoded, use env vars, verify .gitignore.
```

**Block stop if no tests run (Stop event + transcript field)**:
```markdown
---
name: require-tests-run
enabled: false
event: stop
action: block
conditions:
  - field: transcript
    operator: not_contains
    pattern: npm test|pytest|cargo test
---

Tests not detected in transcript! Run tests before stopping.
```

### Rule Engine Architecture

```
.claude/hookify.*.local.md files
        |
        v
config_loader.py::load_rules(event=)
  - glob pattern match
  - YAML frontmatter parse (custom parser, no PyYAML dependency)
  - filter by event and enabled=true
  - return List[Rule]
        |
        v
rule_engine.py::RuleEngine.evaluate_rules(rules, input_data)
  - for each rule: _rule_matches()
    - optional tool_matcher check (exact or |-separated OR)
    - all conditions must pass (AND logic)
    - _check_condition(): extract field, apply operator
  - accumulate blocking_rules, warning_rules
  - blocking_rules take priority over warning_rules
        |
        v
Response JSON
  - Stop event: {"decision": "block", "reason": ..., "systemMessage": ...}
  - PreToolUse/PostToolUse: {"hookSpecificOutput": {"hookEventName": ..., "permissionDecision": "deny"}, "systemMessage": ...}
  - Warning only: {"systemMessage": ...}
  - No match: {} (empty, allow)
```

### Rule Engine Design Decisions

| Decision | Implementation |
|----------|---------------|
| Regex caching | `@lru_cache(maxsize=128)` on compiled patterns |
| Custom YAML parser | Avoids PyYAML dependency; handles `---` frontmatter with multi-line list items |
| Error safety | All file I/O errors logged to stderr, hook exits 0 (never blocks due to hook error) |
| Priority | Block rules always take priority over warn rules; all matching messages combined |
| Condition logic | All conditions within a rule are AND; multiple rules are evaluated independently |
| Event→field inference | `bash` event → `command` field; `file` event → `new_text` field (legacy pattern mode) |
| Transcript access | `stop` event with `field: transcript` reads the transcript file from `transcript_path` |

### Hookify vs Direct Hook Scripts (Comparison)

| Aspect | hookify | Direct Script (security-guidance) |
|--------|---------|----------------------------------|
| Rule authoring | Markdown files, no Python needed | Hardcoded in Python/bash |
| Adding new rules | Create new `.local.md` file | Edit script, requires coding |
| Per-user customization | Yes — `.local.md` per-project | No — rules are plugin-global |
| Disabling a rule | `enabled: false` in frontmatter | Comment out code |
| Rule scope | Regex/field matching | Substring + path lambda matching |
| Action granularity | warn or block | block or allow (binary) |
| Session state | None | JSON state file per session_id |
| Transcript inspection | Yes (`field: transcript`) | No |

---

## 4. Hook Architecture Comparison

| Plugin | Script Language | State Management | Security Pattern | Rule Engine |
|--------|----------------|-----------------|-----------------|-------------|
| **hookify** | Python 3 | None (stateless per invocation) | Regex/field matching on tool input | Markdown frontmatter rules; custom YAML parser; LRU-cached regex |
| **security-guidance** | Python 3 | Session-scoped JSON file (`~/.claude/security_warnings_state_{id}.json`); auto-cleanup at 30 days | Substring scan on file content + path lambda checks; show-once-per-file-per-rule per session | Hardcoded SECURITY_PATTERNS list; 8 rules covering GitHub Actions injection, eval, innerHTML, pickle, os.system, etc. |
| **ralph-wiggum** | bash + jq | `.claude/ralph-loop.local.md` (YAML frontmatter with `iteration`, `max_iterations`, `completion_promise`) | Stop hook reads transcript JSONL; extracts last assistant message; checks `<promise>` tags | No rule engine — single loop-continuation logic; blocks Stop and re-feeds prompt back to Claude |
| **explanatory-output-style** | bash | None | N/A | N/A — only outputs `additionalContext` string |
| **learning-output-style** | bash | None | N/A | N/A — only outputs `additionalContext` string |
| **plugin-dev examples** | bash | Temp files (`/tmp/hook-state-$$`, `/tmp/hook-cache-$HASH`) | Path traversal check, system dir block, pattern detection | None — example scripts only; show rate limiting, caching, audit logging patterns |

### Security Pattern Catalog (security-guidance plugin)

| Rule Name | Detection Method | Action |
|-----------|-----------------|--------|
| `github_actions_workflow` | Path: `.github/workflows/*.yml` | Warn about CI injection |
| `child_process_exec` | Substring: `child_process.exec`, `execSync(` | Warn, suggest execFileNoThrow |
| `new_function_injection` | Substring: `new Function` | Warn |
| `eval_injection` | Substring: `eval(` | Warn |
| `react_dangerously_set_html` | Substring: `dangerouslySetInnerHTML` | Warn |
| `document_write_xss` | Substring: `document.write` | Warn |
| `innerHTML_xss` | Substring: `.innerHTML =`, `.innerHTML=` | Warn |
| `pickle_deserialization` | Substring: `pickle` | Warn |
| `os_system_injection` | Substring: `os.system` | Warn |

### Exit Code Convention (across all plugins)

| Exit Code | Meaning | Used By |
|-----------|---------|---------|
| `0` | Allow / no action | All |
| `2` | Block / deny (stderr → Claude context) | security-guidance, plugin-dev examples |
| `0` + JSON stdout | Structured response (allow, warn, or block via JSON) | hookify, ralph-wiggum |

**Two blocking mechanisms observed**:
1. Exit 2 + stderr message (security-guidance, example scripts) — older pattern
2. Exit 0 + JSON `{"hookSpecificOutput": {"permissionDecision": "deny"}}` stdout — newer structured pattern (hookify)

---

## 5. New Component Types and Capabilities Not Commonly Seen

### 5a. Plugin System (`plugin.json` + `hooks/hooks.json` wrapper)

| Feature | Detail |
|---------|--------|
| Plugin manifest | `.claude-plugin/plugin.json` with `name`, `version`, `description`, `author` |
| Hook wrapper format | `hooks/hooks.json` uses `{"description": "...", "hooks": {...}}` wrapper — distinct from user settings format which uses events directly at top level |
| `$CLAUDE_PLUGIN_ROOT` | Plugin-scoped env var; expands to absolute plugin directory path at runtime; used in all hook command strings |
| Auto-discovery | Commands in `commands/` subdirectory auto-registered; agents in `agents/`; skills in `skills/` |
| Namespaced commands | Subdirectories create command namespaces: `commands/review/security.md` → `/security (plugin:name:review)` |

### 5b. Stop Hook as Loop Controller (ralph-wiggum)

| Feature | Detail |
|---------|--------|
| Mechanism | Stop hook reads transcript JSONL, extracts last assistant message text, feeds it back as `"reason"` to block stop |
| State file | `.claude/ralph-loop.local.md` tracks `iteration`, `max_iterations`, `completion_promise` |
| Completion detection | Looks for `<promise>TAG</promise>` XML tag in Claude's last response; uses Perl for multiline extraction |
| Safety | Validates numeric fields before arithmetic; removes state file on corruption or completion; hard max_iterations limit |
| JSON output | `{"decision": "block", "reason": "<prompt>", "systemMessage": "<iteration info>"}` |

This is the only plugin that uses the Stop hook's `"reason"` field as **input back to Claude** rather than as a human-readable explanation.

### 5c. Markdown-as-Config Rule Files (hookify)

| Feature | Detail |
|---------|--------|
| File glob | `.claude/hookify.*.local.md` — uses `.local.md` convention to signal user-local, gitignore-able config |
| Self-documenting rules | Rule message body IS the warning shown to Claude — Markdown formatted, shown as `systemMessage` |
| No-dependency parser | Custom frontmatter parser in `config_loader.py` handles YAML subset without PyYAML |
| Dual syntax | Legacy: `pattern: "regex"` field; Modern: `conditions:` list with explicit field/operator/pattern |

### 5d. `additionalContext` for Injecting Deprecated Features Back

| Feature | Detail |
|---------|--------|
| Pattern | SessionStart hook outputs `hookSpecificOutput.additionalContext` to inject behavior that was removed from Claude Code's built-in output styles |
| Plugins | explanatory-output-style (re-implements deprecated Explanatory mode), learning-output-style (re-implements unshipped Learning mode) |
| Implication | Plugin hooks can restore/polyfill removed product capabilities by injecting system prompt additions |

### 5e. Prompt-Based Hooks (LLM-in-the-loop validation)

Not implemented in any plugin here, but heavily documented in plugin-dev skill as the **recommended path**:

| Feature | Detail |
|---------|--------|
| Hook type | `"type": "prompt"` instead of `"type": "command"` |
| Supported events | Stop, SubagentStop, UserPromptSubmit, PreToolUse |
| Variables | `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`, `$TRANSCRIPT_PATH` available in prompt strings |
| Benefit | Natural language reasoning; catches semantic violations command scripts miss |
| Hybrid | Combine command (fast/deterministic) + prompt (intelligent) hooks in same event handler — run in parallel |

Example from patterns.md:
```json
{
  "matcher": "mcp__.*__delete.*",
  "hooks": [{"type": "prompt", "prompt": "Deletion detected. Verify intentional and reversible. Return 'approve' only if safe."}]
}
```

### 5f. `$CLAUDE_ENV_FILE` — Session-Persistent Env Injection

| Feature | Detail |
|---------|--------|
| What | SessionStart command hook appends `export KEY=val` lines to `$CLAUDE_ENV_FILE` |
| Effect | Variables persist for entire session, available in all subsequent hook executions |
| Use case | Detect project type (Node/Rust/Go/Python) once at startup; make available to all per-tool hooks |
| Status | Only in example scripts; no production plugin uses this yet |

---

## Files Referenced

| File | Role |
|------|------|
| `hookify/hooks/hooks.json` | Covers PreToolUse, PostToolUse, Stop, UserPromptSubmit with Python commands |
| `hookify/core/rule_engine.py` | RuleEngine class; condition evaluation; blocking vs warning priority |
| `hookify/core/config_loader.py` | Rule dataclass; custom YAML frontmatter parser; glob-based rule discovery |
| `hookify/hooks/{pretooluse,posttooluse,stop,userpromptsubmit}.py` | Per-event entry points; error-safe; always exit 0 |
| `hookify/examples/*.local.md` | Four example rules covering rm block, sensitive files, console.log, stop-without-tests |
| `security-guidance/hooks/security_reminder_hook.py` | 9 hardcoded security patterns; session-state deduplication; exit 2 blocking |
| `ralph-wiggum/hooks/stop-hook.sh` | Loop controller; transcript JSONL parsing; promise-tag completion detection |
| `explanatory-output-style/hooks-handlers/session-start.sh` | additionalContext injection pattern |
| `learning-output-style/hooks-handlers/session-start.sh` | additionalContext injection (larger prompt) |
| `plugin-dev/skills/hook-development/SKILL.md` | Authoritative reference: all events, output schemas, updatedInput, ask permission |
| `plugin-dev/skills/hook-development/references/patterns.md` | 10 patterns: security, test enforcement, context loading, notification, MCP, build verification, permission confirmation, code quality, flag-file activation, config-driven |
| `plugin-dev/skills/hook-development/references/advanced.md` | Multi-stage, caching, cross-event workflows, external integrations, rate limiting |
| `plugin-dev/skills/hook-development/examples/validate-bash.sh` | Demonstrates `permissionDecision: "ask"` for sudo |
| `plugin-dev/skills/hook-development/examples/validate-write.sh` | Demonstrates `permissionDecision: "ask"` for sensitive files |
