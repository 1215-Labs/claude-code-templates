---
name: lsp-type-safety-check
description: Verify type safety of code changes using LSP hover and find-references.
version: 1.1.0
category: lsp
user-invocable: true
hooks:
  - event: PostToolUse
    matcher: Edit
    script: .claude/hooks/lsp-type-validator.py
related:
  agents: [type-checker, code-reviewer]
  commands: [/code-review]
  skills: [lsp-symbol-navigation]
  workflows: [code-quality]
---

# LSP Type Safety Check Skill

## When to Use

When you need to verify type safety of code changes, especially before merge or deploy.

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
