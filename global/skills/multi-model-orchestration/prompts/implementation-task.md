# Implementation Task Template

Use this template when forking Codex for code implementation.

## Variables

- `{FEATURE}` - What to implement/change
- `{EXPLORATION_DOC}` - Path to Gemini exploration output (if available)
- `{REQUIREMENTS}` - Specific requirements list
- `{TEST_COMMAND}` - Command to validate implementation
- `{OUTPUT_FILE}` - Log location (default: `docs/implementation/{feature}-log.md`)

## Prompt Template (With Exploration Context)

```
Implement {FEATURE} based on the exploration in {EXPLORATION_DOC}.

## Context

Read {EXPLORATION_DOC} first for:
- Architecture understanding
- Critical files to modify
- Patterns to follow
- Edge cases to handle

## Requirements

- {REQUIREMENT_1}
- {REQUIREMENT_2}
- {REQUIREMENT_3}

## Constraints

- Follow existing code patterns (see exploration doc)
- Add tests for new functionality
- Don't break existing tests

## Validation

After implementation, run:
```
{TEST_COMMAND}
```

## Output

Document your changes in {OUTPUT_FILE}:

# {FEATURE} Implementation Log

## Summary
[What was implemented, key decisions made]

## Files Changed

| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file.ts` | Added/Modified/Deleted | Brief description |

## Key Decisions

[Any design decisions you made and why]

## Tests Added

| Test File | Coverage |
|-----------|----------|
| `path/to/test.ts` | What it tests |

## Validation Results

```
$ {TEST_COMMAND}
[paste output]
```

## Notes for Reviewer

[Anything the orchestrator should know - edge cases, concerns, follow-ups]
```

## Prompt Template (Without Exploration Context)

```
Implement {FEATURE} in this codebase.

## Requirements

- {REQUIREMENT_1}
- {REQUIREMENT_2}
- {REQUIREMENT_3}

## Before Implementing

1. Find relevant files using grep/glob
2. Understand existing patterns
3. Identify integration points

## Constraints

- Match existing code style
- Add tests for new functionality
- Don't break existing tests

## Validation

After implementation, run:
```
{TEST_COMMAND}
```

## Output

Document your changes in {OUTPUT_FILE}:
[... log format above ...]
```

## Example: Add User Profile Feature

```
Implement user profile management based on the exploration in docs/exploration/user-system.md.

## Context

Read docs/exploration/user-system.md first for:
- How users are stored and fetched
- Validation patterns used
- API route conventions

## Requirements

- Add GET /api/users/:id/profile endpoint
- Add PUT /api/users/:id/profile endpoint
- Profile includes: bio, avatar_url, social_links
- Only user can update their own profile

## Constraints

- Follow existing API patterns from exploration doc
- Use existing validation middleware
- Add unit tests for new endpoints

## Validation

After implementation, run:
```
npm test -- --grep "profile"
```

## Output

Document your changes in docs/implementation/user-profile-log.md
```

## Tips for Effective Implementation Tasks

1. **Reference exploration docs** - Codex benefits from pre-gathered context
2. **Be specific about requirements** - Ambiguity leads to wrong implementations
3. **Include validation commands** - Makes success measurable
4. **Request the implementation log** - Helps orchestrator review and follow up
