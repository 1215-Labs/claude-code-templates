---
name: sync-reference
description: |
  Compare skillz against claude-code reference submodule using parallel explorers.
  Tracks sync state and generates prioritized recommendations.

  Usage: /sync-reference [--update-submodule] [--full]
  Examples:
  /sync-reference                    # Quick comparison
  /sync-reference --full             # Deep analysis
  /sync-reference --update-submodule # Update submodule first
argument-hint: [--update-submodule] [--full]
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Write
  - Grep
  - Glob
  - Bash(git *)
  - Task
---

# Reference Sync Command

Compare skillz components against the claude-code reference submodule to identify best practices, new patterns, and recommended updates.

## Configuration

**Submodule**: `references/claude-code/` (https://github.com/anthropics/claude-code.git)
**Sync Log**: `.claude/reference-sync.local.md`
**Report Output**: `reference-sync-report.md`

## Phase 0: Preparation

### Parse Flags

Check arguments for:
- `--update-submodule`: Update submodule before comparison
- `--full`: Enable deep analysis mode (more thorough but longer)

### Update Submodule (if --update-submodule)

```bash
git submodule update --remote references/claude-code
```

Report if submodule was updated to a new version.

### Load Previous Sync State

Read `.claude/reference-sync.local.md` if it exists:
- Extract `last_sync_date`, `last_commit`, `mode`
- Use for "What's New Since Last Sync" comparison

### Get Current State

```bash
git -C references/claude-code rev-parse HEAD
git -C references/claude-code describe --tags --always
```

Store current commit hash and tag for the sync log.

## Phase 1: Parallel Discovery (Use Subagents)

**IMPORTANT**: Launch these explorations as PARALLEL subagents to preserve main agent context for synthesis and report generation.

### Subagent 1: Plugin Structure Explorer

Use the **Explore subagent** with "thorough" thoroughness to analyze `references/claude-code/plugins/`:

**Discover:**
- Plugin manifest structure (`plugin.json` patterns)
- Directory organization conventions
- File naming patterns
- Configuration approaches

**Return:** Summary of plugin structural patterns and conventions.

### Subagent 2: Commands/Agents/Skills Explorer

Use the **Explore subagent** with "thorough" thoroughness to analyze:
- `references/claude-code/plugins/*/commands/` - Command patterns
- `references/claude-code/plugins/*/agents/` - Agent definitions
- `references/claude-code/plugins/*/skills/` - Skill structures

**Discover:**
- Frontmatter fields and conventions
- Description best practices
- Tool allowlists patterns
- Argument handling approaches

**Return:** Summary of component conventions and notable patterns.

### Subagent 3: Hooks & New Features Explorer

Use the **Explore subagent** with "thorough" thoroughness to analyze:
- `references/claude-code/plugins/*/hooks/` - Hook implementations
- Any new directories or component types not in skillz
- Claude Code documentation for recent features

**Discover:**
- Hook event types and patterns
- New hook API features
- New component types or capabilities
- Configuration file formats

**Return:** List of new features, hook patterns, and capabilities.

Wait for all subagents to complete before proceeding.

## Phase 2: Compare Against skillz

### Enumerate skillz Components

Inventory current skillz structure:
```
.claude/
├── agents/      # Count and list
├── commands/    # Count and list
├── skills/      # Count and list
├── hooks/       # Count and list
├── workflows/   # Count and list
└── rules/       # Count and list
```

### Gap Analysis

Compare subagent findings against skillz inventory:

1. **Missing Features**: Components in claude-code but not in skillz
2. **Pattern Differences**: Different approaches to same tasks
3. **Outdated Approaches**: skillz patterns that differ from current best practices
4. **Naming Conventions**: Inconsistencies with reference patterns

For `--full` mode: Also analyze individual file contents for detailed pattern comparison.

## Phase 3: Prioritize Findings

Score each finding by impact and effort:

| Priority | Criteria |
|----------|----------|
| **Critical** | Security, breaking changes, deprecated patterns |
| **High** | New capabilities that enhance productivity significantly |
| **Medium** | Better patterns, improved conventions |
| **Low** | Minor improvements, optional enhancements |

Group recommendations by priority level.

## Phase 4: Generate Report

Write `reference-sync-report.md` with the following structure:

```markdown
# Reference Sync Report

**Generated**: [Today's date]
**claude-code version**: [tag/commit]
**skillz commit**: [current HEAD]
**Mode**: [quick/full]

## Executive Summary

[2-3 sentence overview of key findings]

## What's New Since Last Sync

[If previous sync exists, show changes since then]
[Otherwise: "First sync - baseline established"]

## Recommended Updates

### Critical Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| ... | ... | ... |

### High Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| ... | ... | ... |

### Medium Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| ... | ... | ... |

### Low Priority

| Component | Issue | Recommendation |
|-----------|-------|----------------|
| ... | ... | ... |

## Pattern Comparison

### Frontmatter Conventions

| Field | claude-code | skillz | Status |
|-------|-------------|--------|--------|
| ... | ... | ... | Match/Differs |

### Directory Structure

[Comparison of organization approaches]

### Naming Conventions

[Comparison of file and component naming]

## Plugins Worth Adopting

[List of reference plugins with notable patterns]

## Hook Patterns

[Summary of hook implementations and patterns]

## Action Items

### Immediate (Critical)
- [ ] [Action item]

### Short-term (High Priority)
- [ ] [Action item]

### Long-term (Medium/Low)
- [ ] [Action item]
```

## Phase 5: Update Sync Log

Write `.claude/reference-sync.local.md`:

```markdown
---
last_sync_date: "[ISO timestamp]"
last_commit: "[claude-code commit hash]"
skillz_commit: "[skillz HEAD commit]"
mode: "[quick/full]"
---

# Reference Sync Log

## Latest Sync: [date]

- **claude-code version**: [tag/commit]
- **Findings**: [count by priority]
- **Report**: reference-sync-report.md

## Sync History

[Append previous sync entries, keep last 10]
```

## Output Summary

After completing all phases, provide:

1. **Summary Stats**:
   - Components analyzed in claude-code
   - Gaps identified
   - Recommendations by priority

2. **Top 3 Recommendations**: Most impactful changes to make

3. **Next Steps**: Suggest running specific commands or agents to implement recommendations

## Related Commands

- `/deep-prime "references/claude-code" "plugin patterns"` - Deep dive into reference
- `/code-review` - Review skillz components for quality
- `/onboarding` - Get familiar with skillz structure
