---
name: catchup
description: |
  Resume a session with a briefing: last session summary, git state, active tasks, and suggested next actions.

  Usage: /catchup

  Use for: First command when resuming work — answers "where did I leave off?"
  See also: /quick-prime (project context), /memory (memory management)
argument-hint: none
user-invocable: true
related:
  commands: [/quick-prime, /memory, /deep-prime]
  agents: []
allowed-tools:
  - Read
  - Write
  - Bash(git *)
  - Grep
  - Glob
---

# Session Catchup

You are resuming a work session. Build a concise briefing so the user knows exactly where they left off and what to do next.

## Step 1: Find the Latest Session Log

Search `.claude/memory/sessions/` for the most recent session log file (sorted by filename, which uses `YYYY-MM-DD_HHMM.md` format).

- If session logs exist, read the most recent one. Extract:
  - **Summary** — what was accomplished
  - **Key Changes** — files/features changed
  - **Open Items** — anything left unfinished
  - **Next Session** — suggestion for what to tackle (may not exist in older logs)
- If no session logs exist, note this is the first tracked session.

## Step 2: Check Active Tasks

Read `.claude/memory/tasks.md` for:
- **Active** tasks — currently in progress
- **Blocked** tasks — waiting on something

If the file is empty or has no entries, note "No tracked tasks."

## Step 3: Get Git State

Run a single git command to capture current state:

```bash
git log --oneline -5 && echo "---BRANCH---" && git branch --show-current && echo "---STATUS---" && git status --short && echo "---UNPUSHED---" && git log @{upstream}..HEAD --oneline 2>/dev/null || echo "(no upstream or no unpushed commits)"
```

Extract:
- **Current branch**
- **Last few commits** (to show recent work)
- **Uncommitted changes** (modified/untracked files)
- **Unpushed commits** (commits ahead of remote)

## Step 4: Append Session Resume Entry

Append a timestamped resume entry to `.claude/memory/tasks.md` in the Notes section. If there is no `## Notes` section, create one at the end of the file.

Format: `- [YYYY-MM-DD] Session resumed on branch <current-branch>`

## Step 5: Present the Briefing

Output a concise, scannable briefing in this format:

```
## Session Catchup

### Last Session
_[Summary from session log, or "First tracked session" if none]_

**Key changes:** [bullet list or "none recorded"]
**Open items:** [bullet list or "none"]
**Next session suggestion:** [from session log, or omit if not present]

### Git State
- **Branch:** `<branch-name>`
- **Last commit:** `<hash> <message>`
- **Uncommitted:** [count of modified + untracked files, or "clean"]
- **Unpushed:** [count of commits ahead, or "in sync"]

### Active Tasks
[List from tasks.md, or "No tracked tasks"]

### Blocked
[List from tasks.md, or "Nothing blocked"]

### Suggested Next Actions
[Based on all the above, suggest 1-3 concrete next steps. Examples:]
- Continue working on [open item]
- Review uncommitted changes and commit
- Run `/quick-prime` to refresh project context
- Run `/code-review` before pushing
```

## Guidelines

- Keep the briefing **short** — this is a quick orientation, not a deep dive
- If there are uncommitted changes, always suggest reviewing/committing them
- If there are unpushed commits, suggest pushing after review
- If open items exist from last session, prioritize those in suggestions
- If this is a first session (no logs), suggest `/quick-prime` or `/onboarding` to get started
- Do NOT re-read memory files that were already loaded by the SessionStart hook — reference loaded context instead
