# LSP Type Safety Check

Verify type safety of code changes using LSP capabilities.

---

## Purpose

Provides patterns for validating type correctness before merge or deploy, using LSP hover and find-references to ensure type compatibility across callers.

## Activates On

- Type safety verification
- Pre-merge type check
- Type compatibility
- Parameter type validation
- Return type checking

## File Count

2 files, ~55 lines total

## Core Capabilities

### Type Extraction
Use hover to get parameter types, return types, and type signatures.

### Caller Verification
Find all callers and verify they remain type-compatible after changes.

### Interface Compliance
Check that implementations match their interface contracts.

## Use Cases

- Verifying function signature changes don't break callers
- Checking type compatibility before merging PRs
- Validating refactored code maintains type safety
- Pre-deploy type verification

## Related Components

- **Agents**: type-checker, code-reviewer
- **Skills**: lsp-symbol-navigation
- **Commands**: /code-review
- **Hooks**: lsp-type-validator
- **Workflows**: code-quality

## Files

- **SKILL.md** - Main skill content with verification steps
- **README.md** (this file) - Skill metadata

---

**Part of**: claude-code-templates
