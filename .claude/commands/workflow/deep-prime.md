---
name: deep-prime
description: |
  Prime with deep context for a specific part of the codebase using parallel subagents.

  Usage: /deep-prime "<area>" "<special focus>"
  Examples:
  /deep-prime "frontend" "Focus on UI components"
  /deep-prime "backend" "Focus on API services"
  /deep-prime "tests" "Focus on testing patterns"
argument-hint: <area> <Specific focus>
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash(git *)
  - Task
---

# Deep Context Priming

## Today's Focus

**Area**: $1
**Special attention**: $2

## Phase 1: Parallel Context Discovery (Use Subagents)

**IMPORTANT**: Launch these explorations as PARALLEL subagents to preserve main agent context for synthesis and task execution.

### Subagent 1: Project Guidelines Explorer
Use the **Explore subagent** with "medium" thoroughness to extract from CLAUDE.md:
- `## Overview` - Project purpose
- `## Project Structure` - Directory layout
- `## Where to Look` - Task-to-location mapping (critical for finding relevant files)
- `## Conventions` - Patterns to follow
- `## Anti-Patterns` - Things to avoid

Return a structured summary of conventions relevant to **$1**.

### Subagent 2: Area File Discovery
Use the **Explore subagent** with "thorough" thoroughness to:

**If CLAUDE.md has "## Where to Look" section:**
- Find the row matching "$1" focus area
- Use listed locations as starting points
- Return list of key files with brief descriptions

**Otherwise, explore dynamically based on focus area:**

| Focus Area | Directories to Explore |
|------------|----------------------|
| frontend | `src/components/`, `src/pages/`, `app/`, `src/hooks/`, `src/contexts/` |
| backend | `src/server/`, `src/api/`, `server/`, `api/`, `routes/` |
| tests | `tests/`, `__tests__/`, `*.test.*`, `*.spec.*` |
| services | `src/services/`, `services/` |
| database | `src/db/`, `database/`, `migrations/`, `models/` |
| config | Config files in root, `src/config/` |
| tools | `src/tools/`, `tools/` |

Return prioritized file list with entry points first.

### Subagent 3: Pattern & Dependency Mapper
Use the **Explore subagent** with "thorough" thoroughness to:
- Identify main entry points (index files, main files, app files)
- Map import/dependency relationships in the **$1** area
- Note key patterns and abstractions used
- Identify how this area connects to other parts of the codebase

Return a dependency graph summary and pattern list.

Wait for all subagents to complete before proceeding.

## Phase 2: Synthesize Discovery

Consolidate subagent findings into:

1. **Curated Reading List** - Ordered by importance, starting with entry points
2. **Pattern Summary** - Key conventions for this area
3. **Dependency Map** - How components connect

## Phase 3: Deep Context Building

Use the **general-purpose subagent** to read and analyze the curated file list:

For each key file:
1. **Read the file**
2. **Understand its purpose** - What does it do?
3. **Note key patterns** - How does it fit the codebase conventions?
4. **Track critical dependencies** - Important connections to note

Return structured analysis for each file.

## Phase 4: Context Summary (Main Agent)

With main context preserved, synthesize understanding:

### Structure
_[How this area is organized]_

### Patterns
_[Key patterns and conventions used]_

### Connections
_[How it connects to other parts of the codebase]_

### Dependencies
_[What it depends on and what depends on it]_

### Ready For
_[What tasks you're now prepared to handle in this area]_

## Critical Rules

### Follow CLAUDE.md Guidelines

Always check:
- **Conventions section** - Required patterns
- **Anti-Patterns section** - Things to avoid
- **Testing section** - How to test changes

### Project-Specific Rules

If CLAUDE.md mentions:
- Package manager preferences (e.g., "bun exclusively")
- Type system requirements
- Error handling philosophy
- Testing requirements

Apply these strictly during development.

## Related Commands

- `/quick-prime` - Quick overview without deep dive
- `/code-review` - Review changes after making them
- `/onboarding` - Full onboarding for new developers
