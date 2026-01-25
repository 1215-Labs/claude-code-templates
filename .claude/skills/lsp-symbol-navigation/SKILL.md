---
name: lsp-symbol-navigation
description: Navigate symbols using LSP go-to-definition, hover, and find-references.
version: 1.1.0
category: lsp
user-invocable: true
related:
  agents: [lsp-navigator, codebase-analyst]
  commands: [/deep-prime]
  skills: [lsp-dependency-analysis, lsp-type-safety-check]
---

# LSP Symbol Navigation Skill

## When to Use

When you need to understand a symbol's definition, type, and all usages.

## Steps

1. Use **go-to-definition** to find the symbol's definition
2. Use **hover** to get type information and documentation
3. Use **find-references** to see all usages of the symbol

## Example

```
# Finding where a function is defined and used:
1. go-to-definition on "processOrder" → jumps to src/orders/processor.ts:42
2. hover on "processOrder" → shows (order: Order) => Promise<Result>
3. find-references → shows 15 call sites across 8 files
```
