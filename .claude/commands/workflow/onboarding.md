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
---

# Developer Onboarding

You are helping a new developer get up and running with this project! Your goal is to provide them with a personalized onboarding experience.

## Step 1: Discover Project Context

### Read Core Documentation

1. **Read CLAUDE.md** for development guidelines and patterns:
   - `## Overview` - Project purpose and description
   - `## Project Structure` - Directory layout
   - `## Where to Look` - Task-to-location mapping
   - `## Conventions` - Coding patterns to follow
   - `## Anti-Patterns` - Things to avoid
   - `## Testing` - How to run tests

2. **Read README.md** for:
   - Project overview and goals
   - Setup instructions
   - Prerequisites

### Detect Tech Stack

If CLAUDE.md doesn't fully describe the tech stack, detect from:
- `package.json` + `tsconfig.json` (TypeScript/JavaScript/Node.js)
- `pyproject.toml` or `setup.py` (Python)
- `Cargo.toml` (Rust)
- `go.mod` (Go)
- `docker-compose.yml` (Multi-service architecture)

## Step 2: Provide Project Overview

Based on what you discovered, explain to the new developer:

### What is this project?

_[One paragraph summary based on README.md and CLAUDE.md]_

### Architecture Overview

_[Explain how different parts connect based on CLAUDE.md structure or exploration]_

### Tech Stack

_[List main technologies based on detection]_

## Step 3: Getting Started

Guide the user through setup based on README.md:

1. **Prerequisites** they need installed
2. **Installation steps** from README.md
3. **How to run** the project locally
4. **How to verify** everything works

## Step 4: Decision Time - Focus Area

Ask the user which area they'd like to explore:

"Which area of the codebase would you like to explore first?"

**Generate options dynamically based on project structure:**

Look at the directory structure and offer relevant options:
- If `src/components/` or `app/` exists: "Frontend/UI"
- If `src/api/` or `server/` or `backend/` exists: "Backend API"
- If `tests/` or `__tests__/` exists: "Testing"
- If `docs/` exists: "Documentation"
- Use CLAUDE.md "## Where to Look" section to identify other areas

Wait for the user to choose before proceeding.

## Step 5: Deep Dive into Chosen Area

Based on the user's choice:

### 5.1 Explore the Area

1. Use CLAUDE.md "## Where to Look" if it lists files for this area
2. Otherwise, explore the relevant directory with glob patterns
3. Read key files to understand patterns and structure

### 5.2 Identify Patterns and Conventions

From CLAUDE.md and code inspection:
- What patterns are used in this area?
- What conventions must be followed?
- What anti-patterns should be avoided?

### 5.3 Find Contribution Opportunities

Look for:
- TODO or FIXME comments in the code
- Missing error handling or validation
- Areas with minimal test coverage
- Documentation gaps
- Hardcoded values that should be configurable

## Step 6: Generate Report

Provide the user with a structured report:

### Area Overview

_[Architecture explanation and how it connects to other parts]_

### Key Files Walkthrough

_[Purpose of main files and their relationships]_

### Development Patterns

Based on CLAUDE.md conventions:
- Key patterns they should know
- Testing approach for this area
- Common gotchas

### Suggested First Contribution

_[A specific, small improvement with:]_
- Exact file location
- Current behavior vs improved behavior
- Step-by-step implementation guide
- Testing instructions

### What to Include

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
