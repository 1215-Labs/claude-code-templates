---
name: repo-equip-engine
description: Matching heuristics, gap detection, complexity scoring, and templates for automated component integration into target repos
version: 1.0.0
category: orchestration
user-invocable: false
related:
  commands: [workflow/repo-equip]
  skills: [skill-evaluator, multi-model-orchestration]
---

# Repo Equip Engine

Shared logic referenced by `/repo-equip`. Do NOT invoke directly.

## Component Applicability Matrix

### Universal Components (any repo)

These apply to every repo and are already globally installed. Document them, don't reinstall.

| Component | Type | Why Universal |
|-----------|------|---------------|
| `code-reviewer` | Agent | Every repo benefits from code review |
| `debugger` | Agent | Every repo has bugs |
| `codebase-analyst` | Agent | Pattern discovery works on any codebase |
| `test-automator` | Agent | Every repo should have tests |
| `context-manager` | Agent | Context management is always useful |
| `library-researcher` | Agent | Any repo may use external libraries |
| `technical-researcher` | Agent | Technical research is universal |
| `/code-review` | Command | Pre-merge validation |
| `/rca` | Command | Root cause analysis |
| `/onboarding` | Command | New developer experience |
| `/deep-prime` | Command | Area-specific context |
| `/quick-prime` | Command | Quick project overview |
| `/remember`, `/forget`, `/memory` | Commands | Persistent memory |
| `/all_skills` | Command | Skill discovery |
| All 4 workflows | Workflow | Feature dev, bug investigation, code quality, new developer |
| All session hooks | Hook | Session init, memory, security, verification |

### Tech-Conditional Components

Match these based on detected tech stack:

| Signal | Component | Type |
|--------|-----------|------|
| `tsconfig.json`, `*.ts` files | `type-checker` agent | Agent |
| `tsconfig.json`, `*.ts` files | `lsp-navigator` agent | Agent |
| `tsconfig.json`, `*.ts` files | `lsp-symbol-navigation` skill | Skill |
| `tsconfig.json`, `*.ts` files | `lsp-type-safety-check` skill | Skill |
| `tsconfig.json`, `*.ts` files | `lsp-dependency-analysis` skill | Skill |
| `tsconfig.json`, `*.ts` files | `dependency-analyzer` agent | Agent |
| Typed languages (TS, Rust, Go, Java) | `type-checker` agent | Agent |
| `Dockerfile`, `.github/workflows/`, CI config | `deployment-engineer` agent | Agent |
| MCP server code, `@modelcontextprotocol` | `mcp-backend-engineer` agent | Agent |
| Frontend files (React, Vue, Svelte, HTML) | `/ui-review` command | Command |
| Frontend with URLs to test | `agent-browser` skill | Skill |
| n8n project (`n8n` in package.json) | All `n8n-*` skills + `n8n-mcp-tester` agent | Multiple |
| PRP workflow needed | `/prp-*` commands | Commands |
| Multi-model delegation needed | `fork-terminal`, `multi-model-orchestration`, `/orchestrate` | Multiple |

### Domain-Specific Components (require new creation)

These signal the need for new, repo-specific components:

| Signal | What to Create |
|--------|----------------|
| CLI with subcommands | Wrapper commands (one per subcommand or logical group) |
| Structured output formats | Context skill with output format glossary |
| Domain-specific terminology | Context skill with domain glossary |
| Recurring multi-step workflows | Workflow commands |
| External APIs with complex responses | Interpretation commands |
| Configuration with many knobs | Status/audit commands |

### Ecosystem: MCP Server Signals

Match detected external service integrations to MCP server recommendations. These are advisory — the user installs them manually via `claude mcp add`.

| Codebase Signal | MCP Server | Install | Value |
|-----------------|-----------|---------|-------|
| Popular npm packages (React, Vue, Express, FastAPI, etc.) | context7 | `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` | Live docs instead of stale training data |
| React/Vue/Next.js frontend | Playwright MCP | `claude mcp add playwright -- npx @anthropic-ai/mcp-playwright@latest` | Browser automation, UI testing, screenshots |
| `@supabase/supabase-js` in deps | Supabase MCP | `claude mcp add supabase` | Direct DB queries, auth, storage |
| `pg` or `postgres` in deps | PostgreSQL MCP | `claude mcp add postgres` | Query, schema inspection, data analysis |
| GitHub remote in `.git/config` | GitHub MCP | `claude mcp add github` | Issues, PRs, Actions, releases |
| `.linear` files or `ABC-123` issue refs | Linear MCP | `claude mcp add linear` | Issue tracking, sprint management |
| `@aws-sdk/*` in deps | AWS MCP | `claude mcp add aws` | Cloud resource management |
| `@sentry/*` in deps | Sentry MCP | `claude mcp add sentry` | Error investigation, root cause analysis |
| `docker-compose.yml` present | Docker MCP | `claude mcp add docker` | Container management, logs |
| Slack webhook URLs in code | Slack MCP | `claude mcp add slack` | Team notifications, incident response |
| `wrangler.toml` or Cloudflare deps | Cloudflare MCP | `claude mcp add cloudflare` | Workers, Pages, R2, D1 |
| `vercel.json` or Vercel deps | Vercel MCP | `claude mcp add vercel` | Deployment configuration |
| K8s manifests or Helm charts | Kubernetes MCP | `claude mcp add kubernetes` | Cluster management, pod operations |
| Notion workspace references | Notion MCP | `claude mcp add notion` | Documentation, knowledge base |
| Neon serverless Postgres | Neon MCP | `claude mcp add neon` | Serverless database operations |
| Turso/libSQL usage | Turso MCP | `claude mcp add turso` | Edge database operations |
| GitLab remote | GitLab MCP | `claude mcp add gitlab` | GitLab issues, MRs, pipelines |
| Datadog integration | Datadog MCP | `claude mcp add datadog` | APM, logs, metrics |

**Team sharing tip**: Check `.mcp.json` into git so the entire team gets the same MCP servers.

### Ecosystem: Plugin Signals

Match detected tech stack and workflow patterns to plugin recommendations. Users install via `claude plugin install <name>`.

| Codebase Signal | Plugin | What It Adds |
|-----------------|--------|-------------|
| PR-based workflow (GitHub PRs) | pr-review-toolkit | Specialized review agents (code, tests, types) |
| Git commits needed | commit-commands | `/commit`, `/commit-push-pr` commands |
| React/Vue/Angular frontend | frontend-design | Production UI generation skill |
| Automation rules needed | hookify | Hook creation from conversation patterns |
| TypeScript project | typescript-lsp | TypeScript LSP integration |
| Python project | pyright-lsp | Python LSP integration |
| Go project | gopls-lsp | Go LSP integration |
| Rust project | rust-analyzer-lsp | Rust LSP integration |
| C/C++ project | clangd-lsp | C/C++ LSP integration |
| Java project | jdtls-lsp | Java LSP integration |
| Security-sensitive code (auth, payments) | security-guidance | Security warnings on edit |
| Learning/onboarding context | explanatory-output-style | Educational code insights |
| Building Claude Code plugins | plugin-dev | Skills for creating skills, hooks, commands |

## Gap Detection Heuristics

### CLI Wrapper Signals

A target repo likely needs CLI wrapper commands when:
1. **Has a CLI entry point** — `bin/` scripts, `main.sh`, `cli.py`, a `"bin"` field in `package.json`
2. **CLI has subcommands** — dispatcher pattern (`case $1 in ...`, argparse with subparsers, commander.js)
3. **Subcommands produce structured output** — tables, JSON, status codes, colored output
4. **Output requires interpretation** — security findings, health checks, diffs, metrics

### Context Skill Signals

A target repo needs a context skill when:
1. **Domain glossary exists** — specialized terminology (medical codes, financial instruments, protocol names)
2. **Output formats are non-obvious** — status prefixes, color codes, structured reports
3. **Multiple commands share constants** — paths, config keys, environment variables
4. **Integration patterns exist** — "after running X, you should run Y"

### Workflow Command Signals

A target repo benefits from workflow commands when:
1. **Multi-step procedures exist** — "to deploy: first X, then Y, then Z"
2. **Conditional logic is complex** — "if X fails, do Y; if Z, do W"
3. **Regular cadence tasks** — weekly reviews, daily checks, release processes

## Complexity Scoring

### Simple (build inline during Phase 4)

Score: 1-3 points. Build directly.

- Single CLI subcommand wrapper (+1)
- Template-based output (no interpretation needed) (+1)
- No shared state with other commands (+1)

Examples:
- `/repo-health` wrapping `./tool.sh health`
- `/repo-build` wrapping `npm run build` with error interpretation
- `/repo-test` wrapping `pytest` with failure analysis

### Complex (generate PRP for later development)

Score: 4+ points. Generate a PRP document in `PRPs/`.

- Multiple interacting commands (+2)
- Deep domain knowledge needed (+2)
- Requires new agent definition (+2)
- Needs persistent state between runs (+2)
- Complex output interpretation (not just pass/fail) (+1)

Examples:
- Full monitoring system with multiple dashboards
- Multi-service orchestration with dependency graphs
- Domain-specific code generation with validation

## Templates

### Context Skill Template

```markdown
---
name: {REPO_NAME}-context
description: Shared knowledge base for {REPO_NAME} slash commands — paths, output formats, glossaries, and integration patterns
version: 1.0.0
category: {CATEGORY}
user-invocable: false
related:
  commands: [{COMMAND_LIST}]
  workflows: [bug-investigation]
---

# {REPO_NAME} Context

Shared context referenced by all `/{REPO_PREFIX}-*` commands. Do NOT invoke directly.

## Paths & Constants

| Variable | Value |
|----------|-------|
| `{REPO_NAME_UPPER}_DIR` | `{REPO_PATH}` |
{PATH_ENTRIES}

## CLI Commands

```
{CLI_COMMANDS}
```

## Output Format Reference

{OUTPUT_FORMATS}

## Glossary

{GLOSSARY}

## Integration Patterns

{INTEGRATION_PATTERNS}
```

### Command Template

```markdown
---
name: {COMMAND_NAME}
description: |
  {DESCRIPTION}

  Usage: /{COMMAND_NAME} {USAGE_ARGS}

  {EXAMPLES}

  Best for: {BEST_FOR}
  See also: {SEE_ALSO}
argument-hint: "{ARGUMENT_HINT}"
user-invocable: true
related:
  commands: [{RELATED_COMMANDS}]
  skills: [{REPO_NAME}-context]
  workflows: [bug-investigation]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# {TITLE}

**User context**: $ARGUMENTS

Reference the `{REPO_NAME}-context` skill for paths, output formats, and glossaries.

## Step 1: {FIRST_STEP}

{STEP_CONTENT}

## Step 2: {SECOND_STEP}

{STEP_CONTENT}

## Step 3: Present Results

{RESULTS_FORMAT}
```

### Skill Priorities Template

Write to `{REPO_PATH}/.claude/memory/skill-priorities.md`:

```markdown
# Skill Priorities

## Always (invoke proactively every session)
- `/catchup` - Resume session with briefing (run first thing)
{ALWAYS_ENTRIES}

## Context-Triggered (invoke when topic matches)
{CONTEXT_ENTRIES}

## Available (use when explicitly relevant)
- `/code-review` - Before merging or pushing
- `/deep-prime "area"` - When diving into unfamiliar code
- `/remember "fact"` - When discovering reusable knowledge

## Repo Context
- **Primary domain**: {DOMAIN}
- **Key commands prefix**: `/{PREFIX}-*`
- **Context skill**: `{REPO_NAME}-context`
```

**Tier assignment rules:**
- **Always**: `/catchup` + the repo's primary status/overview command (e.g., `/{PREFIX}-status`)
- **Context-Triggered**: All repo-specific commands, with a brief trigger description (e.g., "When checking service health")
- **Available**: Universal commands that apply to any repo
- **Repo Context**: Domain, command prefix, and context skill name from the analysis

### MANIFEST.json Entry Snippets

**Skill entry:**
```json
{
  "name": "{REPO_NAME}-context",
  "path": ".claude/skills/{REPO_NAME}-context",
  "deployment": "global",
  "status": "beta",
  "description": "Shared knowledge base for {REPO_NAME} slash commands"
}
```

**Command entry:**
```json
{
  "name": "{COMMAND_DIR}/{COMMAND_NAME}",
  "path": ".claude/commands/{COMMAND_DIR}/{COMMAND_NAME}.md",
  "deployment": "global",
  "status": "beta",
  "description": "{DESCRIPTION}"
}
```

### CLAUDE.md Section Template

```markdown
## Claude Code Commands

{INTRO_SENTENCE}

| Command | What it does |
|---------|-------------|
{COMMAND_TABLE_ROWS}

### Recommended Workflows

{WORKFLOW_SECTIONS}

### How They Work

{HOW_EXPLANATION}

The shared knowledge base lives in the `{REPO_NAME}-context` skill (installed globally at `~/.claude/skills/{REPO_NAME}-context/`). It contains paths, output format references, {GLOSSARY_DESCRIPTION}.

### General-Purpose Commands

These commands work in any repo and are always available:

| Command | What it does |
|---------|-------------|
| `/quick-prime` | Fast 4-point project context |
| `/deep-prime "area" "focus"` | Deep analysis of a specific area |
| `/code-review` | Comprehensive code review with report |
| `/rca "error"` | Root cause analysis for issues |
| `/onboarding` | Interactive project introduction |
| `/remember "fact"` | Store a preference or decision |
| `/memory` | View and search stored memory |
```

## Re-Run Detection

When `/repo-equip` is run against a previously equipped repo:

1. **Check MANIFEST.json** for components whose name starts with the repo name or whose description mentions the repo
2. **Check target repo's CLAUDE.md** for existing "## Claude Code Commands" section
3. **Show "Already Equipped" list** — existing components with their status
4. **Only suggest additions** — new components not yet created, or updates to existing ones
5. **For CLAUDE.md updates** — replace the existing block between `## Claude Code Commands` and the next `##` heading
