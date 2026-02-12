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
3. **PreCompact** — When context is about to be compacted, `precompact-guard.py` checks for recent flushes (60s cooldown), then a prompt hook flushes unsaved memories to disk before they're lost
4. **Stop** — A hook prompts Claude to review the session for anything worth remembering, writes to the appropriate files, and creates a session log
5. **SessionEnd** — `memory-distill.py` creates a stub session log if the Stop hook didn't write one (safety net)

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

**Session logs** follow a template with category tags:

```markdown
# Session 2026-02-07

## Summary
2-3 sentences of what was accomplished

## Key Changes
- [DECISION] Chose JWT over sessions for auth
- [FACT] API rate limit is 100 req/min
- [CONTEXT] Refactored auth middleware in src/auth/

## Open Items
- [CONTEXT] Rate limiting tests not yet written
```

### Category Tags

Both the Stop hook and PreCompact flush tag entries for structured retrieval:

| Tag | When to Use |
|-----|-------------|
| `[DECISION]` | Architectural or design choices made |
| `[PREFERENCE]` | User preferences discovered |
| `[FACT]` | Important facts or constraints learned |
| `[ENTITY]` | People, projects, URLs worth tracking |
| `[CONTEXT]` | Current task state, progress, blockers |

Tags make session logs scannable and improve FTS5 search results (see Search below).

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
/memory "search typescript" # Ranked FTS5 search (falls back to grep)
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

### On PreCompact (Mid-Session Memory Flush)

When context is about to be compacted (long sessions), a two-stage hook fires:

1. **`precompact-guard.py`** — Checks if a memory flush already happened within the last 60 seconds. If so, injects a `FLUSH_ALREADY_DONE` system message to prevent duplicate writes.
2. **Prompt hook** — Instructs Claude to write unsaved memories to `.claude/memory/sessions/YYYY-MM-DD.md` with category tags, then preserve critical context in the compaction summary.

This is the highest-value pattern — it ensures memories survive even when context is compressed mid-session. Based on OpenClaw's pre-compaction memory flush pattern.

### On Stop

A prompt-based hook asks Claude to:
1. Review the session for memory-worthy information
2. Write new entries to the appropriate files (with timestamps and category tags)
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

## Search

### FTS5 Ranked Search

The `/memory "search <term>"` command uses SQLite FTS5 for ranked keyword search across all memory files. This replaces simple grep with relevance-ranked results and highlighted snippets.

The sidecar script (`memory-search.py`) can also be called directly:

```
uv run .claude/hooks/memory-search.py "auth middleware"
```

It indexes all `.md` files in both `~/.claude/memory/` and `.claude/memory/`, rebuilds the index on each call (fast — memory dirs are small), and returns results ranked by relevance. If FTS5 fails, the command falls back to grep.

The FTS5 database (`.claude/memory/.memory-search.db`) is auto-generated and gitignored.

### Hybrid Search (FTS5 + pgvector)

For semantic similarity beyond keyword matching, the hybrid search script combines FTS5 keyword results with pgvector vector search using OpenAI embeddings.

```
uv run .claude/hooks/memory-search-hybrid.py "query"              # hybrid (vector + keyword)
uv run .claude/hooks/memory-search-hybrid.py --keyword-only "q"   # FTS5 only (no DB needed)
uv run .claude/hooks/memory-search-hybrid.py --vector-only "q"    # pgvector only
uv run .claude/hooks/memory-search-hybrid.py --index              # index memory files
uv run .claude/hooks/memory-search-hybrid.py --status             # show index stats
```

Results are merged using a 0.7 vector / 0.3 keyword weighting (per OpenClaw's recommended ratio). When `DATABASE_URL` is not set, it gracefully falls back to keyword-only search.

**Requirements**: `DATABASE_URL` (PostgreSQL with pgvector) and `OPENAI_API_KEY` (for text-embedding-3-small embeddings). The script creates a dedicated `memory_embeddings` table with an HNSW index for fast cosine similarity search.

**Chunking**: Memory files are chunked at 800 characters (~200 tokens) with 100-char overlap. Content-hash caching skips re-embedding unchanged files.

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

## Comparison with OpenClaw

This memory system is based on patterns from [OpenClaw](https://github.com/openclaw/openclaw)'s memory architecture (documented in `docs/exploration/openclaw-architecture.md`, Part VIII). Here's how they compare.

### Parity — What We Match

| Capability | OpenClaw | This System |
|---|---|---|
| File-based daily logs | `memory/YYYY-MM-DD.md` | `sessions/YYYY-MM-DD.md` |
| Curated long-term memory | Single `MEMORY.md` | Split across 6 typed files (decisions, tasks, profile, etc.) |
| Pre-compaction disk flush | `memory-flush.ts` in agent runtime | `PreCompact` prompt hook + dedup guard |
| Flush dedup guard | Token threshold + cycle tracking | 60s cooldown via `precompact-guard.py` |
| Bootstrap loader at start | `before_agent_start` hook | `memory-loader.py` with priority tiers |
| Auto-capture at session end | Regex triggers → categorize → store | Stop prompt hook with category tags |
| Keyword search (BM25) | SQLite FTS5 | SQLite FTS5 via `memory-search.py` |

### Gaps — Where OpenClaw Is Ahead

| Capability | OpenClaw | Gap |
|---|---|---|
| **Vector search** | sqlite-vec embeddings, hybrid BM25+vector (0.7/0.3 weighting) | `memory-search-hybrid.py` provides pgvector + FTS5 hybrid (alpha) |
| **Embedding cascade** | Auto-selects: local GGUF → OpenAI → Gemini → Voyage with caching | Single provider (OpenAI text-embedding-3-small) |
| **Plugin system** | Slot-based memory plugins (core, LanceDB), hot-swappable backends | Single implementation, no plugin API |
| **Session transcript indexing** | Full conversations chunked (400 tokens, 80 overlap) into SQLite | Session summaries only |
| **File watching** | Real-time inotify with 1500ms debounce | Reindex on each search call |
| **Configurable thresholds** | Dozens of tunable params (`memorySearch.*`, `compaction.*`) | Hardcoded constants |

### Advantages — Where We're Ahead

| Capability | This System | OpenClaw |
|---|---|---|
| **Two-tier memory** | Global (`~/.claude/memory/`) + project (`.claude/memory/`) with auto-routing | Single directory, no global/project split |
| **Auto-classification** | `/remember` routes by keyword analysis to 6 typed files | Manual categorization or regex triggers |
| **Priority-based loading** | P0/P1/P2 tiers ensure critical facts always load within budget | Loads by recency, no priority system |
| **Memory commands** | `/remember`, `/forget`, `/memory` with status, search, init, prune | No user-facing CLI commands |
| **Secret scanning** | 13 patterns block credentials from being stored | Not addressed |

### Summary

The 4 highest-value OpenClaw patterns have been adopted: pre-compaction flush, auto-capture with category tags, FTS5 search, and hybrid vector+keyword search. The hybrid search prototype (`memory-search-hybrid.py`) uses pgvector on Supabase with OpenAI embeddings, merging results at 0.7/0.3 vector/keyword weighting — matching OpenClaw's approach. Remaining gaps (plugin system, session transcript indexing, file watching) solve scale problems that don't apply to small memory directories.

## See Also

- [USER_GUIDE.md](USER_GUIDE.md) — Quick reference for all `.claude/` components
- [REGISTRY.md](REGISTRY.md) — Complete component catalog
- `.claude/commands/workflow/memory.md` — `/memory` command source
- `.claude/commands/workflow/remember.md` — `/remember` command source
- `.claude/commands/workflow/forget.md` — `/forget` command source
- `.claude/hooks/memory-loader.py` — Session start loader
- `.claude/hooks/precompact-guard.py` — PreCompact dedup guard (60s cooldown)
- `.claude/hooks/memory-search.py` — FTS5 ranked search sidecar
- `.claude/hooks/memory-search-hybrid.py` — Hybrid FTS5 + pgvector search (alpha)
- `.claude/hooks/memory-distill.py` — Session end fallback
- `.claude/utils/memory.py` — Core utility functions
- `docs/exploration/obsidian-vector-patterns.md` — pgvector infrastructure analysis
