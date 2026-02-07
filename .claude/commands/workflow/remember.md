---
name: remember
description: |
  Store a fact, preference, or decision in persistent memory.

  Usage: /remember "Always use bun instead of npm"

  Auto-classifies into:
  - Global preferences → ~/.claude/memory/user-profile.md
  - Voice/style → ~/.claude/memory/voice.md
  - Tools/env → ~/.claude/memory/tool-environment.md
  - Decisions → .claude/memory/decisions.md
  - Tasks → .claude/memory/tasks.md
  - Project facts → .claude/memory/project-context.md
argument-hint: "<fact, preference, or decision to remember>"
user-invocable: true
related:
  commands: [forget, memory]
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash(python3 *)
---

# Remember

**Store this in persistent memory**: $ARGUMENTS

## Steps

1. **Secret Detection**: Before storing anything, scan the input for secrets (API keys, passwords, tokens, private keys, connection strings). If secrets are detected, STOP and warn the user. Do NOT store the content.

2. **Classification**: Determine where this memory belongs:
   - **User preference** ("I prefer...", "always use...", "never..."): `~/.claude/memory/user-profile.md` → Preferences section
   - **Voice/style** ("tone", "concise", "formal"): `~/.claude/memory/voice.md` → Style section
   - **Tool/environment** ("use bun", "node 20", "docker"): `~/.claude/memory/tool-environment.md` → Tools section
   - **Decision** ("decided", "chose", "trade-off"): `.claude/memory/decisions.md` → Decisions section (use DEC-NNN format)
   - **Task/TODO** ("todo", "remember to", "next time"): `.claude/memory/tasks.md` → Active section
   - **Project fact** (anything else project-specific): `.claude/memory/project-context.md` → Notes section

3. **Check for Duplicates**: Read the target file and check if this fact already exists. If it does, inform the user rather than duplicating.

4. **Create File if Missing**: If the target memory file doesn't exist, create it from the appropriate template structure:
   - Global files: Create with `# Title` and relevant `## Section` headers
   - Project files: Should already exist from `/memory "init"`, but create if needed

5. **Write**: Append the entry with a timestamp prefix: `- [YYYY-MM-DD] content`

6. **Confirm**: Tell the user what was stored and where.

## Decision Format (for decisions.md)

When storing a decision, use this format:
```
### DEC-NNN: [Title]
- **Date**: YYYY-MM-DD
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Alternatives**: [What was considered]
```

## Example

Input: `/remember "Always use bun instead of npm"`
→ Classified as: user preference (tool choice)
→ Written to: `~/.claude/memory/user-profile.md` under `## Preferences`
→ Entry: `- [2026-02-07] Always use bun instead of npm`
