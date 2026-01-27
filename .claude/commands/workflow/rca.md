---
name: rca
description: |
  Generate Root Cause Analysis report using parallel diagnostic subagents

  Usage: /rca "<issue description or error message>"

  Examples:
  /rca "Login endpoint returning 500 errors"
  /rca "Memory usage growing unbounded after 24h"
  /rca "Tests passing locally but failing in CI"
  /rca "Service not starting after deployment"

  Best for: Production issues, system-wide problems, mysterious failures
  Use instead: /deep-prime when investigating a specific code area
  Use instead: /code-review for code quality issues in PRs
argument-hint: "<error or issue description>"
user-invocable: true
related:
  agents: [debugger, dependency-analyzer]
  skills: [lsp-dependency-analysis]
  workflows: [bug-investigation]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Write
  - Task
---

# Root Cause Analysis

**Issue to investigate**: $ARGUMENTS

Investigate this issue systematically using parallel subagents for diagnostics, then generate an RCA report saved to `RCA.md` in the project root.

## Phase 1: Parallel Context & Diagnostics (Use Subagents)

**IMPORTANT**: Launch these as PARALLEL subagents to preserve main agent context for root cause synthesis.

### Subagent 1: Project Context Explorer
Use the **Explore subagent** with "medium" thoroughness to extract from CLAUDE.md:
- Architecture and how services connect
- Configuration approach
- Error handling philosophy (if mentioned)
- Testing patterns

Also detect project type from:
- `docker-compose.yml` - Multi-service architecture
- `package.json` - Node.js/TypeScript project
- `pyproject.toml` - Python project
- `Cargo.toml` - Rust project
- `go.mod` - Go project

Return: Project type, architecture summary, error handling conventions.

### Subagent 2: System Health Diagnostics
Use the **general-purpose subagent** to run health checks based on project type:

**For Docker-based projects:**
```bash
docker-compose ps
docker-compose logs --tail=50 [service-name]
```

**For Node.js projects:**
```bash
npm run build 2>&1 | head -50
npm test 2>&1 | head -50
```

**For Python projects:**
```bash
python -c "import your_module"
pytest -x 2>&1 | head -50
```

Return: Health check results, any errors or failures found.

### Subagent 3: Recent Changes Analyzer
Use the **Explore subagent** with "thorough" thoroughness to:
```bash
git log --oneline -20
git diff main...HEAD --stat
```
- Identify recent commits that may relate to the issue
- Check for changes in configuration or dependencies
- Note any relevant commit messages mentioning fixes or changes

Return: List of potentially relevant recent changes with commit hashes.

### Subagent 4: Error Pattern Scanner
Use the **Explore subagent** with "thorough" thoroughness to:
- Search logs for ERROR, Exception, Failed patterns
- Grep codebase for error handling related to the issue
- Identify where errors might be swallowed or hidden

```bash
grep -r "ERROR\|Exception\|Failed" logs/ 2>/dev/null | head -50
```

Return: Error patterns found, potential error swallowing locations.

Wait for all subagents to complete before proceeding.

## Phase 2: Consolidate Diagnostics

Synthesize subagent findings into:
1. **System State**: Health check results summary
2. **Recent Changes**: Potentially relevant commits
3. **Error Patterns**: Where errors are occurring or being hidden
4. **Investigation Targets**: Specific code paths to examine

## Phase 3: Deep Investigation (Subagent)

Use the **general-purpose subagent** for targeted root cause investigation:

Based on consolidated diagnostics:
1. Follow error stack traces to the source
2. Check if errors are being swallowed somewhere
3. Look for missing error handling where it should fail fast
4. Identify dependency or initialization order problems
5. Trace the code path from symptom to root cause

Return: Root cause hypothesis with evidence and specific file:line references.

## Phase 4: Impact Analysis (Main Agent)

With main context preserved, determine scope:
- Which features are affected?
- Is this a startup failure or runtime issue?
- Is there data loss or corruption risk?
- Are errors propagating correctly or being hidden?

## Phase 5: Generate RCA Report

Generate an `RCA.md` report:

```markdown
# Root Cause Analysis

**Date**: [Today's date]
**Project**: [Project name from CLAUDE.md]
**Issue**: [Brief description]
**Severity**: [Critical/High/Medium/Low]

## Summary

[One paragraph overview of the issue and its root cause]

## Investigation

### Symptoms

- [What was observed]

### Diagnostics Performed

- [Health checks run - from Subagent 2]
- [Logs examined - from Subagent 4]
- [Code reviewed - from Subagent 3]

### Root Cause

[Detailed explanation from Phase 3 investigation]

## Impact

- **Areas Affected**: [List]
- **User Impact**: [Description]
- **Duration**: [Time period if known]

## Resolution

### Immediate Fix

[What needs to be done right now]

### Long-term Prevention

[How to prevent this in the future]

## Evidence

[Key logs, error messages, or code snippets from subagent findings]

## Lessons Learned

[What we learned from this incident]
```

## Error Handling Analysis Reference

**Good errors (helpful for debugging):**
- Stack traces with full context
- Specific error messages saying what failed
- Service initialization failures that stop the system
- Validation errors that show what was invalid

**Bad patterns (cause problems):**
- Silent failures returning None/null
- Generic "Something went wrong" messages
- Catch-all exception handlers hiding the real issue
- Services continuing with broken dependencies

## Related Commands

- `/code-review` - Review code changes
- `/deep-prime` - Get context on affected area
- `/quick-prime` - Quick project overview
