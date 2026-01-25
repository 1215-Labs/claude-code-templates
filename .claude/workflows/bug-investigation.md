---
name: bug-investigation
description: Systematic bug investigation workflow
trigger: Bug report or error
---

# Bug Investigation Workflow

Systematic approach to debugging and fixing issues.

## Workflow Sequence

```
1. /rca "error message"            → Initial investigation
         ↓
2. debugger agent                  → Deep root cause analysis
         ↓
3. lsp-dependency-analysis skill   → Trace affected code
         ↓
4. [Developer fixes bug]           → Implementation
         ↓
5. test-automator agent            → Add regression test
         ↓
6. /code-review                    → Review fix
```

## Step Details

### Step 1: Initial Investigation
**Command**: `/rca "error message or description"`
- Capture error details
- Identify likely locations
- Form initial hypotheses

### Step 2: Root Cause Analysis
**Agent**: `debugger`
- Deep investigation
- Trace execution path
- Identify actual cause

### Step 3: Impact Analysis
**Skill**: `lsp-dependency-analysis`
- Find all affected code
- Check for related issues
- Assess fix impact

### Step 4: Fix Implementation
- Address root cause (not symptoms)
- Maintain backward compatibility
- Document the fix

### Step 5: Regression Test
**Agent**: `test-automator`
- Create test that catches the bug
- Verify fix works
- Prevent regression

### Step 6: Review Fix
**Command**: `/code-review`
- Verify fix is complete
- Check for side effects
- Ready for merge

## Decision Points

| Situation | Action |
|-----------|--------|
| Error unclear | → Add debug logging |
| Many references | → `dependency-analyzer` agent first |
| Type mismatch | → `type-checker` agent |
| Pattern needed | → `codebase-analyst` agent |

## Related Components

- **Agents**: debugger, dependency-analyzer, test-automator
- **Commands**: /rca, /code-review
- **Skills**: lsp-dependency-analysis
- **Hooks**: lsp-reference-checker
