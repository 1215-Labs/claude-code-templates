---
name: ui-review
description: Analyze UI components for consistency, patterns, and styling using parallel subagents
argument-hint: <component path or directory>
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Bash(*)
  - Task
---

# UI Consistency Review

**Review scope**: $ARGUMENTS

I'll perform a comprehensive UI review using parallel subagents to preserve context, then synthesize findings into an actionable improvement report.

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

Note this for later recommendation. Standards will be inferred from existing components.

## Step 2: Identify Files to Review

Glob all component files in the provided path:
- `**/*.tsx` for React TypeScript
- `**/*.jsx` for React JavaScript
- `**/*.vue` for Vue
- `**/*.svelte` for Svelte

## Phase 1: Parallel Analysis (Use Subagents)

**IMPORTANT**: Launch these as PARALLEL subagents (single message, multiple Task tool calls) to preserve main agent context for synthesis.

### Subagent 1: Component Structure Analyzer
Use the **Explore subagent** with "thorough" thoroughness to:
- Review component hierarchy and organization
- Check for proper component composition patterns
- Identify prop drilling vs context usage
- Verify separation of concerns (logic vs presentation)
- Look for component reusability opportunities
- Check for consistent naming conventions

Return: Component structure issues, hierarchy concerns, reusability opportunities.

### Subagent 2: Accessibility Checker
Use the **Explore subagent** with "thorough" thoroughness to check WCAG compliance:
- Keyboard navigation support (tab order, focus management)
- ARIA attributes usage and correctness
- Screen reader support (alt text, labels)
- Focus indicators (visible focus states)
- Color contrast considerations (if design tokens used)
- Semantic HTML usage (heading hierarchy, landmarks)
- Form accessibility (labels, error announcements)

Return: Accessibility violations with severity, file:line references, remediation guidance.

### Subagent 3: Performance Analyzer
Use the **Explore subagent** with "medium" thoroughness to:
- Identify unnecessary re-renders
- Check for missing memoization opportunities (React.memo, useMemo, useCallback)
- Look for expensive computations in render paths
- Identify large bundle imports that could be code-split
- Check for proper lazy loading of heavy components
- Look for list virtualization needs
- Identify image optimization opportunities

Return: Performance concerns with impact assessment, optimization recommendations.

### Subagent 4: Styling Consistency Checker
Use the **Explore subagent** with "thorough" thoroughness to:
- Identify styling approach (CSS modules, Tailwind, styled-components)
- Check for design token usage vs hardcoded values
- Verify spacing consistency (margins, padding)
- Check color usage against design system
- Look for responsive design patterns
- Identify dark mode support (if applicable)
- Check for style duplication that should be abstracted

**For Tailwind CSS Projects specifically:**
- Dynamic class names that won't be detected
- Missing responsive variants
- Missing dark mode variants

Return: Styling inconsistencies, design system violations, abstraction opportunities.

### Subagent 5: UX Pattern Analyzer
Use the **Explore subagent** with "medium" thoroughness to:
- Review navigation patterns and consistency
- Check interaction feedback (loading states, hover states)
- Verify error state handling and messaging
- Look for empty state implementations
- Check loading state patterns
- Identify missing edge case handling
- Verify form validation UX
- Check for consistent action patterns (buttons, links)

Return: UX gaps, missing states, interaction inconsistencies.

Wait for all subagents to complete before proceeding.

## Phase 2: Synthesize Findings

Consolidate subagent findings into:
1. **Structure Issues**: Component hierarchy and organization problems
2. **Accessibility Violations**: WCAG compliance issues by severity
3. **Performance Concerns**: Optimization opportunities
4. **Styling Issues**: Design system deviations
5. **UX Gaps**: Missing states and interaction problems

## Phase 3: Cross-Cutting Analysis (Main Agent)

With main context preserved, identify:

### Patterns to Extract
- Common patterns that should become shared components
- Repeated styling that should become design tokens
- Duplicate logic that should be custom hooks

### TypeScript Quality
- Proper type definitions for props
- No `any` types in UI code
- Props interfaces defined and exported

### Framework-Specific Issues
Based on detected framework (React/Vue/Svelte), check for framework-specific best practices and anti-patterns.

## Phase 4: Generate Report

Save to `ui-review-[feature].md` with:

```markdown
# UI Consistency Review

**Date**: [Today's date]
**Scope**: [What was reviewed]
**Files Analyzed**: [Count]
**Standards Reference**: [UI_STANDARDS.md or "Inferred from codebase"]

## Summary

**Overall Score**: [A-F or percentage]
- Component Structure: [Score]
- Accessibility: [Score]
- Performance: [Score]
- Styling Consistency: [Score]
- UX Patterns: [Score]

## Issues Found

### Critical Issues

[Issues that break functionality or accessibility - primarily from Subagent 2]

### High Priority

[Significant inconsistencies or violations - from all subagents]

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

## Accessibility Report

[Detailed findings from Subagent 2 - grouped by WCAG criterion]

## Performance Recommendations

[Findings from Subagent 3 - prioritized by impact]

## Styling Audit

[Findings from Subagent 4 - categorized by type]

## UX Improvements

[Findings from Subagent 5 - prioritized by user impact]

## Recommendations

### Immediate Actions

[What should be fixed now - critical and high priority items]

### Future Improvements

[What to address later - medium and low priority items]

### Suggested Abstractions

[Components or patterns that should be extracted]

## Standards Reference

[Reference to UI_STANDARDS.md sections or inferred patterns]
```

## Step 5: Optional - Create Fix Plan

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
