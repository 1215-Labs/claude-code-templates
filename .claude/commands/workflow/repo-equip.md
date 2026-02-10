---
name: repo-equip
description: |
  Analyze a target repo and automatically equip it with matching Claude Code components.
  Installs global components, creates repo-specific commands/skills, and documents everything.

  Usage: /repo-equip "<path to repo>" ["optional focus hint"]

  Examples:
  /repo-equip "/Users/mike/my-project"
  /repo-equip "/Users/mike/api-server" "focus on testing and deployment"
  /repo-equip "/Users/mike/cli-tool" "CLI wrapper commands"

  Best for: Equipping any repo with the right Claude Code components
  Use instead: /sync-reference for updating the templates repo itself
argument-hint: "<repo path>" ["focus hint"]
user-invocable: true
related:
  commands: [workflow/sync-reference, workflow/onboarding]
  skills: [repo-equip-engine, skill-evaluator]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Write
  - Grep
  - Glob
  - Task
  - AskUserQuestion
---

# Repo Equipment

**Target**: $ARGUMENTS

Reference the `repo-equip-engine` skill for matching heuristics, gap detection, complexity scoring, and templates throughout this workflow.

## Phase 0: Validation

### Parse Arguments

Extract from `$ARGUMENTS`:
- **First argument**: Target repo path (required) — strip quotes if present
- **Second argument**: Focus hint (optional) — narrows analysis scope

### Validate Target

1. **Path exists**: Verify the directory exists and is accessible
2. **Not this repo**: If the path resolves to the claude-code-templates repo, decline and suggest `/sync-reference` instead
3. **Is a git repo**: Check for `.git/` directory (warn if not, don't block)
4. **Note existing `.claude/`**: Check if target already has a `.claude/` directory — note this for Phase 2 but don't block

### Set Working Variables

- `REPO_PATH`: Absolute path to target repo
- `REPO_NAME`: Directory basename (e.g., `mac-manage`, `api-server`)
- `FOCUS_HINT`: Optional focus string or empty
- `TEMPLATES_REPO`: Path to this claude-code-templates repo

## Phase 1: Parallel Discovery (Use Subagents)

**IMPORTANT**: Launch these as PARALLEL subagents (single message, multiple Task tool calls) to preserve main agent context for matching and synthesis.

### Subagent A: Target Repo Analyzer

Use the **Explore subagent** with "thorough" thoroughness to analyze the target repo at `REPO_PATH`:

**Discover:**
- **Tech stack**: Look for `package.json`, `tsconfig.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, shell scripts
- **Architecture**: Entry points (main files, index files, CLI dispatchers), directory structure, how parts connect
- **CLI tools**: Any CLI with subcommands — look for argument parsers (`case $1`, `argparse`, `commander`, `clap`), `bin/` directories, executable scripts
- **APIs**: REST endpoints, GraphQL schemas, MCP servers (`@modelcontextprotocol`)
- **Key workflows**: Build commands, test commands, deploy commands, lint commands (from package.json scripts, Makefile targets, CI config)
- **Pain points**: TODOs, FIXMEs, missing tests, no CI, no docs, large files without documentation
- **Output formats**: Any structured output (tables, JSON, status codes, colored terminal output, health checks)
- **Ecosystem integrations**: External services used (databases, cloud providers, monitoring, communication tools). Check package.json dependencies, config files (wrangler.toml, vercel.json, .linear), CI/CD references, Docker Compose service names, `.mcp.json` if present
- **Domain terminology**: Specialized terms, glossaries, jargon in comments or docs

If `FOCUS_HINT` is provided, weight exploration toward that area.

Return: Structured summary of tech stack, architecture, CLI tools, APIs, workflows, pain points, output formats, and domain terms.

### Subagent B: Component Library Indexer

Use the **Explore subagent** with "medium" thoroughness to analyze the templates repo:

**Read and index:**
- `MANIFEST.json` at `TEMPLATES_REPO/MANIFEST.json`
- `.claude/REGISTRY.md` at `TEMPLATES_REPO/.claude/REGISTRY.md`

**Build capability index:**
- List every component with: name, type, deployment level, description
- Classify each as: universal (any repo), tech-conditional (needs specific stack), domain-specific (needs specific domain)
- Note which components are already globally deployed

Return: Complete component capability index with classifications.

### Subagent C: Existing Context Reader

Use the **Explore subagent** with "medium" thoroughness to read the target repo's existing documentation:

**Read:**
- `REPO_PATH/CLAUDE.md` — existing Claude Code instructions
- `REPO_PATH/README.md` — project overview
- `REPO_PATH/.claude/` directory — any existing components
- `REPO_PATH/.claude/CLAUDE.md` — project-level instructions if separate

**Determine:**
- Documentation quality (thorough/basic/minimal/none)
- Existing conventions documented
- Areas where AI assistance would clearly help
- Whether repo was previously equipped (look for "Claude Code Commands" section in CLAUDE.md)
- If previously equipped: which components exist, their status

Return: Documentation summary, existing config, previous equipment status.

Wait for all three subagents to complete before proceeding.

## Phase 2: Component Matching

Using the `repo-equip-engine` skill's Component Applicability Matrix and the subagent findings, produce three categorized lists:

### Direct Fit — Existing global components that apply as-is

Check every component from Subagent B's index against Subagent A's tech stack findings:

**Always include (universal):**
- All universal agents: `code-reviewer`, `debugger`, `codebase-analyst`, `test-automator`, `context-manager`, `library-researcher`, `technical-researcher`
- All universal commands: `/code-review`, `/rca`, `/onboarding`, `/deep-prime`, `/quick-prime`, `/remember`, `/forget`, `/memory`, `/all_skills`
- All workflows: `feature-development`, `bug-investigation`, `code-quality`, `new-developer`
- All session hooks

**Conditionally include** based on tech stack signals from Subagent A:
- Typed languages (TS/Rust/Go/Java) → `type-checker`, `lsp-navigator`, `dependency-analyzer`, LSP skills
- Has Dockerfile/CI → `deployment-engineer`
- Has MCP code → `mcp-backend-engineer`
- Has frontend → `/ui-review`, `agent-browser`
- n8n project → all `n8n-*` skills, `n8n-mcp-tester`
- Needs PRP → `/prp-*` commands
- Multi-model → `fork-terminal`, `multi-model-orchestration`, `/orchestrate`

**Action**: Documentation only — these are already globally installed.

### Close Fit — Components that need repo-specific adaptation

Typically a `{REPO_NAME}-context` skill with:
- Repo-specific paths and constants
- CLI commands and their usage
- Output format references
- Domain glossary
- Integration patterns between commands

**Action**: Create the adapted component(s), register in MANIFEST, install.

### Gap — Needs that no existing component addresses

Apply gap detection heuristics from `repo-equip-engine`:

- **CLI with subcommands** → wrapper commands (one per logical group)
- **Domain-specific workflows** → workflow commands
- **Complex output formats** → interpretation commands
- **Recurring procedures** → automation commands

For each gap, score complexity using the `repo-equip-engine` skill:
- **Simple** (score 1-3): Build inline during Phase 4
- **Complex** (score 4+): Generate a PRP document in `PRPs/`

### Ecosystem — MCP Servers & Plugins (manual install)

Using the `repo-equip-engine` skill's Ecosystem MCP Server Signals and Plugin Signals tables, match detected integrations to recommendations:

**MCP Servers**: Cross-reference Subagent A's ecosystem integrations against the MCP Server Signals table. List matches with install commands.

**Plugins**: Cross-reference Subagent A's tech stack against the Plugin Signals table. List matches.

These are advisory — user installs them manually after reviewing. If the target repo already has a `.mcp.json`, note which recommended servers are already configured.

## Phase 3: Present Plan & Confirm

Present the equipment plan to the user in a structured format:

```
# Equipment Plan for {REPO_NAME}

## Direct Fit (already installed globally)
{TABLE: Component | Type | Why it applies}

## Close Fit (need repo-specific adaptation)
{TABLE: Component to Create | Based On | What it adds}

## Gap — New Components
### Simple (will build now)
{TABLE: Command/Skill | Purpose | Complexity Score}

### Complex (will generate PRP)
{TABLE: PRP | Purpose | Why complex}

## Ecosystem Recommendations (manual install)

### MCP Servers
{TABLE: MCP Server | Why | Install Command}

### Plugins
{TABLE: Plugin | Why | Install Command}

## Actions Summary
- {N} existing components documented
- {N} adapted components to create
- {N} simple components to build
- {N} PRPs to generate
```

Use `AskUserQuestion` with options:
- "Proceed with full plan" — execute everything
- "Proceed without gap components" — only direct fit + close fit
- "Modify plan" — let user adjust before proceeding

**NEVER execute without user confirmation.**

## Phase 4: Execute (after confirmation)

Execute in this order:

### Step 1: Create Close-Fit Components

For each close-fit component (typically a context skill):

1. Create the skill directory: `.claude/skills/{REPO_NAME}-context/`
2. Write `SKILL.md` using the Context Skill Template from `repo-equip-engine`
3. Fill in all placeholders with data from Subagent A findings

### Step 1.5: Generate Skill Priorities File

Generate a `skill-priorities.md` for the target repo using the Skill Priorities Template from `repo-equip-engine`:

1. Ensure `.claude/memory/` directory exists in the target repo: `mkdir -p {REPO_PATH}/.claude/memory/`
2. Categorize all installed components into tiers:
   - **Always tier**: `/catchup` + the repo's primary status/overview command (e.g., `/cbass-status`)
   - **Context-Triggered tier**: All repo-specific commands with trigger keywords describing when to activate
   - **Available tier**: Universal commands like `/code-review`, `/deep-prime`, `/remember`
3. Fill in the **Repo Context** section with domain, command prefix, and context skill name
4. Write to `{REPO_PATH}/.claude/memory/skill-priorities.md`

### Step 2: Create Simple Gap Components

For each simple gap component:

1. Create the command directory if needed: `.claude/commands/{REPO_NAME}/`
2. Write command `.md` file using the Command Template from `repo-equip-engine`
3. Fill in all placeholders with data from Subagent A findings
4. Reference the context skill for shared knowledge

### Step 3: Generate PRPs for Complex Gaps

For each complex gap:

1. Create `PRPs/` directory if needed
2. Write a PRP document following the project's PRP conventions
3. Include: context from Subagent A, requirements, suggested approach, complexity notes

### Step 4: Update MANIFEST.json

Read `TEMPLATES_REPO/MANIFEST.json`, then for each new component:

1. Add skill entries to `components.skills[]`
2. Add command entries to `components.commands[]`
3. All new entries get `"deployment": "global"` and `"status": "beta"`
4. Write the updated MANIFEST.json

**Validate**: Run `python3 scripts/validate-manifest.py` to verify sync.

### Step 5: Update REGISTRY.md

Read `TEMPLATES_REPO/.claude/REGISTRY.md`, then:

1. Add a Quick Lookup row for the main new command(s)
2. Add a new section (like "Mac Management") for the repo's components
3. Update Component Counts table
4. Update Cross-Reference Map if applicable

### Step 6: Run Installer

```bash
python3 scripts/install-global.py
```

Verify output shows new components installed without errors.

### Step 7: Validate

1. Run `python3 scripts/validate-manifest.py` — must exit 0
2. Verify new symlinks exist in `~/.claude/commands/` and `~/.claude/skills/`
3. Check for broken symlinks

## Phase 5: Document in Target Repo

### Update Target CLAUDE.md

Read `REPO_PATH/CLAUDE.md` (create if it doesn't exist).

**If CLAUDE.md doesn't exist**, create one with basic structure:
```markdown
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

{OVERVIEW_FROM_README}

## Commands

{COMMANDS_FROM_SUBAGENT_A}

## Architecture

{ARCHITECTURE_FROM_SUBAGENT_A}
```

**Add/replace "## Claude Code Commands" section** using the CLAUDE.md Section Template from `repo-equip-engine`. Follow the exact pattern from the mac-manage CLAUDE.md:

1. **Intro sentence** explaining the commands are globally installed AI wrappers
2. **Command reference table** with command name and description
3. **Recommended Workflows** section with common use cases
4. **How They Work** section explaining the AI enhancement layer
5. **General-Purpose Commands** subsection listing universal commands
6. **Ecosystem Setup** subsection (if ecosystem recommendations were generated) listing recommended MCP servers with install commands and recommended plugins with install commands

If re-running (section already exists), replace everything between `## Claude Code Commands` and the next `##` heading (or end of file).

### Verify Documentation

Read back the updated CLAUDE.md to confirm:
- Section renders correctly
- Command names match what was created
- No broken references
- Skill priorities file exists at `{REPO_PATH}/.claude/memory/skill-priorities.md`

## Output Summary

After completing all phases, provide:

1. **Equipment Summary**:
   - Components created (with paths)
   - Components documented (direct fit count)
   - Skill priorities file generated (path)
   - PRPs generated (if any)

2. **What's New in the Target Repo**:
   - New commands available (with usage examples)
   - New context skill (what knowledge it contains)

3. **Next Steps**:
   - Suggest running `/all_skills` in the target repo to verify
   - If PRPs were generated, suggest running `/prp-claude-code-execute` on them
   - Suggest running the new commands to test them

## Related Commands

- `/sync-reference` — Sync templates against claude-code reference
- `/onboarding` — Get familiar with any project
- `/all_skills` — Verify installed components
