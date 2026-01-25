---
name: code-review
description: Perform comprehensive code review and save report to `code-review.md`
argument-hint: <PR number, branch name, file path, or leave empty for staged changes>
user-invocable: true
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Write
---

# Code Review

**Review scope**: $ARGUMENTS

I'll perform a comprehensive code review and generate a report saved to the root of this directory as `code-review[n].md`. Check if other reviews exist before creating the file and increment n as needed.

## Step 1: Discover Project Context

Read CLAUDE.md to understand:
- Project name and purpose (use for report header)
- Tech stack and conventions
- Testing patterns and commands
- Anti-patterns to watch for

If CLAUDE.md doesn't exist, detect from:
- `package.json` + `tsconfig.json` (TypeScript/JavaScript)
- `pyproject.toml` or `setup.py` (Python)
- `Cargo.toml` (Rust)
- `go.mod` (Go)

Store the project name and tech stack for use in the review.

## Step 2: Determine Review Scope

Determine what needs reviewing:
- If no arguments: Review staged changes (`git diff --staged`)
- If PR number: Review pull request (`gh pr view`)
- If branch name: Compare with main (`git diff main...branch`)
- If file path: Review specific files
- If directory: Review all changes in that area

## Step 3: Review Focus

### Code Quality Checks (Dynamic by Tech Stack)

**For TypeScript/JavaScript projects:**
- TypeScript types properly defined, avoid `any`
- React patterns (if applicable): hooks, error boundaries, component structure
- API error handling that shows actual error messages
- Console.error for debugging, not hidden errors

**For Python projects:**
- Type hints on all functions
- Proper exception handling with context
- No print statements (use logging)
- Async/await used correctly

**For Rust projects:**
- Proper Result/Option handling
- Avoid excessive unwrap() calls
- Appropriate error types and propagation

**For Go projects:**
- Proper error checking (no ignored errors)
- Idiomatic Go patterns
- Appropriate defer usage

### Error Handling Philosophy (for beta/alpha projects)

If CLAUDE.md indicates this is beta/alpha software, apply these principles:

**Where errors should fail fast:**
- Service initialization failures
- Configuration errors
- Database connection failures
- Authentication failures
- Data validation errors

**Where to complete but log clearly:**
- Background tasks (process what you can, report failures)
- Batch operations
- Optional features
- External API calls (retry, then fail with clear message)

### Security Considerations

Check for:
- Input validation
- SQL injection vulnerabilities
- No hardcoded secrets or API keys
- Authentication issues
- CORS configuration

### Architecture & Patterns

Ensure code follows patterns from CLAUDE.md:
- Check "## Conventions" section for required patterns
- Check "## Anti-Patterns" section for things to avoid
- Verify consistency with existing codebase patterns

### Testing

Verify:
- Tests exist for new functionality
- Error paths are tested
- No catch-all exception handlers hiding issues

## Review Process

1. **Understand the changes** - What problem is being solved?
2. **Check functionality** - Does it do what it's supposed to?
3. **Review code quality** - Is it maintainable and follows standards?
4. **Consider performance** - Any N+1 queries or inefficient algorithms?
5. **Verify tests** - Are changes properly tested?
6. **Check documentation** - Are complex parts documented?

## Report Format

Generate a `code-review.md` with:

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

[Any security concerns or confirmations]

## Performance Considerations

[Any performance impacts]

## Test Coverage

- Current coverage: [if available]
- Missing tests for: [list areas]

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

**Run tests (adapt based on project):**
- Check CLAUDE.md "## Testing" section for project-specific commands

## Related Commands

- `/deep-prime` - Get deep context for a specific area before making changes
- `/rca` - Investigate issues found during review
- `/coderabbit-helper` - Analyze specific CodeRabbit suggestions

Remember: Focus on impact and maintainability. Good code review helps ship better code, not just find problems. Be constructive and specific with feedback.
