# Claude Code Templates

A curated library of Claude Code configuration components—commands, agents, skills, hooks, and workflows—designed to be copied into your projects and kept up-to-date with Claude Code best practices.

## Purpose

This repository serves two goals:

1. **Template Library**: Provide ready-to-use `.claude/` folder components that can be copied into any project
2. **Best Practices Sync**: Maintain alignment with the official Claude Code repository to ensure all templates follow current patterns and conventions

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  claude-code-templates                                      │
│                                                             │
│  ┌──────────────┐     ┌──────────────────────────────────┐ │
│  │ claude-code  │     │ .claude/                         │ │
│  │ (submodule)  │────►│   agents/    (12 agents)         │ │
│  │              │     │   commands/  (10+ commands)      │ │
│  │ Official     │     │   skills/    (12 skills)         │ │
│  │ Reference    │     │   hooks/     (automated checks)  │ │
│  └──────────────┘     │   workflows/ (4 workflow chains) │ │
│         │             └──────────────────────────────────┘ │
│         │                            │                      │
│         ▼                            ▼                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Sync Workflows                                      │   │
│  │ • Check for claude-code updates                     │   │
│  │ • Validate templates against best practices         │   │
│  │ • Update components when patterns change            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### The Submodule

The `claude-code/` submodule points to the [official Anthropic Claude Code repository](https://github.com/anthropics/claude-code). It serves as:

- **Reference Source**: The authoritative source for Claude Code's file formats, conventions, and capabilities
- **Update Trigger**: When the submodule is updated, workflows can detect changes and flag templates that may need revision
- **Documentation**: Direct access to official docs for verifying template correctness

## Component Deployment Architecture

All components live in `.claude/`—the single source of truth. How they're deployed depends on the `deployment` field in `MANIFEST.json`:

```
┌─────────────────────────────────────────────────────────────────┐
│  .claude/  (development directory - ALL components live here)   │
│                                                                 │
│  ┌─────────────────────────┐   ┌────────────────────────────┐  │
│  │  deployment: "global"   │   │  deployment: "template"    │  │
│  │                         │   │                            │  │
│  │  fork-terminal          │   │  (in templates/n8n/)       │  │
│  │  multi-model-orch.      │   │  n8n-code-javascript       │  │
│  │  code-reviewer agent    │   │  n8n-workflow-patterns      │  │
│  │  /orchestrate command   │   │  n8n-validation-expert      │  │
│  │  ...                    │   │  ...                        │  │
│  └───────────┬─────────────┘   └─────────────┬──────────────┘  │
│              │                                │                  │
│              ▼                                ▼                  │
│  install-global.sh              deploy-template.sh              │
│  Symlinks to ~/.claude/         Copies to project .claude/      │
│  Available in ALL projects      Project-specific only            │
└─────────────────────────────────────────────────────────────────┘
```

- **`install-global.sh`** is the authority on what ships globally—run it after updates
- **`MANIFEST.json`** is the component catalog with deployment metadata
- **`REGISTRY.md`** is the human-readable quick-reference

## Using the Templates

### Quick Start

1. Copy the `.claude/` folder to your project:
   ```bash
   cp -r .claude/ /path/to/your/project/
   ```

2. Customize for your project:
   - Edit agent prompts to match your codebase
   - Update command paths in workflows
   - Remove components you don't need (e.g., n8n skills)

3. See [.claude/USER_GUIDE.md](.claude/USER_GUIDE.md) for usage instructions

### What's Included

| Component | Count | Description |
|-----------|-------|-------------|
| Agents | 12 | Specialized sub-agents (code-reviewer, debugger, test-automator, etc.) |
| Commands | 10+ | Slash commands (/onboarding, /code-review, /rca, etc.) |
| Skills | 13 | Reusable patterns (LSP navigation, orchestration, n8n development) |
| Hooks | 4 | Automated checks (type validation, reference checking) |
| Workflows | 4 | Multi-step processes (feature development, bug investigation) |

See [.claude/REGISTRY.md](.claude/REGISTRY.md) for the complete component catalog.

## Keeping Templates Current

### Sync Workflow

The `/sync-reference` command compares templates against the claude-code submodule:

```
/sync-reference
```

This workflow:
1. Checks if the submodule is at the latest release
2. Scans for deprecated patterns or outdated conventions
3. Reports which templates need updates
4. Suggests specific changes based on new best practices

### Updating the Reference

To pull the latest Claude Code changes:

```bash
cd claude-code
git fetch --tags
git checkout <latest-tag>
cd ..
git add claude-code
git commit -m "Update claude-code submodule to <version>"
```

Then run `/sync-reference` to identify any templates needing updates.

## Change Tracking

All changes are automatically logged in [CHANGELOG.md](CHANGELOG.md). A git post-commit hook appends each commit to the log with:
- Date
- Category (extracted from commit message)
- Commit message
- Short hash

### Setup (for contributors)

Install the git hooks after cloning:

```bash
./git-hooks/install.sh
```

This enables automatic changelog updates on each commit.

## Repository Structure

```
claude-code-templates/
├── README.md              # This file
├── MANIFEST.json          # Component catalog with deployment metadata
├── CHANGELOG.md           # Auto-updated change log
├── scripts/
│   ├── install-global.sh  # Symlinks global components to ~/.claude/
│   └── validate-manifest.py  # Ensures MANIFEST.json matches filesystem
├── references/            # Git submodules for learning (not for copying)
│   ├── claude-code/       # Official Anthropic Claude Code reference
│   └── ...                # Other reference repos
├── templates/             # Project-specific template packs
│   └── n8n/               # n8n workflow automation skills
├── git-hooks/             # Git hooks (install with install.sh)
│   ├── post-commit        # Auto-updates CHANGELOG.md
│   └── install.sh         # Hook installer
└── .claude/               # ALL components (source of truth)
    ├── CLAUDE.md          # Configuration overview
    ├── REGISTRY.md        # Human-readable component index
    ├── USER_GUIDE.md      # Usage instructions
    ├── agents/            # Sub-agent definitions
    ├── commands/          # Slash commands
    ├── skills/            # Reusable expertise (fork-terminal, LSP, orchestration)
    ├── hooks/             # Claude Code hooks (automated checks)
    ├── workflows/         # Multi-step processes
    └── rules/             # Development rules
```

## Contributing

When adding or updating templates:

1. Check the `claude-code/` submodule for current conventions
2. Follow existing file format patterns (YAML frontmatter, etc.)
3. Update REGISTRY.md if adding new components
4. Run `/sync-reference` to validate against best practices

## License

Templates in this repository are provided for use with Claude Code. See the [claude-code](https://github.com/anthropics/claude-code) repository for Claude Code licensing.
