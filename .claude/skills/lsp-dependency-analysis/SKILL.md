---
name: lsp-dependency-analysis
description: Map incoming and outgoing dependencies for modules using LSP.
version: 1.1.0
category: lsp
user-invocable: true
hooks:
  - event: PreToolUse
    matcher: Edit
    script: .claude/hooks/lsp-reference-checker.py
related:
  agents: [dependency-analyzer, codebase-analyst]
  skills: [lsp-symbol-navigation]
---

# LSP Dependency Analysis Skill

## When to Use

When you need to map incoming and outgoing dependencies for a module or file.

## Steps

1. Use **find-references** to identify all places that import or call from the module
2. Use **go-to-definition** to follow dependency chains
3. Map both incoming (who uses this) and outgoing (what this uses) dependencies

## Output Format

```
Module: src/services/userService.ts

Incoming (12 files depend on this):
- src/api/routes/users.ts (imports: getUserById, createUser)
- src/api/routes/auth.ts (imports: validateUser)
...

Outgoing (5 dependencies):
- src/models/User.ts
- src/database/connection.ts
...
```
