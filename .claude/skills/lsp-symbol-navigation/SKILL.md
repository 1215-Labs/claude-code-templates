---
name: lsp-symbol-navigation
description: Navigate symbols using LSP go-to-definition, hover, and find-references.
version: 1.2.0
category: lsp
user-invocable: true
related:
  agents: [lsp-navigator, codebase-analyst, dependency-analyzer]
  commands: [/deep-prime]
  skills: [lsp-dependency-analysis, lsp-type-safety-check]
  workflows: [bug-investigation, feature-development]
---

# LSP Symbol Navigation Skill

## When to Use

Use this skill when you need to understand a symbol's definition, type, and all usages:

- **Exploring unfamiliar code** - find where functions/classes are defined
- **Understanding call sites** - see everywhere a symbol is used
- **Checking type signatures** - hover to see parameter and return types
- **Tracing execution flow** - follow from call site to implementation

### Decision Guide

| Need | LSP Operation |
|------|---------------|
| Find where something is defined | go-to-definition |
| See type signature and docs | hover |
| Find all usages of a symbol | find-references |
| Follow import chains | go-to-definition on imports |

## When NOT to Use

- **Searching for text patterns** - use Grep tool for string searches
- **Finding patterns across codebase** - use `codebase-analyst` agent
- **Large-scale dependency mapping** - use `lsp-dependency-analysis` skill
- **Runtime behavior analysis** - use `debugger` agent
- **Languages without LSP support** - won't work without language server

## Prerequisites

- Language server must be running (TypeScript, Python, Go, Rust, etc.)
- File must be open/accessible for LSP to analyze

## Steps

1. Use **go-to-definition** to find the symbol's definition
2. Use **hover** to get type information and documentation
3. Use **find-references** to see all usages of the symbol

## Examples

### Finding a function definition
```
# Scenario: You see processOrder() called but don't know where it's defined
1. go-to-definition on "processOrder" → jumps to src/orders/processor.ts:42
2. hover on "processOrder" → shows (order: Order) => Promise<Result>
3. find-references → shows 15 call sites across 8 files
```

### Understanding a type
```
# Scenario: You see UserProfile used but don't know its shape
1. go-to-definition on "UserProfile" → jumps to src/types/user.ts:12
2. hover → shows interface with all properties
```

### Tracing an import
```
# Scenario: You want to see what a module exports
1. go-to-definition on the import path → opens the source file
2. find-references on each export → shows where each is used
```
