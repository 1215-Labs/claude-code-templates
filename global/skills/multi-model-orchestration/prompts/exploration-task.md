# Exploration Task Template

Use this template when forking Gemini for codebase exploration.

## Variables

- `{TOPIC}` - The area/system to explore (e.g., "authentication", "API routing")
- `{QUESTION_1}` through `{QUESTION_N}` - Specific questions to answer
- `{OUTPUT_FILE}` - Output location (default: `docs/exploration/{topic}.md`)

## Prompt Template

```
Explore the {TOPIC} in this codebase.

## Focus Areas

Answer these questions:
- {QUESTION_1}
- {QUESTION_2}
- {QUESTION_3}

## Output Requirements

Write your findings to {OUTPUT_FILE} using this exact format:

# {TOPIC} Exploration

## Executive Summary
[2-3 sentence overview - what did you find? What's the key insight?]

## Table of Contents
- [Quick Reference](#quick-reference)
- [Architecture Overview](#architecture-overview)
- [Critical Files](#critical-files)
- [Patterns & Conventions](#patterns--conventions)
- [Integration Points](#integration-points)
- [Edge Cases & Gotchas](#edge-cases--gotchas)
- [Recommendations](#recommendations)
- [Raw Findings](#raw-findings)

## Quick Reference

| Aspect | Details |
|--------|---------|
| Main entry point | `path/to/file.ts` |
| Key dependencies | list here |
| Config location | `path/to/config` |
| Test location | `path/to/tests` |

## Architecture Overview

[High-level structure. Include ASCII diagrams if helpful.]

## Critical Files

| File | Purpose | Key Lines |
|------|---------|-----------|
| `path/to/file.ts` | What it does | 45-67 |

Include ALL relevant files. Better to include too many than miss important ones.

## Patterns & Conventions

[Code patterns you observed. Naming conventions. Architectural decisions.]

## Integration Points

[How this system connects to others. APIs, events, shared state.]

## Edge Cases & Gotchas

[Non-obvious behaviors. Things that might trip up an implementer.]

## Recommendations

[Specific guidance for whoever implements changes to this system.]

## Raw Findings

[Everything else. Code snippets. Detailed notes. Full context dump.]
```

## Example: Auth System Exploration

```
Explore the authentication system in this codebase.

## Focus Areas

Answer these questions:
- How do users authenticate (JWT, sessions, OAuth)?
- Where are auth tokens validated?
- How are protected routes identified?
- What happens on auth failure?

## Output Requirements

Write your findings to docs/exploration/auth-system.md using this exact format:
[... format template above ...]
```

## Tips for Effective Exploration

1. **Be specific in questions** - "How does X work?" is better than "Tell me about X"
2. **Request critical files with line numbers** - Helps orchestrator reference specific code
3. **Ask about edge cases** - Implementation often fails on edge cases
4. **Request recommendations** - Gemini's insights guide implementation
