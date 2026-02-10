# Optimization Plan Template

Template used by `/repo-optimize` Phase 2 to present the synthesized plan to the user for approval.

## Variables

- `{REPO_NAME}` - Repository basename
- `{MODE}` - greenfield, upgrade, or audit
- `{MODELS_USED}` - Which models contributed (e.g., "Gemini Pro + Codex" or "Gemini Pro + Sonnet (Codex fallback)")
- `{GEMINI_NEED_COUNT}` - Number of needs identified by Gemini
- `{GEMINI_CATEGORIES}` - Categories of needs (e.g., "architecture, CLI, testing")
- `{CODEX_ISSUE_COUNT}` - Number of issues found by Codex
- `{AVG_FRESHNESS}` - Average freshness score of existing components (N/A for greenfield)
- `{TOTAL_TASK_COUNT}` - Total number of upgrade tasks
- `{CONFIG_TASK_COUNT}`, `{COMMAND_TASK_COUNT}`, `{DOCS_TASK_COUNT}` - Per-teammate counts
- `{COMMAND_BLOCKERS}`, `{DOCS_BLOCKERS}` - Blocker descriptions
- `{CONFIG_TASK_ROWS}`, `{COMMAND_TASK_ROWS}`, `{DOCS_TASK_ROWS}` - Filled table rows
- `{PRP_ROWS}` - Rows for deferred PRPs (may be empty)
- `{MCP_SERVER_ROWS}` - MCP server recommendation rows (may be empty if no ecosystem matches)
- `{PLUGIN_ROWS}` - Plugin recommendation rows (may be empty if no ecosystem matches)

## Plan Format

```markdown
# Optimization Plan for {REPO_NAME}

## Mode: {MODE}

## Analysis Summary
- **Gemini Pro** found: {GEMINI_NEED_COUNT} needs across {GEMINI_CATEGORIES}
- **Codex** found: {CODEX_ISSUE_COUNT} issues, avg freshness score: {AVG_FRESHNESS}/100
- **Models used**: {MODELS_USED}

## Upgrade Tasks ({TOTAL_TASK_COUNT} total)

### config-upgrader ({CONFIG_TASK_COUNT} tasks, no blockers — starts immediately)

| # | Task | Impact | Effort |
|---|------|--------|--------|
{CONFIG_TASK_ROWS}

### command-builder ({COMMAND_TASK_COUNT} tasks, blocked by {COMMAND_BLOCKERS})

| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
{COMMAND_TASK_ROWS}

### docs-finalizer ({DOCS_TASK_COUNT} tasks, blocked by {DOCS_BLOCKERS})

| # | Task | Impact | Effort | Blocked By |
|---|------|--------|--------|------------|
{DOCS_TASK_ROWS}

### Deferred (PRPs — complex gaps for later development)

| PRP | Why Complex | Effort Est |
|-----|-------------|------------|
{PRP_ROWS}

### Ecosystem Recommendations (manual install)

#### MCP Servers
| MCP Server | Why | Install |
|---|---|---|
{MCP_SERVER_ROWS}

#### Plugins
| Plugin | Why | Install |
|---|---|---|
{PLUGIN_ROWS}

## Execution Timeline

```
config-upgrader  ║════════════════╗
                 ║ T1,T2,T3      ║──── unblocks T4,T5
                 ║════════════════╝
command-builder  ║════╦══════════════════╗
                 ║ T6 ║ T4,T5 (after T1) ║──── unblocks T7,T8
                 ║════╩══════════════════╝
docs-finalizer              ║═══════════════╗
                  waiting...║ T7,T8,T9      ║
                            ║═══════════════╝
```

## Summary
- **{CONFIG_TASK_COUNT}** config tasks (no blockers)
- **{COMMAND_TASK_COUNT}** command tasks (blocked by context skill)
- **{DOCS_TASK_COUNT}** docs tasks (blocked by commands/workflows)
- **{PRP_COUNT}** PRPs deferred for later
```

## User Options

Present via AskUserQuestion with these choices:
- **Proceed with full plan** — execute all tasks including PRPs
- **Modify plan** — let user adjust tasks or priorities before proceeding
- **Proceed without PRPs** — only direct work, skip complex gaps
