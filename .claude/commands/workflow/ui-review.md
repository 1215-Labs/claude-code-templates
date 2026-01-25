---
name: ui-review
description: Analyze UI components for consistency, patterns, and styling
argument-hint: <component path or directory>
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Bash(*)
---

# UI Consistency Review

**Review scope**: $ARGUMENTS

## Step 1: Find UI Standards

### Check for Standards Documentation

Search for UI standards in common locations:
1. `UI_STANDARDS.md` in project root
2. `docs/UI_STANDARDS.md`
3. `STYLE_GUIDE.md`
4. CLAUDE.md sections about UI conventions

### If Standards File Exists

Read the standards file - this is the single source of truth for all rules, patterns, and scans.

### If No Standards File

Infer standards from existing components:
1. Identify the most mature/complete components
2. Extract patterns for:
   - Styling approach (CSS modules, Tailwind, styled-components)
   - Component structure
   - Accessibility patterns
   - State management

## Step 2: Find Files to Review

Glob all component files in the provided path:
- `**/*.tsx` for React TypeScript
- `**/*.jsx` for React JavaScript
- `**/*.vue` for Vue
- `**/*.svelte` for Svelte

## Step 3: Run Automated Scans

Based on the UI framework detected:

### For Tailwind CSS Projects

Check for:
- Dynamic class names that won't be detected by Tailwind
- Hardcoded colors instead of design tokens
- Missing responsive variants
- Missing dark mode variants

### For All React Projects

Check for:
- Accessibility: keyboard support, ARIA attributes, focus management
- TypeScript: proper prop types, no `any`
- Component patterns: consistent structure, proper hooks usage

### General Checks

- Native HTML elements that should use design system components
- Inconsistent spacing or sizing
- Missing error/loading states
- Unconstrained scroll containers

## Step 4: Deep Analysis

For each file, analyze:

### 1. Styling Consistency

- Are design tokens/variables used?
- Is spacing consistent with project standards?
- Are colors from the design system?

### 2. Component Patterns

- Does the component follow project conventions?
- Are props properly typed?
- Is state management consistent with other components?

### 3. Accessibility

- Keyboard navigation
- Screen reader support
- Focus indicators
- ARIA attributes where needed

### 4. TypeScript Quality

- Proper type definitions
- No `any` types
- Props interface defined

### 5. Functional Correctness

- Does the UI actually work?
- Are edge cases handled?
- Error and loading states present?

## Step 5: Generate Report

Save to `ui-review-[feature].md` with:

```markdown
# UI Consistency Review

**Date**: [Today's date]
**Scope**: [What was reviewed]
**Files Analyzed**: [Count]

## Summary

**Overall Score**: [A-F or percentage]
- Styling Consistency: [Score]
- Accessibility: [Score]
- TypeScript Quality: [Score]
- Pattern Adherence: [Score]

## Issues Found

### Critical Issues

[Issues that break functionality or accessibility]

### High Priority

[Significant inconsistencies or violations]

### Medium Priority

[Minor inconsistencies]

### Low Priority

[Style suggestions]

## Component Analysis

### [Component Name]

**File**: [path]
**Score**: [Score]

**Issues**:
- [Issue with file:line reference]

**Good Patterns**:
- [What's done well]

## Recommendations

### Immediate Actions

[What should be fixed now]

### Future Improvements

[What to address later]

## Standards Reference

[Reference to UI_STANDARDS.md sections or inferred patterns]
```

## Step 6: Optional - Create Fix Plan

If significant violations found, suggest using a planning command to create a fix plan:
- Reference the review report
- Specify which standards were violated
- Include validation commands to verify fixes

## Related Commands

- `/code-review` - General code review
- `/deep-prime "frontend"` - Get context on frontend architecture
- `/onboarding` - Full onboarding for the project

---

**Note**: If no UI_STANDARDS.md exists and the project would benefit from one, suggest creating it based on patterns found in the most mature components.
