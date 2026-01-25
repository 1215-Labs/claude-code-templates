---
name: code-review
description: Perform comprehensive code review using parallel subagents and save report to `code-review.md`
argument-hint: <PR number, branch name, file path, or leave empty for staged changes>
user-invocable: true
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Write
  - Task
---

# Code Review

**Review scope**: $ARGUMENTS

I'll perform a comprehensive code review using parallel subagents to preserve context, then synthesize findings into a report saved to `code-review[n].md`.

## Step 1: Determine Review Scope

First, determine what needs reviewing:
- If no arguments: Review staged changes (`git diff --staged`)
- If PR number: Review pull request (`gh pr view`)
- If branch name: Compare with main (`git diff main...branch`)
- If file path: Review specific files
- If directory: Review all changes in that area

## Phase 1: Parallel Analysis (Use Subagents)

**IMPORTANT**: Launch these as PARALLEL subagents (single message, multiple Task tool calls) to preserve main agent context for synthesis.

### Subagent 1: Changes Analyzer
Use the **Explore subagent** with "medium" thoroughness to:
- Identify all modified files and their scope
- Summarize what problem is being solved
- Map which areas of the codebase are affected
- Check if changes touch critical paths (auth, payments, data)

Return: Change summary, affected areas, risk assessment.

### Subagent 2: Pattern Checker
Use the **Explore subagent** with "thorough" thoroughness to:
- Read CLAUDE.md for project conventions and anti-patterns
- Compare changes against documented patterns
- Check consistency with existing codebase style
- Identify deviations from established patterns

**Check for tech-stack specific issues:**
- **TypeScript/JavaScript**: Proper types (no `any`), hooks usage, error handling
- **Python**: Type hints, exception handling, no print statements
- **Rust**: Result/Option handling, minimal unwrap() calls
- **Go**: Proper error checking, idiomatic patterns

Return: Pattern violations, convention issues, style inconsistencies.

### Subagent 3: Security Scanner
Use the **Explore subagent** with "thorough" thoroughness to check for OWASP vulnerabilities:
- SQL injection vulnerabilities
- XSS attack vectors
- Input validation gaps
- Hardcoded secrets or API keys
- Authentication/authorization issues
- CORS misconfigurations
- Command injection risks

Return: Security issues found with severity ratings and file:line references.

### Subagent 4: Test Coverage Analyzer
Use the **Explore subagent** with "medium" thoroughness to:
- Verify tests exist for new functionality
- Check if error paths are tested
- Identify untested edge cases
- Look for catch-all exception handlers hiding issues
- Verify test assertions are meaningful

Return: Coverage gaps, missing tests, testing quality issues.

Wait for all subagents to complete before proceeding.

## Phase 2: Synthesize Findings

Consolidate subagent findings into:
1. **Change Summary**: What changed and why
2. **Quality Issues**: Pattern and convention violations
3. **Security Concerns**: Vulnerabilities requiring attention
4. **Test Gaps**: Missing or inadequate test coverage
5. **Priority Rankings**: Critical > Important > Suggestions

## Phase 3: Architecture & Performance Check (Main Agent)

With main context preserved, perform final analysis:

### Architecture Review
- Do changes follow project structure from CLAUDE.md?
- Are dependencies appropriate?
- Is there unnecessary coupling?

### Performance Considerations
- Any N+1 queries or inefficient algorithms?
- Unnecessary re-renders (React)?
- Memory leaks or resource management issues?

### Error Handling Philosophy

**Where errors should fail fast:**
- Service initialization failures
- Configuration errors
- Database connection failures
- Authentication failures
- Data validation errors

**Where to complete but log clearly:**
- Background tasks
- Batch operations
- Optional features
- External API calls (retry, then fail with clear message)

## Phase 4: Generate Report

Check if other reviews exist and increment filename as needed. Generate `code-review.md` with:

```markdown
# Code Review

**Date**: [Today's date]
**Project**: [Project name from CLAUDE.md]
**Scope**: [What was reviewed]
**Overall Assessment**: [Pass/Needs Work/Critical Issues]

## Summary

[Brief overview of changes and general quality]

## Issues Found

### Critical (Must Fix)

- [Issue description with file:line reference and suggested fix]

### Important (Should Fix)

- [Issue description with file:line reference]

### Suggestions (Consider)

- [Minor improvements or style issues]

## What Works Well

- [Positive aspects of the code]

## Security Review

[Any security concerns or confirmations - from Subagent 3]

## Performance Considerations

[Any performance impacts]

## Test Coverage

- Current coverage: [if available]
- Missing tests for: [list areas - from Subagent 4]

## Pattern Compliance

[How well changes follow project conventions - from Subagent 2]

## Recommendations

[Specific actionable next steps]
```

## Helpful Commands

Based on detected tech stack, suggest relevant commands:

**Git commands:**
```bash
git diff --staged
git diff main...HEAD
gh pr view $PR_NUMBER --json files
```

**Quality checks (adapt based on project):**
- TypeScript: `npm run lint`, `npm run typecheck`
- Python: `ruff check`, `mypy src/`
- Rust: `cargo clippy`
- Go: `go vet ./...`

## Related Commands

- `/deep-prime` - Get deep context for a specific area before making changes
- `/rca` - Investigate issues found during review
- `/coderabbit-helper` - Analyze specific CodeRabbit suggestions

Remember: Focus on impact and maintainability. Good code review helps ship better code, not just find problems. Be constructive and specific with feedback.
