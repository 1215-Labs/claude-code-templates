# Reference Sync Report

**Generated**: 2026-03-05
**claude-code version**: v2.1.38 (`19bb071f`)
**agent-os commit**: `1f3279bb` (memory branch)
**Mode**: quick

---

## Executive Summary

Agent-os is broadly well-aligned with the claude-code reference. The 6 commits since last sync were CHANGELOG-only — no plugin or API changes. The primary gaps are on the agent-os side: skill descriptions lack the standard "This skill should be used when..." phrasing (only 1/19 compliant), most agents lack `<example>` routing blocks, lightweight agents don't use `model: inherit`, and commands accepting `$ARGUMENTS` are missing `argument-hint` fields. Two medium-priority hook API features (`permissionDecision: "ask"` and prompt-based hooks) offer meaningful improvements over the current binary block/allow pattern.

**Total findings**: 0 critical, 3 high, 5 medium, 2 low.

---

## What's New Since Last Sync

**6 commits** since last sync (2026-02-09 against v2.1.31):

| Commit | Message |
|--------|---------|
| `19bb071` | chore: Update CHANGELOG.md |
| `85f2807` | chore: Update CHANGELOG.md |
| `e7f36bc` | chore: Update CHANGELOG.md |
| `2bc62d1` | chore: Update CHANGELOG.md |
| `ef1e0ac` | chore: Update CHANGELOG.md |
| `d7e3cfb` | chore: Update CHANGELOG.md |

**Files changed**: `CHANGELOG.md` only (+57 lines). No plugin, API, or structural changes. Gap analysis below reflects agent-os drift from previously-established reference patterns.

---

## Recommended Updates

### Critical Priority

_None._

---

### High Priority

| # | Component | Issue | Recommendation | Impact | Effort | ROI |
|---|-----------|-------|----------------|--------|--------|-----|
| H1 | 18/19 skills | Description phrasing inconsistent — only `agent-browser` uses "This skill should be used when..." | Standardize all skill descriptions to third-person "This skill should be used when the user asks to..." pattern | 4 | 2 | 2.0 |
| H2 | ~10/17 agents | No `model:` field set — all default to session model regardless of task weight | Add `model: inherit` to lightweight/helper agents (e.g., `code-reviewer`, `debugger`, `team-validator`, `team-builder`); keep `sonnet`/`opus` only for complex agents | 3 | 1 | 3.0 |
| H3 | Commands with `$ARGUMENTS` | No `argument-hint` field — users see no hint about expected argument format | Add `argument-hint: [descriptive-name]` to all commands that accept `$ARGUMENTS` | 3 | 1 | 3.0 |

---

### Medium Priority

| # | Component | Issue | Recommendation | Impact | Effort | ROI |
|---|-----------|-------|----------------|--------|--------|-----|
| M1 | ~7/17 agents | Missing `<example>` blocks — agents without examples have lower routing accuracy | Add 2–3 `<example>` blocks to agents missing them: `codex-delegator`, `gemini-delegator`, `meta-agent`, `team-builder`, `team-validator`, `deployment-engineer` | 4 | 3 | 1.3 |
| M2 | Complex skills (5+) | No `references/` or `examples/` subdirs — all content crammed into SKILL.md | Add `references/` for docs and `examples/` for worked examples in: `multi-model-orchestration`, `agent-teams`, `repo-audit-engine`, `repo-optimize-engine`, `skill-evaluator` | 3 | 2 | 1.5 |
| M3 | Hooks | Binary allow/deny only — no `permissionDecision: "ask"` for ambiguous operations | Update sensitive hooks (e.g., env file writes, destructive Bash) to emit `permissionDecision: "ask"` instead of `deny` when human judgment is appropriate | 3 | 2 | 1.5 |
| M4 | Hooks | All hooks are command-type — no prompt-based semantic validation | Add `"type": "prompt"` hooks for Stop event validation (e.g., "verify tests ran before stopping") alongside existing command hooks | 3 | 2 | 1.5 |
| M5 | Internal commands | No `hide-from-slash-command-tool: "true"` on sub-workflow commands | Identify internal helper commands (e.g., sub-steps called only by other commands) and hide them from the slash command picker | 2 | 1 | 2.0 |

---

### Low Priority

| # | Component | Issue | Recommendation | Impact | Effort | ROI |
|---|-----------|-------|----------------|--------|--------|-----|
| L1 | SessionStart hook | `additionalContext` not used — could inject per-project context into system prompt | Use SessionStart + `additionalContext` to inject repo-specific instructions on first run | 2 | 2 | 1.0 |
| L2 | Hooks exit convention | Mixed: some hooks use exit 2 + stderr (older), should be exit 0 + JSON stdout (newer) | Audit all hook scripts; migrate any using exit 2 to structured JSON `permissionDecision` output | 2 | 3 | 0.7 |

---

## Pattern Comparison

### Agents

| Field | claude-code reference | agent-os status | Gap |
|-------|-----------------------|-----------------|-----|
| `name` | kebab-case, matches filename | ✅ Consistent | None |
| `description` | "Use this agent when..." + `<example>` blocks | ⚠️ Mix: some have examples, ~10 are one-liners | Partial |
| `model` | `inherit` for lightweight, `sonnet`/`opus` for heavy | ⚠️ Not set consistently | Yes |
| `color` | Set on most agents | ✅ Widely set | None |
| `tools` | Comma-separated or JSON array | ✅ Consistent | None |

### Commands

| Field | claude-code reference | agent-os status | Gap |
|-------|-----------------------|-----------------|-----|
| `description` | Verb-first, under 60 chars | ✅ All 46 have it | None |
| `allowed-tools` | Present when needed | ✅ All 46 have it | None |
| `argument-hint` | `[arg-name]` brackets; consistent | ❌ Not used | Yes |
| `model` | Optional, used rarely | N/A | None |
| `hide-from-slash-command-tool` | Used for internal helpers | ❌ Not used | Low |

### Skills

| Field | claude-code reference | agent-os status | Gap |
|-------|-----------------------|-----------------|-----|
| `name` | Display name, Title Case OK | ✅ Consistent | None |
| `description` | "This skill should be used when the user asks to..." | ⚠️ Only 1/19 compliant | Yes |
| `version` | Present in all plugin-dev skills | ✅ 19/19 have it | None |
| `references/` subdir | Used for supplementary docs | ❌ Not used | Yes |
| `examples/` subdir | Used for worked examples | ❌ Not used | Yes |

### Hooks

| Feature | claude-code reference | agent-os status | Gap |
|---------|----------------------|-----------------|-----|
| `PreToolUse` | 2 plugins use it | ✅ Used | None |
| `PostToolUse` | hookify uses it | ✅ Used | None |
| `SessionStart` | 2 plugins use it | ✅ Used | None |
| `Stop` | hookify, ralph-wiggum | ✅ Used | None |
| `UserPromptSubmit` | hookify | ✅ Used | None |
| `permissionDecision: "ask"` | In example scripts | ❌ Not used | Medium |
| `updatedInput` middleware | Documented, not implemented | ❌ Not used | Low |
| `additionalContext` | 2 plugins use it | ❌ Not used | Low |
| Prompt-based hooks | Documented pattern | ❌ Not used | Medium |
| `$CLAUDE_ENV_FILE` | Example scripts only | ❌ Not used | Low |
| Exit 0 + JSON (structured) | hookify preferred | ⚠️ Mix of exit 2 and JSON | Partial |

### Directory Structure

| Convention | claude-code reference | agent-os | Status |
|-----------|----------------------|----------|--------|
| Plugin manifest `.claude-plugin/plugin.json` | Standard | N/A (no plugin system) | N/A |
| `skills/{name}/SKILL.md` | Standard | ✅ Adopted | Done |
| `skills/{name}/references/` | Optional, widely recommended | ❌ Not used | Gap |
| `skills/{name}/examples/` | Optional, widely recommended | ❌ Not used | Gap |
| `hooks-handlers/` for shell scripts | Some plugins | ✅ `hooks/` dir used | Equivalent |
| kebab-case filenames | Consistent | ✅ Consistent | Done |

---

## Hook Patterns

### New Features Available

| Feature | Description | Agent-OS Status | Recommendation |
|---------|-------------|-----------------|----------------|
| `permissionDecision: "ask"` | Third option: surfaces human confirmation dialog (not block/allow binary) | ❌ Not used | Add to hooks where outcome is ambiguous (env file writes, config changes) |
| Prompt hooks (`"type": "prompt"`) | LLM-in-the-loop validation — catches semantic violations command scripts miss | ❌ Not used | Add Stop hook prompt to enforce test-run policy |
| `additionalContext` in SessionStart | Inject string into Claude's system context at session start | ❌ Not used | Could inject repo conventions from CLAUDE.md automatically |
| `updatedInput` middleware | Modify tool input before execution (sanitize paths, strip secrets) | ❌ Not used | Low priority — no specific use case yet |
| `$CLAUDE_ENV_FILE` | Persist env vars across entire session from SessionStart | ❌ Not used | Low priority — useful for project-type detection |

### Architecture Comparison

| Aspect | claude-code reference | agent-os |
|--------|----------------------|----------|
| Dominant script language | Python 3 + bash | Python 3 (UV shebangs) |
| Exit convention | Exit 0 + JSON preferred (hookify) | Mixed (exit 2 + JSON) |
| Blocking mechanism | `permissionDecision: "deny"` in JSON | Primarily exit 2 |
| Prompt-based hooks | Documented, example-only in reference | Not used |
| Rule engines | hookify: markdown frontmatter rules | Hardcoded per hook |
| Session state | JSON file per session_id (security-guidance) | Not used |

---

## Plugins Worth Adopting

| Plugin | What to Extract | Effort | ROI |
|--------|----------------|--------|-----|
| `security-guidance` | 9-rule SECURITY_PATTERNS catalog (GitHub Actions injection, eval, innerHTML, pickle, os.system) | Low | High — plug into existing PreToolUse hook |
| `plugin-dev` | `references/` + `examples/` subdir pattern; `argument-hint` field conventions | Low | High — copy structure pattern immediately |
| `hookify` | Markdown-based rule engine for user-configurable hooks without scripting | High | Medium — already integrated as a skill; adopting Python engine is a separate project |
| `ralph-wiggum` | Stop hook loop controller (feeds `"reason"` back to Claude as next prompt) | Medium | Low — niche; useful for auto-loop workflows only |

---

## Trivial Fixes Available

| # | Files | Fix Type | Current | Proposed |
|---|-------|----------|---------|----------|
| 1 | 18/19 SKILL.md files | `standardize_description` | Non-standard phrasings | "This skill should be used when the user asks to [triggers]..." |
| 2 | ~10 agent .md files | `add_model_inherit` | (no model field) | `model: inherit` |
| 3 | Commands accepting `$ARGUMENTS` | `add_argument_hint` | (no field) | `argument-hint: [arg-name]` |

Run `/sync-reference --apply-fixes` to auto-apply trivial fixes.

---

## Action Items

### Immediate (High Priority)
- [ ] **H1**: Standardize 18 skill descriptions — run `/sync-reference --apply-fixes` or batch-edit SKILL.md files
- [ ] **H2**: Add `model: inherit` to lightweight agents: `code-reviewer`, `debugger`, `team-validator`, `team-builder`, `context-manager`, `codebase-analyst`
- [ ] **H3**: Add `argument-hint` to commands accepting `$ARGUMENTS` — find with `grep -rl '\$ARGUMENTS' .claude/commands/`

### Short-term (Medium Priority)
- [ ] **M1**: Add 2–3 `<example>` blocks to: `codex-delegator`, `gemini-delegator`, `meta-agent`, `team-builder`, `team-validator`, `deployment-engineer`
- [ ] **M2**: Create `references/` and `examples/` subdirs in: `multi-model-orchestration`, `agent-teams`, `repo-audit-engine`, `skill-evaluator`, `repo-optimize-engine`
- [ ] **M3**: Update sensitive hooks to use `permissionDecision: "ask"` for ambiguous operations
- [ ] **M4**: Add a prompt-based Stop hook for semantic test-enforcement policy
- [ ] **M5**: Add `hide-from-slash-command-tool: "true"` to internal sub-workflow commands

### Long-term (Low Priority)
- [ ] **L1**: Use `additionalContext` in SessionStart to inject project conventions
- [ ] **L2**: Migrate exit-2 hooks to structured JSON output (exit 0 + `permissionDecision`)
- [ ] Adopt security-guidance SECURITY_PATTERNS catalog into existing PreToolUse hook
