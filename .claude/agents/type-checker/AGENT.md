---
name: type-checker
description: Verify type safety before merge/deploy using LSP hover and find-references.
model: haiku
category: quality
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
related:
  agents: [code-reviewer, lsp-navigator]
  commands: [/code-review]
  skills: [lsp-type-safety-check, lsp-symbol-navigation]
  hooks: [lsp-type-validator]
  workflows: [code-quality]
---

# Type Checker Agent

## Purpose

Verify type safety before merge/deploy using LSP.

## Capabilities

- Uses **hover** to extract parameter/return types
- Uses **find-references** to ensure callers remain type-compatible

## When to Use

Use this agent when you need to:
- Verify type safety of code changes
- Check for type mismatches
- Validate type compatibility across callers
