# INDEX.md Template

Use this template when creating a `.claude/INDEX.md` file for a project. This is the lightweight entry point that `/prime` reads instead of the full CLAUDE.md.

## Rules

- **Hard budget**: max 80 lines or ~1200 characters
- Every path in Documentation Map must point to an existing file
- Every hop in Critical Paths must reference concrete backtick-quoted paths
- Purpose and "If you only read one file" are required fields
- Known Drift section is for accepted temporary mismatches (prevents audit noise)

## Template

```markdown
# {PROJECT_NAME}

> **Purpose**: {One sentence — what this project does and why it exists}
> **If you only read one file today**: {path to the single most important file for understanding this project}

## Quick Facts

| Key | Value |
|-----|-------|
| Stack | {e.g., TypeScript, Next.js, PostgreSQL} |
| Deploy | {e.g., Docker on VPS at 1.2.3.4, Vercel, N/A} |
| Entry point | {e.g., src/index.ts, app/main.py} |
| Build | {e.g., npm run build, cargo build} |
| Test | {e.g., npm test, pytest} |
| Package mgr | {e.g., npm, uv, cargo} |

## Documentation Map

| Doc | When to read | Path |
|-----|-------------|------|
| Full reference | Deep work, unfamiliar areas | CLAUDE.md |
| Architecture | Structural changes, new features | docs/ARCHITECTURE.md |
| API reference | Endpoint changes, integration | docs/API.md |
| Deploy guide | Deployment, infra changes | docs/DEPLOY.md |
| Contributing | First PR, conventions | CONTRIBUTING.md |

## Critical Paths

Each hop references concrete paths that exist in the repo:

- **Request flow**: `src/routes/` -> `src/services/` -> `src/db/`
- **Auth**: `src/auth/middleware.ts` -> `src/auth/providers/`
- **Build pipeline**: `tsconfig.json` -> `esbuild.config.ts` -> `dist/`

## Anti-Patterns

- Do NOT {pattern to avoid} -- {what to do instead}
- Do NOT {pattern to avoid} -- {what to do instead}
- Do NOT {pattern to avoid} -- {what to do instead}

## Known Drift

<!-- Accepted temporary mismatches so audits don't create noise -->
<!-- Format: - [DATE] Description of accepted drift (remove when resolved) -->
```

## Usage

1. Copy the template above into `.claude/INDEX.md` in your project
2. Fill in all `{placeholder}` values
3. Remove Documentation Map rows for docs that don't exist
4. Add Critical Paths for your project's key data flows
5. Add 3-5 Anti-Patterns specific to your project
6. Verify all paths exist: every Documentation Map path and Critical Path anchor must resolve

## Validation

`/repo-audit` checks INDEX.md for:
- Line count (>80 lines = flagged)
- Every Quick Facts entry is verifiable against the codebase
- Every Documentation Map path points to an existing file
- Every Critical Path references existing directories/files
- Anti-Patterns are not contradicted by actual code
- Known Drift entries have dates and are still relevant
