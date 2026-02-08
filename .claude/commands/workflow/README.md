# Developer Workflow Commands

A suite of Claude Code commands for streamlined development workflows. These commands auto-discover project context from CLAUDE.md and adapt to any codebase.

## Quick Start

| Command | Purpose | Usage |
|---------|---------|-------|
| `/catchup` | Resume session | `/catchup` |
| `/onboarding` | New developer intro | `/onboarding` |
| `/quick-prime` | Fast context | `/quick-prime` |
| `/deep-prime` | Deep context | `/deep-prime "area" "focus"` |
| `/code-review` | Review changes | `/code-review [PR/branch/file]` |
| `/rca` | Debug issues | `/rca "error message"` |
| `/coderabbit-helper` | Analyze suggestions | `/coderabbit-helper [paste]` |
| `/ui-review` | UI consistency | `/ui-review src/components/` |

## Workflow

```
Resume work   ──► /catchup
                      │
                      ▼
New developer ──► /onboarding
                      │
                      ▼
Get context   ──► /quick-prime or /deep-prime
                      │
                      ▼
Make changes  ──► (edit code)
                      │
                      ▼
Review        ──► /code-review
                      │
                      ▼
Debug issues  ──► /rca (if needed)
```

## How Arguments Work

Commands receive user input via `$ARGUMENTS` in the command file.

### No Arguments

Some commands work without arguments:

```
/quick-prime
/onboarding
```

### Single Argument

Pass one value:

```
/rca "connection timeout error"
/code-review 123
/ui-review src/components/
```

### Multiple Arguments

Pass multiple quoted values:

```
/deep-prime "backend" "API routes"
/deep-prime "frontend" "Focus on state management"
```

### Flexible Input Types

`/code-review` accepts various input types:
- Empty → reviews staged changes
- `123` → reviews PR #123
- `feature-branch` → compares branch to main
- `src/api/routes.ts` → reviews specific file

## Context Discovery

Commands automatically discover project information. No hardcoded paths!

### Discovery Priority

1. **CLAUDE.md** (primary) - Project overview, structure, conventions
2. **README.md** (fallback) - Project description
3. **Config files** - Detects tech stack:
   - `package.json` + `tsconfig.json` → TypeScript/JavaScript
   - `pyproject.toml` → Python
   - `Cargo.toml` → Rust
   - `go.mod` → Go
   - `docker-compose.yml` → Multi-service

### Recommended CLAUDE.md Sections

For best command behavior, include these sections in your project's CLAUDE.md:

```markdown
## Overview
[Project name and purpose - commands use this for report headers]

## Project Structure
[Directory layout - commands use this for exploration]

## Where to Look
[Task-to-location mapping - commands use this to find relevant files]

| Task | Location |
|------|----------|
| Add API endpoint | `src/api/routes/` |
| Add component | `src/components/` |
| Add test | `tests/` |

## Conventions
[Patterns to follow - commands enforce these during review]

## Anti-Patterns
[Things to avoid - commands flag these during review]

## Testing
[How to run tests - commands use these for verification]
```

## Command Details

### /onboarding

Interactive onboarding for new developers.

**Arguments**: none

**What it does**:
1. Reads CLAUDE.md and README.md to understand the project
2. Detects tech stack from config files
3. Presents architecture overview
4. Asks user to choose a focus area
5. Deep dives into chosen area
6. Suggests a first contribution with step-by-step guide

**Output**: Interactive conversation with structured report

---

### /quick-prime

Fast context building for quick tasks.

**Arguments**: none

**What it does**:
1. Reads CLAUDE.md and README.md
2. Explores directory structure
3. Detects tech stack
4. Reads key entry points

**Output**: 4-point summary (Purpose, Architecture, Patterns, Tech Stack)

---

### /deep-prime

Deep context priming for specific work areas.

**Arguments**: `"<area>" "<special focus>"`

**Examples**:
```
/deep-prime "frontend" "React components"
/deep-prime "backend" "database queries"
/deep-prime "tests" "integration testing"
```

**What it does**:
1. Reads CLAUDE.md "Where to Look" section for the area
2. Creates intelligent reading plan
3. Reads files and follows imports
4. Builds todo list of files to explore
5. Synthesizes understanding

**Output**: Ready to work on that area with full context

---

### /code-review

Comprehensive code review with report generation.

**Arguments**: PR number, branch name, file path, or empty for staged changes

**Examples**:
```
/code-review              # Review staged changes
/code-review 123          # Review PR #123
/code-review feature-xyz  # Review branch vs main
/code-review src/api.ts   # Review specific file
```

**What it does**:
1. Discovers project conventions from CLAUDE.md
2. Detects tech stack for appropriate checks
3. Reviews code for quality, security, patterns
4. Applies error handling philosophy (if beta project)
5. Generates detailed report

**Output**: `code-review.md` (or `code-review[n].md` if exists)

---

### /rca

Root cause analysis for debugging issues.

**Arguments**: Issue description or error message

**Examples**:
```
/rca "API returns 500 on login"
/rca "Tests failing after merge"
/rca "Connection timeout in production"
```

**What it does**:
1. Discovers architecture from CLAUDE.md
2. Runs health checks appropriate to project type
3. Analyzes error patterns
4. Traces to root cause
5. Generates actionable report

**Output**: `RCA.md` with symptoms, root cause, and resolution steps

---

### /coderabbit-helper

Analyze CodeRabbit (or similar) code review suggestions.

**Arguments**: Paste the suggestion text

**What it does**:
1. Discovers project phase from CLAUDE.md
2. Analyzes if suggestion is valid
3. Considers project context and priorities
4. Generates 2-5 options with tradeoffs
5. Recommends best option

**Output**: Structured analysis with options and recommendation

---

### /ui-review

UI consistency and pattern analysis.

**Arguments**: Component path or directory

**Examples**:
```
/ui-review src/components/
/ui-review src/pages/Dashboard.tsx
/ui-review app/
```

**What it does**:
1. Looks for UI_STANDARDS.md or infers from existing components
2. Scans components for consistency issues
3. Checks accessibility, TypeScript, styling patterns
4. Analyzes against project standards

**Output**: `ui-review-[feature].md` with scores and issues

---

## Customization

### Adding Project-Specific Context

The more complete your CLAUDE.md, the better commands work. Include:

- Specific file paths for different tasks
- Code patterns required by your team
- Testing requirements
- Error handling philosophy
- Security considerations

### Tech Stack Auto-Detection

Commands automatically adapt to your tech stack:

| Detected | Review Focus |
|----------|-------------|
| TypeScript | Types, `any` usage, React patterns |
| Python | Type hints, logging vs print, async patterns |
| Rust | Result handling, unwrap() usage |
| Go | Error handling, defer patterns |

## Related Resources

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- Commands are defined in `.claude/commands/*.md`
- Customize by editing command files directly
