---
name: coderabbit-helper
description: Analyze CodeRabbit suggestions, assess validity, and provide actionable options with tradeoffs
argument-hint: Paste the CodeRabbit suggestion here
user-invocable: true
allowed-tools:
  - Read
  - Grep
  - Glob
---

# CodeRabbit Review Analysis

**Review:** $ARGUMENTS

## Step 1: Discover Project Context

Read CLAUDE.md to understand:
- Project phase (alpha, beta, production)
- Conventions and patterns
- Current priorities
- Anti-patterns to avoid

This context helps assess whether the suggestion aligns with project goals.

## Step 2: Deep Analysis

- Understand the technical issue being raised
- Check if it's a real problem or false positive
- Search the codebase for related patterns and context
- Consider project phase and architecture from CLAUDE.md

## Step 3: Context Assessment

Based on project phase from CLAUDE.md:

**If early/beta phase:**
- Prioritize simplicity over perfection
- Follow KISS principles and existing codebase patterns
- Avoid premature optimization or over-engineering
- Consider if this affects user experience or is internal only

**If production phase:**
- Higher bar for code quality
- Consider long-term maintainability
- Performance and security more critical

## Step 4: Generate Options

Think harder about the problem and potential solutions.
Provide 2-5 practical options with clear tradeoffs.

## Response Format

### Issue Summary

_[One sentence describing what CodeRabbit found]_

### Is this valid?

_[YES/NO with brief explanation]_

### Priority for this PR

_[HIGH/MEDIUM/LOW/SKIP with reasoning based on project phase]_

### Options & Tradeoffs

**Option 1: [Name]**
- What: _[Brief description]_
- Pros: _[Benefits]_
- Cons: _[Drawbacks]_
- Effort: _[Low/Medium/High]_

**Option 2: [Name]**
- What: _[Brief description]_
- Pros: _[Benefits]_
- Cons: _[Drawbacks]_
- Effort: _[Low/Medium/High]_

### Recommendation

_[Your recommended option with 1-2 sentence justification, considering project phase and conventions from CLAUDE.md]_

## User Feedback

- When you have presented the review to the user, ask for their feedback on the suggested changes
- Ask the user if they wish to discuss any of the options further
- If the user wishes for you to explore further, provide additional options or tradeoffs
- If the user is ready to implement the recommended option right away, proceed with implementation

## Related Commands

- `/code-review` - Full code review for a PR or changes
- `/rca` - Investigate root cause of issues
- `/deep-prime` - Get context on a specific area
