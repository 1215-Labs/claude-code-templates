# Agent Teams — Reference Overview

Supplementary reference for the `agent-teams` skill. Read SKILL.md for full instructions.

## When to Use Agent Teams vs. Alternatives

| Situation | Best Choice | Reason |
|-----------|-------------|--------|
| Workers need to communicate with each other | Agent teams | Messaging between teammates |
| Workers just report results to you | Subagents (Task tool) | Simpler, less overhead |
| Workers need different AI models | `/orchestrate` (forked terminals) | Multi-model support |
| Sequential steps, each depending on previous | Single session | No parallelism benefit |
| 2-file change | Single session | Coordination overhead exceeds benefit |

## Team Size Decision Criteria

Start with the smallest team that covers the independent workstreams:

- **2 teammates**: Paired review (two lenses on same code), or research + implementation
- **3 teammates**: Cross-layer feature (frontend + backend + tests), or 3-angle review
- **4 teammates**: Large feature with clear module boundaries (API + UI + DB + tests)
- **5 teammates**: Competing hypotheses — adversarial debugging where theories challenge each other

Rule: each additional teammate adds overhead. Default to fewer.

## Role Pattern Decision Tree

```
What is the team doing?
├── Reviewing existing code → Parallel Reviewers
│   Each reviewer: one lens (security / performance / test coverage)
│   Lead: synthesizes findings, does NOT implement
│
├── Building a new feature → Cross-Layer Builders
│   Each builder: one layer (frontend / backend / DB / tests)
│   File ownership prevents conflicts
│
├── Debugging a mysterious bug → Competing Investigators
│   Each investigator: one hypothesis
│   They message each other to challenge findings
│
├── Complex risky change → Architect + Implementers
│   Architect plans first, plan approval required before others start
│
└── Researching a decision → Research Council
    Each researcher: one aspect (options / benchmarks / security implications)
    Lead synthesizes into recommendation
```

## Critical Rules for Conflict Avoidance

**File ownership is non-negotiable:**
- Every file must have exactly one owner
- State explicit ownership in the spawn prompt: "You own these files exclusively: [list]"
- If two teammates need the same shared file (e.g., `index.ts`, `types.ts`):
  - Designate one as owner; others block on them
  - OR have the lead edit shared files after teammates finish

**The lead must stay in delegate mode (Shift+Tab):**
- Lead does NOT implement anything
- Lead only: spawns, messages, monitors task list, shuts down
- Failing to enable delegate mode is the most common mistake

## Task Quality Checklist

Each task assigned to a teammate must be:
- [ ] Self-contained (can start without waiting for another task, unless explicitly blocked)
- [ ] Has a clear, verifiable deliverable (a file, a report, a function)
- [ ] States which files the task will touch
- [ ] Right-sized: 5-6 tasks per teammate is the target

## Environment Compatibility

| Platform | Display Mode | Notes |
|----------|-------------|-------|
| WSL2 | `in-process` | tmux unreliable under WSL |
| macOS + iTerm2 | `tmux` | Best visual experience |
| VS Code terminal | `in-process` | Split panes not supported |
| SSH session | `in-process` | Unless tmux already running |

## Token Cost Awareness

N teammates costs approximately N+1 context windows in parallel. Each teammate independently loads CLAUDE.md, MCP servers, and skills. Use Sonnet for implementation teammates to reduce cost; reserve Opus for the lead and architect.

## Anti-Pattern Quick Reference

| Symptom | Root Cause | Fix |
|---------|-----------|-----|
| Two teammates modifying the same file | No file ownership enforced | Add explicit file lists to spawn prompts |
| Lead is writing code | Delegate mode not enabled | Press Shift+Tab after spawning |
| Tasks never completing | Tasks too large or blocked | Break into smaller units, verify blockers |
| Team left running after session | No cleanup step | Always end with "clean up the team" |
| Teammate doing the wrong thing | Spawn prompt too vague | Include file paths, constraints, examples |
