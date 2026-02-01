---
name: multi-model-orchestration
description: |
  Orchestrate tasks across specialized models via forked terminals.
  Gemini (1M context) for exploration, Codex (SWE-bench leader) for implementation, Opus for synthesis.

  Use when:
  - Large codebase exploration needed before implementation
  - Complex features requiring explore-then-implement workflow
  - Parallel investigations across different codebase areas
  - Preserving Opus context for strategic decisions
version: 1.0.0
category: orchestration
user-invocable: false
related:
  skills: [fork-terminal]
  commands: [/orchestrate]
---

# Multi-Model Orchestration

Transform Opus into a strategic orchestrator that delegates tasks to specialized models via forked terminals, keeping Opus's context clean for user interaction and synthesis.

## Model Specializations

| Model | Context | Strengths | Use For |
|-------|---------|-----------|---------|
| **Gemini Flash** | 1M tokens | Fast, massive context | Quick exploration, file discovery |
| **Gemini Pro** | 1M tokens | Deep reasoning | Architecture analysis, complex patterns |
| **Codex** | Large + compaction | SWE-bench leader | Implementation, refactoring, bug fixes |
| **Opus** (self) | Session context | User interaction, synthesis | Orchestration, decisions, coordination |

## Quick Reference

| I need to... | Fork to | Model | Output Location |
|--------------|---------|-------|-----------------|
| Explore large codebase | Gemini | gemini-3-flash | docs/exploration/ |
| Understand architecture | Gemini | gemini-3-pro | docs/exploration/ |
| Find patterns & conventions | Gemini | gemini-3-flash | docs/exploration/ |
| Implement feature | Codex | gpt-5.2-codex | docs/implementation/ |
| Refactor code | Codex | gpt-5.2-codex | docs/implementation/ |
| Fix bugs | Codex | gpt-5.2-codex | docs/implementation/ |
| Coordinate & decide | Stay in Opus | - | - |

## Orchestration Patterns

### Pattern 1: Explore-Then-Implement

The most common pattern. Gemini explores, Opus synthesizes, Codex implements.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Gemini    │───▶│    Opus     │───▶│    Codex    │
│  Explore    │    │  Synthesize │    │  Implement  │
└─────────────┘    └─────────────┘    └─────────────┘
      │                  │                   │
      ▼                  ▼                   ▼
docs/exploration/   User decisions   docs/implementation/
   {topic}.md       & coordination      {topic}-log.md
```

**Steps:**
1. Fork Gemini to explore codebase area
2. Read Gemini's exploration output (executive summary first)
3. Discuss findings with user, make decisions
4. Fork Codex with exploration context + implementation task
5. Monitor implementation, review results

### Pattern 2: Parallel Exploration

Multiple Gemini forks explore different aspects simultaneously.

```
                    ┌── Gemini: Auth ──▶ docs/exploration/auth.md
                    │
User Request ──▶ Opus ├── Gemini: DB ───▶ docs/exploration/db.md
                    │
                    └── Gemini: API ──▶ docs/exploration/api.md

              Then: Opus synthesizes all findings
```

**Use when:**
- Feature spans multiple subsystems
- Need comprehensive understanding quickly
- Independent areas to investigate

### Pattern 3: Iterative Refinement

Codex implements, Opus reviews, Codex refines.

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Codex    │───▶│    Opus     │───▶│    Codex    │
│  Implement  │    │   Review    │    │   Refine    │
└─────────────┘    └─────────────┘    └─────────────┘
      │                  │                   │
      ▼                  ▼                   ▼
  First pass       User feedback       Final version
```

## Task Structuring Guidelines

### For Gemini Exploration Tasks

Always include in the prompt:
1. **Clear scope** - What area/topic to explore
2. **Output location** - `docs/exploration/{topic}.md`
3. **Output format** - Request progressive disclosure format
4. **Specific questions** - What you need to know

**Example prompt structure:**
```
Explore the {TOPIC} in this codebase.

Focus on:
- {SPECIFIC_QUESTION_1}
- {SPECIFIC_QUESTION_2}
- {SPECIFIC_QUESTION_3}

Write findings to docs/exploration/{topic}.md using this format:
[Include progressive disclosure template]
```

### For Codex Implementation Tasks

Always include in the prompt:
1. **Context reference** - Point to exploration doc if available
2. **Clear requirements** - What to build/change
3. **Output location** - `docs/implementation/{topic}-log.md`
4. **Validation commands** - How to verify success

**Example prompt structure:**
```
Implement {FEATURE} based on the exploration in docs/exploration/{topic}.md.

Requirements:
- {REQUIREMENT_1}
- {REQUIREMENT_2}

After implementation:
1. Run tests: {TEST_COMMAND}
2. Document changes in docs/implementation/{topic}-log.md
3. List all files modified
```

## Result Handoff Patterns

### Gemini Output Format (Progressive Disclosure)

Gemini exploration outputs follow this structure:

```markdown
# {Topic} Exploration

## Executive Summary
[2-3 sentence overview - the "5-second answer"]

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
[Key facts table - the "30-second scan"]

## Architecture Overview
[High-level structure, diagrams if helpful]

## Critical Files
| File | Purpose | Key Lines |
|------|---------|-----------|
| `path/to/file.ts` | Description | 45-67 |
[Comprehensive list - err on side of including more]

## Patterns & Conventions
[Code patterns, naming conventions, architectural decisions]

## Integration Points
[APIs, interfaces, dependencies, data flow]

## Edge Cases & Gotchas
[Non-obvious behaviors, special cases, potential pitfalls]

## Recommendations
[Specific guidance for implementation phase]

## Raw Findings
[Verbose details, code snippets, full context - the "deep dive"]
```

**Rationale**: Gemini's 1M context can capture everything. Opus reads summary/TOC first, drills into details only as needed.

### Codex Output Format

```markdown
# {Topic} Implementation Log

## Summary
[What was implemented, key decisions made]

## Files Changed
| File | Change Type | Description |
|------|-------------|-------------|
| `path/to/file.ts` | Modified | Added auth middleware |

## Tests
- [x] Unit tests passing
- [x] Integration tests passing
- [ ] E2E tests (need manual run)

## Validation
```
$ npm test
✓ All tests pass
```

## Notes
[Anything the orchestrator should know]
```

## Reading Results

When a forked agent completes, read results progressively:

1. **Read Executive Summary** - Get the gist
2. **Scan Quick Reference** - Key facts at a glance
3. **Check Critical Files** - If you need specifics
4. **Deep dive Raw Findings** - Only if needed

This preserves Opus context while getting necessary information.

## Anti-Patterns

### Don't Fork for Simple Tasks
If it can be done in 2-3 tool calls, just do it. Forking has overhead.

### Don't Lose Context Between Forks
Always reference previous outputs when starting new forks.

### Don't Over-Orchestrate
Not every task needs explore-then-implement. Use judgment.

### Don't Forget Output Locations
Always specify where the forked agent should write results.

## Integration with Fork-Terminal

This skill works with the `fork-terminal` skill. Use fork-terminal to:
1. Create the forked terminal
2. Pass the structured prompt
3. Monitor for completion via output file

See: `.claude/skills/fork-terminal/SKILL.md`
