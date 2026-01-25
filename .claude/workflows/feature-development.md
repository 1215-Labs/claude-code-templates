---
name: feature-development
description: End-to-end feature development workflow
trigger: New feature request
---

# Feature Development Workflow

Complete workflow for implementing new features from understanding to deployment.

## Workflow Sequence

```
1. /onboarding or /quick-prime     → Understand project
         ↓
2. /deep-prime "area" "focus"      → Deep dive into relevant area
         ↓
3. codebase-analyst agent          → Find patterns and conventions
         ↓
4. [Developer writes code]         → Implementation
         ↓
5. code-reviewer agent             → Review changes
         ↓
6. test-automator agent            → Create/update tests
         ↓
7. /code-review                    → Final review before merge
```

## Step Details

### Step 1: Project Understanding
**Command**: `/onboarding` (first time) or `/quick-prime` (returning)
- Get project overview
- Understand tech stack
- Learn conventions

### Step 2: Deep Context
**Command**: `/deep-prime "area" "focus"`
- Example: `/deep-prime "authentication" "JWT handling"`
- Understand specific area in depth
- Find related code

### Step 3: Pattern Discovery
**Agent**: `codebase-analyst`
- Find similar implementations
- Extract naming conventions
- Document integration patterns

### Step 4: Implementation
- Write code following discovered patterns
- Use existing conventions
- Stay consistent with codebase

### Step 5: Code Review
**Agent**: `code-reviewer`
- Security check
- Quality assessment
- Best practices validation

### Step 6: Testing
**Agent**: `test-automator`
- Unit tests for new code
- Integration tests if needed
- Update existing tests

### Step 7: Final Review
**Command**: `/code-review`
- Complete code review with report
- Verify all issues addressed
- Ready for merge

## Decision Points

| Situation | Action |
|-----------|--------|
| Tests fail | → `debugger` agent |
| Patterns unclear | → `codebase-analyst` agent |
| Dependencies complex | → `dependency-analyzer` agent |
| Type issues | → `type-checker` agent |

## Related Components

- **Agents**: codebase-analyst, code-reviewer, test-automator, debugger
- **Commands**: /onboarding, /quick-prime, /deep-prime, /code-review
- **Skills**: lsp-symbol-navigation, lsp-dependency-analysis
