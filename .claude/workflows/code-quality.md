---
name: code-quality
description: Code quality assurance workflow
trigger: Before merge/deploy
---

# Code Quality Workflow

Pre-merge/deploy validation to ensure code quality.

## Workflow Sequence

```
1. /code-review                    → General code review
         ↓
2. type-checker agent              → Verify type safety
         ↓
3. test-automator agent            → Verify test coverage
         ↓
4. lsp-reference-checker hook      → Check all references
         ↓
5. lsp-type-validator hook         → Validate types
```

## Step Details

### Step 1: Code Review
**Command**: `/code-review`
- Security check
- Best practices
- Code organization
- Documentation

### Step 2: Type Safety
**Agent**: `type-checker`
- Verify all types
- Check function signatures
- Validate caller compatibility

### Step 3: Test Coverage
**Agent**: `test-automator`
- Check existing coverage
- Add missing tests
- Verify critical paths tested

### Step 4: Reference Check
**Hook**: `lsp-reference-checker`
- Warns about heavily-used symbols
- Suggests impact analysis
- Runs automatically on commit

### Step 5: Type Validation
**Hook**: `lsp-type-validator`
- Runs tsc --noEmit
- Catches type errors
- Runs automatically on commit

## Automated vs Manual

| Step | Automated | Manual |
|------|-----------|--------|
| Code review | Checks | Full review |
| Type checking | Hook | Agent for complex |
| Test coverage | CI/CD | Agent for new tests |

## Quality Checklist

- [ ] Code review passed
- [ ] Types verified
- [ ] Tests passing
- [ ] Coverage adequate
- [ ] No critical warnings
- [ ] Documentation updated

## Related Components

- **Agents**: code-reviewer, type-checker, test-automator
- **Commands**: /code-review, /ui-review
- **Skills**: lsp-type-safety-check
- **Hooks**: lsp-reference-checker, lsp-type-validator
