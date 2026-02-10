# Repo Needs Analysis

Use this template when forking Gemini Pro for repo needs analysis during `/repo-optimize` Phase 1.

## Variables

- `{REPO_PATH}` - Absolute path to the target repository
- `{REPO_NAME}` - Directory basename (e.g., `cbass`, `mac-manage`)
- `{FOCUS_HINT}` - Optional user-provided focus area (may be empty)
- `{MODE}` - `greenfield`, `upgrade`, or `audit`

## Prompt Template

```
Analyze the repository at {REPO_PATH} to determine what Claude Code components it needs.

## Context

- Repository: {REPO_NAME}
- Path: {REPO_PATH}
- Mode: {MODE}
- Focus hint: {FOCUS_HINT}

## Your Task

Perform a comprehensive needs analysis across six areas. Read as many files as needed to build a thorough understanding. Your analysis will be used to determine which Claude Code components (agents, commands, skills, hooks, workflows) this repo needs.

## Analysis Areas

### 1. Architecture
- Entry points (main files, index files, CLI dispatchers)
- Module boundaries and directory structure
- Data flow between components
- Key abstractions and patterns

### 2. Tech Stack
- Languages and runtimes
- Frameworks (web, CLI, testing, etc.)
- Build tools and task runners
- Package managers and dependency management
- CI/CD configuration

### 3. Developer Workflows
- How to build the project
- How to run tests (unit, integration, E2E)
- How to deploy or release
- How to debug common issues
- How to add new features (patterns to follow)

### 4. Domain Concepts
- Specialized terminology and vocabulary
- Business logic patterns
- Configuration knobs and their purposes
- Data models and their relationships

### 5. Pain Points
- TODOs and FIXMEs in the code
- Missing or outdated tests
- Undocumented areas
- Complex code without comments
- Fragile or error-prone workflows
- Missing CI/CD or automation

### 6. CLI Surface
- CLI tools with subcommands (argument parsers, dispatchers)
- Structured output formats (tables, JSON, status codes, colored output)
- Configuration files and their formats
- Scripts in bin/, package.json scripts, Makefile targets

### 7. Ecosystem Integrations
- External services: databases (Supabase, PostgreSQL, Neon, Turso), cloud (AWS, Cloudflare, Vercel), monitoring (Sentry, Datadog), communication (Slack, Notion)
- Package dependencies that suggest MCP server opportunities (check package.json, pyproject.toml, go.mod for client libraries)
- CI/CD and DevOps tooling (GitHub Actions, Docker, Kubernetes)
- Issue tracking (Linear, Jira references)
- Documentation/knowledge management tools
- Existing `.mcp.json` configuration (note what's already configured)

## Mode-Specific Instructions

### If MODE is greenfield:
Full analysis — there is no existing .claude/ directory. Focus on discovering everything this repo needs from scratch.

### If MODE is upgrade:
Focus on what has CHANGED since the repo was last equipped. Look for:
- New dependencies or tools added
- New CLI commands or workflows introduced
- Changed directory structure
- New domain concepts or terminology
- Pain points that emerged since last equipment

### If MODE is audit:
The repo has a hand-built .claude/ directory. Focus on:
- What the existing setup is trying to do
- Whether it matches the repo's actual needs
- Gaps between what exists and what would be ideal
- Quality of existing documentation (CLAUDE.md, README)

## Focus Hint Handling

If the focus hint is non-empty, weight your exploration toward that area. Spend 60% of your analysis on the focus area and 40% on the remaining areas. If the focus hint is empty, distribute effort evenly.

## Output Requirements

Write your findings to docs/optimization/{REPO_NAME}-needs.md using this exact format:

# {REPO_NAME} Needs Analysis

## Executive Summary
[2-3 sentences: What is this repo? What are its primary needs for Claude Code tooling?]

## Quick Reference

| Aspect | Details |
|--------|---------|
| Primary language | [language] |
| Framework | [framework or "none"] |
| Build command | [command] |
| Test command | [command] |
| Entry point | [path/to/main] |
| Package manager | [npm/pip/cargo/etc.] |
| CI/CD | [GitHub Actions/CircleCI/none/etc.] |
| Has CLI | [yes/no — if yes, describe subcommands] |

## Architecture Overview

[High-level structure. Include ASCII diagrams if helpful. Describe module boundaries, key abstractions, data flow.]

## Tech Stack Details

| Category | Technology | Config Location |
|----------|-----------|-----------------|
| Language | [e.g., TypeScript] | [e.g., tsconfig.json] |
| Framework | [e.g., Express] | [e.g., src/app.ts] |
| Testing | [e.g., Jest] | [e.g., jest.config.ts] |
| Build | [e.g., esbuild] | [e.g., build.ts] |
| Linting | [e.g., ESLint] | [e.g., .eslintrc.js] |

## Workflow Discovery

### Build
[How to build. Commands, prerequisites, output.]

### Test
[How to test. Unit, integration, E2E if applicable.]

### Deploy
[How to deploy. Steps, environments, automation.]

### Debug
[Common debugging approaches. Logs, tools, techniques.]

## Domain Glossary

| Term | Meaning |
|------|---------|
| [domain term] | [definition] |

[Include all specialized vocabulary found in comments, docs, variable names.]

## Pain Points

| Category | Finding | Location | Impact |
|----------|---------|----------|--------|
| Missing tests | [description] | [file/dir] | High/Medium/Low |
| Undocumented | [description] | [file/dir] | High/Medium/Low |
| TODO/FIXME | [description] | [file:line] | High/Medium/Low |

## CLI Surface

### Commands

| Command | Purpose | Arguments | Output Format |
|---------|---------|-----------|---------------|
| [cmd] | [purpose] | [args] | [JSON/table/text] |

### Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| [name] | [purpose] | [path] |

## Ecosystem Integrations

| Service/Tool | Detection Source | Usage Pattern |
|---|---|---|
| [e.g., Supabase] | [@supabase/supabase-js in package.json] | [Auth + database] |
| [e.g., GitHub] | [GitHub remote in .git/config] | [Issues, PRs, CI] |

[Note any existing .mcp.json configuration.]

## Recommendations

### High Priority
[Components that would immediately improve daily workflow]

### Medium Priority
[Components that address notable gaps]

### Low Priority
[Nice-to-have improvements]

## Raw Findings

[Everything else. Code snippets. Detailed notes. Full context for the orchestrator to reference during synthesis.]
```

## Tips

1. **Read broadly, not just top-level** — explore src/, tests/, docs/, scripts/, config files
2. **Capture actual commands** — copy exact build/test/deploy commands, don't paraphrase
3. **Note output formats** — if CLI tools produce structured output, capture the format
4. **Domain terms matter** — these become the glossary in the context skill
5. **Pain points drive priority** — the more pain, the higher the impact of fixing it
