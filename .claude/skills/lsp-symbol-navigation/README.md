# LSP Symbol Navigation

Navigate and understand code using Language Server Protocol capabilities.

---

## Purpose

Provides patterns for using LSP features (go-to-definition, find-references, hover) to explore and understand codebases efficiently.

## Activates On

- Navigate to definition
- Find usages/references
- Understand symbol types
- Explore unfamiliar code
- Type information lookup

## File Count

2 files, ~50 lines total

## Core Capabilities

### Go-to-Definition
Jump directly to where a symbol (function, class, variable) is defined.

### Find-References
Discover all locations where a symbol is used across the codebase.

### Hover
Get type signatures, documentation, and parameter information for any symbol.

## Use Cases

- Understanding how a function works by finding its definition
- Assessing impact of changes by finding all call sites
- Discovering type information without reading source files
- Navigating between related code locations

## Related Components

- **Agents**: lsp-navigator, codebase-analyst
- **Skills**: lsp-dependency-analysis, lsp-type-safety-check
- **Commands**: /deep-prime

## Files

- **SKILL.md** - Main skill content with steps and examples
- **README.md** (this file) - Skill metadata

---

**Part of**: claude-code-templates
