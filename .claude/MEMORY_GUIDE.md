# Persistent Memory Guide

How Claude Code remembers things across sessions.

## Overview

Claude Code sessions are stateless — when a session ends, everything discussed is gone. The persistent memory system solves this by saving important facts, decisions, and preferences to markdown files that get loaded automatically at the start of every session.

The system has two tiers:

- **Project memory** (`.claude/memory/`) — lives in your repo, travels with git, shared with your team
- **Global memory** (`~/.claude/memory/`) — lives on your machine, follows you across all projects

Both tiers load automatically. You don't need to do anything special after setup.

## Quick Start

```
/memory "init"              # Create the memory directories and starter files
/remember "We use bun, not npm"   # Save a fact
/memory                     # Check what's stored
```

That's it. The hooks handle loading at session start and prompting you to save at session end.

## Theory of Operation

### Session Lifecycle

1. **SessionStart** — `memory-loader.py` runs once, reads all memory files, injects a summary into Claude's context (up to ~2000 tokens)
2. **During session** — Use `/remember`, `/forget`, `/memory` to manage stored knowledge
3. **Stop** — A hook prompts Claude to review the session for anything worth remembering, writes to the appropriate files, and creates a session log
4. **SessionEnd** — `memory-distill.py` creates a stub session log if the Stop hook didn't write one (safety net)

### Priority-Based Loading

Not everything fits in context. The loader uses a priority system:

| Priority | Files | Max Tokens |
|----------|-------|------------|
| P0 (always) | project-context.md, user-profile.md, tasks.md | 600, 400, 400 |
| P1 (if room) | decisions.md, latest session log | 400, 300 |
| P2 (fill remaining) | voice.md, tool-environment.md | 200, 200 |

P0 files load first. If budget remains, P1 files load. P2 fills whatever space is left. Files exceeding their max token allocation are truncated with a `[...truncated]` marker.

## Memory Files

### Project Memory (`.claude/memory/`)

| File | What It Stores |
|------|----------------|
| `project-context.md` | Architecture notes, stack info, coding conventions |
| `decisions.md` | Architectural decisions in `DEC-NNN` format |
| `tasks.md` | Active, completed, and blocked tasks |
| `sessions/` | Per-session logs (named `YYYY-MM-DD_HHMM.md`) |

### Global Memory (`~/.claude/memory/`)

| File | What It Stores |
|------|----------------|
| `user-profile.md` | Your name, role, preferences |
| `voice.md` | Communication style (tone, formality, verbosity) |
| `tool-environment.md` | System tools, versions, environment details |

Global memory is created by `/remember` when it classifies input as personal rather than project-specific. These files are never committed to git.

### File Formats

**Standard entries** are timestamped bullet points:

```markdown
- [2026-02-07] We use bun instead of npm for all package management
```

**Decisions** use a structured format:

```markdown
### DEC-001: Use TypeScript for backend
- **Date**: 2026-02-07
- **Context**: Why this decision was needed
- **Decision**: What was decided
- **Alternatives**: What was considered
```

**Session logs** follow a template:

```markdown
# Session 2026-02-07

## Summary
2-3 sentences of what was accomplished

## Key Changes
- Files and features changed

## Open Items
- Anything left unfinished
```

## Commands

### `/remember` — Store Information

Saves a fact to the right file automatically. The command classifies your input by keywords:

```
/remember "Always use bun instead of npm"        → user-profile.md (preference)
/remember "Backend uses Express + Prisma"         → project-context.md (architecture)
/remember "Decided to use JWT over sessions"      → decisions.md (DEC-NNN format)
/remember "TODO: add rate limiting to API"        → tasks.md
/remember "Keep responses concise and direct"     → voice.md (communication style)
/remember "Running Node 22 with bun 1.1"          → tool-environment.md (tooling)
```

Classification keywords:
- **Preferences**: "I prefer", "always use", "never use"
- **Decisions**: "decided", "chose", "trade-off"
- **Tasks**: "todo", "remember to", "next time"
- **Voice/style**: "tone", "formal", "concise", "style"
- **Tool/environment**: "bun", "node", "docker", "version"
- **Default**: anything else goes to project-context.md

### `/forget` — Remove Information

Removes entries by decision ID or keyword search:

```
/forget "DEC-002"           # Remove a specific decision (entire block)
/forget "bun"               # Find and remove all mentions of bun
/forget "my email address"  # Search across all files
```

Section headings are preserved — only content is removed.

### `/memory` — Status and Management

```
/memory                     # Summary table: files, sizes, token counts, dates
/memory "status"            # Detailed health check with budget breakdown
/memory "search typescript" # Cross-file search with line numbers
/memory "init"              # Create directories and starter templates
/memory "prune"             # Remove old session logs (keeps 10 most recent)
```

## Automatic Behavior

The memory system runs without manual intervention through hooks defined in `.claude/hooks/hooks.json`.

### On Session Start

`memory-loader.py` runs once and:
1. Checks both `~/.claude/memory/` and `.claude/memory/` for files
2. Reads files in priority order (P0 first, then P1, then P2)
3. Stays within the ~2000 token budget
4. Injects the loaded memory as a system message

If the memory directories don't exist, the hook silently skips — no errors, no setup required.

### On Stop

A prompt-based hook asks Claude to:
1. Review the session for memory-worthy information
2. Write new entries to the appropriate files (with timestamps)
3. Create a session log in `.claude/memory/sessions/`
4. Check for uncommitted changes

### On Session End

`memory-distill.py` runs as a safety net:
- If the Stop hook already wrote a session log, this does nothing
- If no log exists, it creates a stub so every session has a record

## Token Budget

The total budget is **~2000 tokens** (estimated at ~4 characters per token). This keeps memory injection small enough to not crowd out the actual conversation.

### How Budget Is Spent

With typical file sizes, a session might load:

```
project-context.md    525 tokens (of 600 max)
user-profile.md       180 tokens (of 400 max)
tasks.md              120 tokens (of 400 max)
decisions.md          200 tokens (of 400 max)
latest session log    150 tokens (of 300 max)
voice.md               80 tokens (of 200 max)
tool-environment.md    65 tokens (of 200 max)
────────────────────────────────
Total               1,320 tokens (of 2000 budget)
```

### What Happens When Files Are Too Large

If a file exceeds its per-file max, it's truncated from the end with a `[...truncated]` marker. The most important content should be at the top of each file.

If total loaded content exceeds the budget, lower-priority files (P2 first, then P1) are dropped entirely.

## Security

### Secret Detection

`/remember` scans input before writing. It refuses to store text matching these patterns:

- API keys (OpenAI, Stripe, Anthropic, AWS, Slack)
- GitHub personal access tokens (classic, OAuth, fine-grained)
- Private keys (RSA, EC, DSA)
- Passwords in config format (`password=`, `passwd:`)
- Database connection strings (MongoDB, PostgreSQL)

If a secret is detected, the command warns you and does not write.

### What's Safe to Store

Project facts, preferences, decisions, task lists, architecture notes, coding conventions — anything that isn't a credential.

## Maintenance

### Pruning Session Logs

Session logs accumulate over time. To clean up:

```
/memory "prune"    # Keeps the 10 most recent, removes the rest
```

### Checking Health

```
/memory "status"   # Shows file sizes, token usage, budget warnings
```

This reports if any file is over its token allocation or if the total budget is exceeded.

### Manual Editing

Memory files are plain markdown. You can edit them directly:

- `.claude/memory/project-context.md` — add or reorganize architecture notes
- `.claude/memory/decisions.md` — update decision records
- `.claude/memory/tasks.md` — mark tasks done or add new ones

Global files at `~/.claude/memory/` can be edited the same way.

### Committing Project Memory

Project memory lives in `.claude/memory/` and should be committed to git. Session logs in `.claude/memory/sessions/` are optional — commit them if you want session history in the repo, or add `sessions/` to `.gitignore` if you don't.

## See Also

- [USER_GUIDE.md](USER_GUIDE.md) — Quick reference for all `.claude/` components
- [REGISTRY.md](REGISTRY.md) — Complete component catalog
- `.claude/commands/workflow/memory.md` — `/memory` command source
- `.claude/commands/workflow/remember.md` — `/remember` command source
- `.claude/commands/workflow/forget.md` — `/forget` command source
- `.claude/hooks/memory-loader.py` — Session start loader
- `.claude/hooks/memory-distill.py` — Session end fallback
- `.claude/utils/memory.py` — Core utility functions
