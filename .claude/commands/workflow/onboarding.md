---
name: onboarding
description: |
  Onboard new developers with a comprehensive overview and first contribution guidance.

  Usage: /onboarding
argument-hint: none
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git *)
  - Task
  - AskUserQuestion
---

# Developer Onboarding

You are helping a new developer get up and running with this project! Your goal is to provide them with a personalized onboarding experience using parallel subagents to preserve context.

## Phase 1: Parallel Discovery (Use Subagents)

**IMPORTANT**: Launch these as PARALLEL subagents (single message, multiple Task tool calls) to preserve main agent context for synthesis.

### Subagent 1: Architecture Explorer
Use the **Explore subagent** with "thorough" thoroughness to:
- Map the complete project directory structure
- Identify key entry points (main files, index files, app files)
- Detect tech stack from config files:
  - `package.json` + `tsconfig.json` (TypeScript/JavaScript/Node.js)
  - `pyproject.toml` or `setup.py` (Python)
  - `Cargo.toml` (Rust)
  - `go.mod` (Go)
  - `docker-compose.yml` (Multi-service architecture)
- Map how different parts of the codebase connect
- Identify the most important directories for development

Return: Project structure map, tech stack summary, architecture diagram (text).

### Subagent 2: Convention Analyzer
Use the **Explore subagent** with "medium" thoroughness to:
- Read CLAUDE.md for:
  - `## Overview` - Project purpose and description
  - `## Project Structure` - Directory layout
  - `## Where to Look` - Task-to-location mapping
  - `## Conventions` - Coding patterns to follow
  - `## Anti-Patterns` - Things to avoid
  - `## Testing` - How to run tests
- Read README.md for:
  - Project overview and goals
  - Setup instructions
  - Prerequisites
- Identify naming conventions from existing code
- Extract coding patterns and style requirements

Return: Convention summary, setup instructions, key patterns to follow.

Wait for both subagents to complete before proceeding.

## Phase 2: Synthesize Overview

With main context preserved, synthesize subagent findings into a clear overview:

### What is this project?

_[One paragraph summary based on README.md and CLAUDE.md]_

### Architecture Overview

_[Explain how different parts connect based on Architecture Explorer findings]_

### Tech Stack

_[List main technologies detected by Architecture Explorer]_

### Getting Started

Based on Convention Analyzer findings:
1. **Prerequisites** they need installed
2. **Installation steps** from README.md
3. **How to run** the project locally
4. **How to verify** everything works

## Phase 3: Choose Focus Area

Ask the user which area they'd like to explore deeper.

**Generate options dynamically based on Architecture Explorer findings:**

Look at the directory structure and offer relevant options:
- If `src/components/` or `app/` exists: "Frontend/UI"
- If `src/api/` or `server/` or `backend/` exists: "Backend API"
- If `tests/` or `__tests__/` exists: "Testing"
- If `docs/` exists: "Documentation"
- Use CLAUDE.md "## Where to Look" section to identify other areas

Use AskUserQuestion to let them choose.

## Phase 4: Deep Dive (Focused Subagent)

After user selects their area of interest, launch a **single focused subagent**:

### Focused Area Explorer
Use the **Explore subagent** with "very thorough" thoroughness to:
- Explore the chosen area in depth
- Read key files to understand patterns and structure
- Identify conventions specific to this area
- Find contribution opportunities:
  - TODO or FIXME comments
  - Missing error handling or validation
  - Areas with minimal test coverage
  - Documentation gaps
  - Hardcoded values that should be configurable

Return: Detailed area analysis, key files, patterns, contribution opportunities.

## Phase 5: Generate Personalized Report (Main Agent)

Synthesize all findings into a personalized onboarding report:

### Area Overview

_[Architecture explanation for their chosen area and how it connects to other parts]_

### Key Files Walkthrough

_[Purpose of main files and their relationships in the chosen area]_

### Development Patterns

Based on CLAUDE.md conventions:
- Key patterns they should know for this area
- Testing approach for this area
- Common gotchas

### Suggested First Contribution

_[A specific, small improvement from Phase 4 findings:]_
- Exact file location
- Current behavior vs improved behavior
- Step-by-step implementation guide
- Testing instructions

### What to Include in Their Work

1. **Key patterns from CLAUDE.md** they should follow
2. **Specific contribution suggestion** with file references
3. **Common gotchas** for this area
4. **Testing approach** from CLAUDE.md

## Related Commands

After onboarding, the developer can use:
- `/deep-prime "<area>" "<focus>"` - Get deep context for specific work
- `/quick-prime` - Quick project overview
- `/code-review` - Review their changes before committing

Remember to encourage the user to start small and iterate. Guide them based on the project's conventions from CLAUDE.md.
