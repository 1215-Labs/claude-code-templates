# LSP Dependency Analysis

Map module dependencies and coupling using LSP capabilities.

---

## Purpose

Provides patterns for analyzing code dependencies, import relationships, and module coupling to understand code architecture and assess change impact.

## Activates On

- Map dependencies
- Analyze imports
- Understand module coupling
- Impact analysis
- Dependency graph

## File Count

2 files, ~60 lines total

## Core Capabilities

### Import Mapping
Trace what a module imports and where those imports come from.

### Reference Tracking
Find all modules that depend on a given symbol or module.

### Coupling Analysis
Assess how tightly coupled modules are based on their dependencies.

## Use Cases

- Understanding module relationships before refactoring
- Assessing blast radius of changes
- Finding circular dependencies
- Planning migration or extraction of code

## Related Components

- **Agents**: dependency-analyzer, codebase-analyst
- **Skills**: lsp-symbol-navigation
- **Hooks**: lsp-reference-checker

## Files

- **SKILL.md** - Main skill content with methodology
- **README.md** (this file) - Skill metadata

---

**Part of**: claude-code-templates
