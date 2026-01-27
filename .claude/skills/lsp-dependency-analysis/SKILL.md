---
name: lsp-dependency-analysis
description: Map incoming and outgoing dependencies for modules using LSP.
version: 1.2.0
category: lsp
user-invocable: true
hooks:
  - event: PreToolUse
    matcher: Edit
    script: .claude/hooks/lsp-reference-checker.py
related:
  agents: [dependency-analyzer, codebase-analyst, lsp-navigator]
  commands: [/deep-prime, /rca]
  skills: [lsp-symbol-navigation]
  workflows: [feature-development, bug-investigation, code-quality]
---

# LSP Dependency Analysis Skill

## When to Use

Use this skill when you need to understand module relationships:

- **Before removing a module** - see what would break
- **Planning refactors** - understand the blast radius
- **Finding circular dependencies** - identify import cycles
- **Dead code detection** - find modules with no dependents
- **Architecture analysis** - understand coupling between parts

### Decision Guide

| Goal | Action |
|------|--------|
| See who uses this module | Map incoming dependencies |
| See what this module needs | Map outgoing dependencies |
| Find import cycles | Check for circular patterns |
| Assess change impact | Count incoming dependencies |

## When NOT to Use

- **Tracing code execution** - use `lsp-symbol-navigation` skill
- **Finding coding patterns** - use `codebase-analyst` agent
- **Build-time dependency graphs** - use compiler/bundler tools (webpack, tsc)
- **Package dependency analysis** - use npm/pip tools for external deps
- **Real-time monitoring** - dependencies don't change during editing

## Prerequisites

- LSP server support for the language
- Reasonable codebase size (may be slow on 5000+ file monorepos)
- Works best with: TypeScript, Python, Go, Rust, Java

## Steps

1. Use **find-references** to identify all places that import or call from the module
2. Use **go-to-definition** to follow dependency chains
3. Map both incoming (who uses this) and outgoing (what this uses) dependencies

## Output Format

```
Module: src/services/userService.ts

INCOMING DEPENDENCIES (12 files depend on this):
├── src/api/routes/users.ts
│   └── imports: getUserById, createUser
├── src/api/routes/auth.ts
│   └── imports: validateUser
├── src/workers/cleanup.ts
│   └── imports: deleteInactiveUsers
└── ... (9 more)

OUTGOING DEPENDENCIES (5 files this depends on):
├── src/models/User.ts
├── src/database/connection.ts
├── src/utils/validation.ts
├── src/config/settings.ts
└── src/types/index.ts

CIRCULAR DEPENDENCIES: None detected

COUPLING ASSESSMENT:
- High coupling (12+ dependents) - changes require careful review
- Recommendation: Consider interface extraction before major changes
```

## Example: Pre-Removal Analysis

```
# Scenario: Want to remove src/utils/legacyHelper.ts

1. find-references on all exports from legacyHelper.ts
2. Results:
   - formatDate() → used in 3 files
   - parseConfig() → used in 0 files (dead code)
   - sanitizeInput() → used in 15 files

3. Conclusion:
   - parseConfig can be safely removed
   - formatDate needs migration to new util
   - sanitizeInput is heavily used - keep or migrate carefully
```
