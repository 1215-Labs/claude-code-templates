---
name: lsp-type-safety-check
description: Verify type safety of code changes using LSP hover and find-references.
version: 1.2.0
category: lsp
user-invocable: true
hooks:
  - event: PostToolUse
    matcher: Edit
    script: .claude/hooks/lsp-type-validator.py
related:
  agents: [type-checker, code-reviewer]
  commands: [/code-review]
  skills: [lsp-symbol-navigation, lsp-dependency-analysis]
  workflows: [code-quality, feature-development]
---

# LSP Type Safety Check Skill

## When to Use

Use this skill when you need to verify type safety of code changes:

- **After changing function signatures** - verify callers are still compatible
- **Before merging PRs** - catch type mismatches before they hit main
- **After refactoring interfaces** - ensure all implementations match
- **When adding null/undefined returns** - find callers that don't handle it

### Decision Guide

```
Changed function signature?
├── YES → Use this skill to verify callers
│   └── Parameter types changed? → Check all call sites
│   └── Return type changed? → Check all consumers
└── NO → Probably don't need this skill
```

## When NOT to Use

- **Code style/quality review** - use `code-reviewer` agent
- **Runtime error debugging** - use `debugger` agent (types are compile-time)
- **Dynamic languages (JS, Python)** - no types to check
- **Finding ALL type errors** - use IDE/compiler for complete analysis
- **Performance analysis** - types don't affect runtime performance

## Prerequisites

- Language must have a type system (TypeScript, Go, Rust, Java, C#, etc.)
- LSP server must be available
- **Won't help with**: vanilla JavaScript, Python without type hints

## Steps

1. Use **hover** on modified functions to extract parameter and return types
2. Use **find-references** to identify all callers
3. Use **hover** on call sites to verify type compatibility
4. Report any parameter/return type mismatches or unsafe call sites

## Checklist

- [ ] All function signatures have explicit types
- [ ] All callers pass correct types
- [ ] Return types match declarations
- [ ] No implicit `any` types
- [ ] Generic constraints are satisfied

## Example

```
# Scenario: Changed getUser() to return User | null instead of User

1. hover on getUser → confirms new signature: (id: string) => User | null
2. find-references → 12 call sites found
3. Check each call site:
   - src/profile.ts:34 → const user = getUser(id); user.name ❌
     Problem: Accessing .name without null check
   - src/admin.ts:89 → if (getUser(id)) {...} ✓
     OK: Already handles null case
4. Report: 3 callers need null handling updates
```
