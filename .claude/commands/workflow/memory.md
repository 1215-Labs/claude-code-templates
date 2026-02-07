---
name: memory
description: |
  Manage persistent memory: view status, search, initialize, or prune.

  Usage:
  /memory              - Show summary of all memory
  /memory "status"     - File sizes, token usage, health
  /memory "search auth"- Search across memory files
  /memory "init"       - Create directory structure + starter templates
  /memory "prune"      - Remove old session logs (keep 10 most recent)
argument-hint: "[status|search <term>|init|prune]"
user-invocable: true
related:
  commands: [remember, forget]
allowed-tools:
  - Read
  - Write
  - Bash(python3 *)
  - Glob
  - Grep
---

# Memory Management

**Action**: $ARGUMENTS

## Route by Action

Determine which action to take based on the argument. If no argument, show summary.

### Default (no args): Summary View

Show a table of all memory files with:
- File path (relative)
- Size (bytes)
- Estimated tokens
- Last modified date
- First few lines preview

Format:
```
📋 Persistent Memory Summary

Global (~/.claude/memory/):
  user-profile.md    1.2 KB  ~300 tokens  2026-02-07
  voice.md           0.4 KB  ~100 tokens  2026-02-05
  tool-environment.md 0.3 KB  ~75 tokens   2026-02-01

Project (.claude/memory/):
  project-context.md  2.1 KB  ~525 tokens  2026-02-07
  decisions.md        0.8 KB  ~200 tokens  2026-02-06
  tasks.md            0.5 KB  ~125 tokens  2026-02-07

Sessions: 3 logs (latest: 2026-02-07)

Total: ~1,325 tokens / 2,000 budget (66%)
```

### "status": Detailed Health Check

Show everything from Summary plus:
- Budget breakdown by priority tier
- Warning if any tier is over budget
- Check for potential issues (empty files, very old sessions, missing templates)
- Verify directory structure is intact

### "search <term>": Cross-file Search

Search across ALL memory files (global + project + sessions) for the term.
Use Grep to find matches. Display:
- File path
- Matching lines with context
- Line numbers

### "init": Initialize Memory Structure

Create the full directory structure and starter templates:

1. Create directories:
   - `~/.claude/memory/` (global)
   - `.claude/memory/` (project)
   - `.claude/memory/sessions/` (session logs)

2. Create project templates (if they don't exist):
   - `.claude/memory/project-context.md`
   - `.claude/memory/decisions.md`
   - `.claude/memory/tasks.md`
   - `.claude/memory/sessions/.gitkeep`

3. Create global templates (if they don't exist):
   - `~/.claude/memory/user-profile.md`
   - `~/.claude/memory/voice.md`
   - `~/.claude/memory/tool-environment.md`

4. Report what was created vs what already existed.

### "prune": Clean Up Session Logs

1. List all session logs in `.claude/memory/sessions/`
2. Sort by date (newest first)
3. Keep the 10 most recent
4. Show which files will be removed and their dates
5. Confirm with user before deleting
6. Delete confirmed files
7. Report how much space was freed

## Global Memory Templates

### user-profile.md
```markdown
# User Profile

## Identity

- Name:
- Role:

## Preferences

## Do

## Don't
```

### voice.md
```markdown
# Voice & Style

## Tone

## Style

## Communication
```

### tool-environment.md
```markdown
# Tool Environment

## System

## Tools

## Setup
```
