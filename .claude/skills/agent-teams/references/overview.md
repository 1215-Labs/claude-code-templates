# Agent Teams — Reference Overview

## Key Concepts

- **Lead + teammates model**: One Opus lead coordinates; Sonnet teammates implement. The lead should enter delegate mode (Shift+Tab) for teams of 3+ to prevent accidental implementation work.
- **File ownership prevents conflicts**: Each file belongs to exactly one teammate. If two teammates need the same file, serialize access via task dependencies or have the lead make shared-file edits after teammates finish.
- **Task decomposition is the critical skill**: Create 5-6 self-contained tasks per teammate. Each task must have a clear deliverable, explicit file ownership, and be verifiable.
- **Token cost scales linearly**: N teammates = N+1 concurrent context windows. Prefer subagents for focused parallel tasks; reserve agent teams for work requiring inter-agent communication.

## Decision Criteria

### Teams vs. Alternatives

```
Task requires parallel work?
  No  → Single session or subagents
  Yes →
    Workers need to communicate?     → Agent teams
    Workers just report results?     → Subagents (cheaper)
    Workers need different models?   → /orchestrate (forked terminals)
```

### When to Use Agent Teams

| Scenario | Use Teams? | Why |
|----------|-----------|-----|
| Parallel exploration (multiple angles) | Yes | Workers can share findings |
| Multi-angle review (security + perf + tests) | Yes | Each reviewer needs full context |
| Cross-layer feature (frontend + backend + tests) | Yes | Clear file ownership per layer |
| Competing hypotheses for debugging | Yes | Adversarial communication helps |
| Sequential task chain (step N needs step N-1) | No | Use task dependencies instead |
| Same-file edits needed | No | Will cause conflicts |
| Simple task completable in one session | No | Coordination overhead > benefit |
| Token-budget-constrained | No | N teammates = N+1 sessions |

### Team Sizing

| Size | Best For | Example |
|------|----------|---------|
| 2 | Paired review, research + implementation | Security + performance review |
| 3 | Multi-angle review, cross-layer feature | Frontend + backend + tests |
| 4 | Large feature with clear module boundaries | API + UI + DB + tests |
| 5 | Competing hypotheses, broad investigation | 5 theories for a mysterious bug |

## Quick Reference

### Role Patterns

| Pattern | Teammates | Lead Role |
|---------|-----------|-----------|
| Parallel Reviewers | 2-3 reviewers, each with a distinct lens | Synthesize findings |
| Cross-Layer Builders | Each owns a layer (frontend/backend/db/tests) | Coordinate, resolve conflicts |
| Competing Investigators | Each tests a different hypothesis | Adjudicate the winning theory |
| Architect + Implementers | 1 architect (plan approval), 2-3 implementers | Approve plans, unblock |
| Research Council | Each researches a different aspect | Synthesize into recommendation |

### Spawn Prompt Templates

**Reviewer:**
```
Review {target} focusing exclusively on {lens}.
For each finding: severity, file+line, specific recommendation.
Do NOT fix code — report only. Save findings to {output_path}.
```

**Implementer:**
```
Implement {feature} in {directory}. Follow patterns in {reference_file}.
You own these files exclusively: {file_list}.
Do NOT modify files outside your ownership.
Run tests after each change: {test_command}.
```

### Display Mode Selection

| Environment | Mode |
|-------------|------|
| WSL2 | in-process (tmux unreliable) |
| macOS + iTerm2/tmux | tmux |
| VS Code terminal | in-process |
| SSH session | in-process |

### Task Ownership Rules

- One file = one owner. No exceptions.
- Lead should NOT edit files when in delegate mode.
- Shared files (index.ts, types.ts): designate one owner; others create blocked tasks.

### Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| Over-teaming (5 teammates for 2-file change) | Use subagents or single session |
| Under-contexting ("fix the bug") | Include file paths, error messages, constraints |
| File collision (two teammates edit index.ts) | Enforce file ownership + task dependencies |
| Lead does implementation work | Enable delegate mode (Shift+Tab) |
| No quality gates | Use TeammateIdle and TaskCompleted hooks |
| Broadcast spam to all teammates | Use targeted messages instead |
