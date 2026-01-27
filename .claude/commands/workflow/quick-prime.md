---
name: quick-prime
description: |
  Quick context priming - reads essential files and provides project overview

  Usage: /quick-prime

  Use for: Fast project context when starting a session
  See also: /deep-prime (detailed area analysis), /onboarding (interactive intro)
argument-hint: none
user-invocable: true
related:
  commands: [/deep-prime, /onboarding, /prime]
  agents: [codebase-analyst]
allowed-tools:
  - Read
  - Glob
  - Grep
---

# Quick Context Priming

You need to quickly understand this codebase. Follow these steps:

## Step 1: Read Project Documentation

1. **Read CLAUDE.md** for development guidelines and patterns
2. **Read README.md** for project overview and setup

## Step 2: Understand Project Structure

### Check CLAUDE.md First

If CLAUDE.md has a "## Project Structure" section, use that as your guide.

### Otherwise Explore

Use `tree -L 2` or explore the directory structure to understand the layout.

Look for common patterns:
- `src/` - Source code
- `tests/` or `__tests__/` - Tests
- `docs/` - Documentation
- `config/` or root config files - Configuration

## Step 3: Detect Tech Stack

Identify the project type by checking for:

| File | Tech Stack |
|------|------------|
| `package.json` + `tsconfig.json` | TypeScript/JavaScript |
| `package.json` + `vite.config.*` | Vite frontend |
| `package.json` + `next.config.*` | Next.js |
| `pyproject.toml` or `setup.py` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `docker-compose.yml` | Multi-service architecture |

## Step 4: Read Key Entry Points

Based on detected project type, read essential files:

**TypeScript/JavaScript:**
- `package.json` - Dependencies and scripts
- Main entry from package.json (`main` or `module` field)
- `src/index.ts` or `src/main.ts` if present

**Python:**
- `pyproject.toml` or `setup.py` - Dependencies
- Main module entry point
- `src/main.py` or `app/main.py` if present

**Rust:**
- `Cargo.toml` - Dependencies
- `src/main.rs` or `src/lib.rs`

**Go:**
- `go.mod` - Dependencies
- `main.go` or `cmd/` structure

## Step 5: Check Configuration

Review key config files:
- `.env.example` or `.env.sample` - Environment variables
- CI/CD configs (`.github/workflows/`, `.gitlab-ci.yml`)
- Docker configs if present

## Step 6: Provide Summary

After reading these files, explain to the user:

### Project Purpose

_[One sentence about what this project does and why it exists]_

### Architecture

_[One sentence about the overall structure]_

### Key Patterns

_[One sentence about important conventions from CLAUDE.md]_

### Tech Stack

_[One sentence listing main technologies]_

## Notes

- This is a quick overview for rapid context building
- For deep understanding of a specific area, use `/deep-prime`
- For full onboarding, use `/onboarding`

## Related Commands

- `/deep-prime "<area>" "<focus>"` - Deep context for specific area
- `/onboarding` - Full developer onboarding
- `/code-review` - Review changes
