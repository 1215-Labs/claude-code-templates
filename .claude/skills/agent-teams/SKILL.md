---
name: agent-teams
description: Best practices and patterns for coordinating multiple Claude Code instances as an agent team — role design, task decomposition, conflict avoidance, and quality gates
version: 1.0.0
category: orchestration
user-invocable: false
related:
  skills: [multi-model-orchestration, fork-terminal]
  commands: [/spawn-team]
  workflows: [agent-team-coordination]
---

# Agent Teams — Patterns & Best Practices

Reference skill for orchestrating Claude Code agent teams. Not user-invocable — used by `/spawn-team` and the `agent-team-coordination` workflow.

## When to Use Agent Teams

```
Task requires parallel work?
  ├── No → Single session or subagents
  └── Yes
       ├── Workers need to communicate? → Agent teams
       ├── Workers just report results? → Subagents
       └── Workers need different models? → /orchestrate (forked terminals)
```

**Strong use cases:**
- Parallel exploration — multiple angles on a research question
- Multi-angle review — security, performance, test coverage in parallel
- Cross-layer features — frontend, backend, tests each owned by a teammate
- Competing hypotheses — adversarial debugging with multiple investigators
- New modules — each teammate owns a separate directory/module

**When NOT to use:**
- Sequential tasks where step N depends on step N-1
- Same-file edits (teammates will overwrite each other)
- Heavy dependency chains between work items
- Token-budget-constrained situations (N teammates ≈ N+1 sessions)
- Simple tasks completable in one session (coordination overhead > benefit)

## Team Sizing

| Team Size | Best For | Example |
|-----------|----------|---------|
| 2 | Paired review, research + implementation | Security + performance review |
| 3 | Multi-angle review, cross-layer feature | Frontend + backend + tests |
| 4 | Large feature with clear module boundaries | API + UI + DB + tests |
| 5 | Competing hypotheses, broad investigation | 5 theories for a mysterious bug |

**Rule of thumb**: more teammates = more coordination overhead. Start small.

## Role Patterns

### Parallel Reviewers (2-3 teammates)
Each reviewer focuses on a distinct lens (security, performance, test coverage). Lead synthesizes findings.

### Cross-Layer Builders (3-4 teammates)
Each teammate owns a layer: frontend, backend, database, tests. File ownership prevents conflicts.

### Competing Investigators (3-5 teammates)
Each teammate tests a different hypothesis. They message each other to challenge findings. The theory that survives is most likely correct.

### Architect + Implementers (1 + 2-3 teammates)
One teammate plans the architecture (plan approval required), others implement after approval.

### Research Council (2-4 teammates)
Each teammate researches a different aspect (API options, performance benchmarks, security implications). Lead synthesizes into a recommendation.

## Task Decomposition

Create 5-6 tasks per teammate. Each task should be:

- **Self-contained** — completable without waiting on other tasks (unless explicitly blocked)
- **Clear deliverable** — a function, test file, review report, or documentation section
- **Explicit file ownership** — list which files/directories the task touches
- **Verifiable** — the lead or a hook can check if it's actually done
- **Right-sized** — not so small that coordination overhead dominates, not so large that progress is invisible

### Example Task Structure

```
Teammate: backend-api
  Task 1: Implement GET /users endpoint (src/routes/users.ts)
  Task 2: Implement POST /users endpoint (src/routes/users.ts)
  Task 3: Add input validation middleware (src/middleware/validate.ts)
  Task 4: Write unit tests (tests/routes/users.test.ts)
  Task 5: Add OpenAPI schema (docs/api/users.yaml)
  Task 6: Update route index (src/routes/index.ts) [blocked by Task 1, 2]
```

## Spawn Prompt Templates

### Reviewer
```
Review {target} focusing exclusively on {lens}. For each finding:
1. Severity (critical/high/medium/low)
2. File and line reference
3. Specific recommendation
Do NOT fix code — report only. Save findings to {output_path}.
```

### Implementer
```
Implement {feature} in {directory}. Follow existing patterns in {reference_file}.
You own these files exclusively: {file_list}.
Do NOT modify files outside your ownership.
Run tests after each change: {test_command}.
```

### Researcher
```
Research {topic} and document findings. Focus on:
- {aspect_1}
- {aspect_2}
- {aspect_3}
Save report to {output_path}. Include code examples where relevant.
```

### Architect
```
Design the architecture for {feature}. Produce a plan covering:
- Module boundaries and interfaces
- File structure and naming
- Data flow
- Error handling strategy
- Test strategy
Plan approval is required before implementation begins.
```

## Conflict Avoidance

### File Ownership Rules
- Each file should be owned by exactly one teammate
- The lead should NOT edit files (use delegate mode)
- If two teammates need the same file, split the file or serialize access via task dependencies

### Directory Partitioning
```
teammate-frontend/  → owns src/components/, src/pages/
teammate-backend/   → owns src/api/, src/services/
teammate-tests/     → owns tests/
teammate-docs/      → owns docs/
```

### Shared Files
For files that multiple teammates need (e.g., `index.ts`, `types.ts`):
- Designate one teammate as the owner
- Other teammates add tasks that are blocked until the owner is done
- Or: have the lead make shared-file edits after teammates finish

## Display Mode Selection

| Environment | Recommended Mode | Notes |
|-------------|-----------------|-------|
| WSL2 | `in-process` | tmux can be unreliable under WSL |
| macOS + iTerm2 | `tmux` (auto-detects iTerm2) | Best visual experience |
| macOS + tmux | `tmux` | Native split panes |
| VS Code terminal | `in-process` | Split panes not supported |
| SSH session | `in-process` | Unless tmux is already running |

## Delegate Mode

**When to enable**: whenever you want the lead to focus on coordination, not implementation. Especially important for teams of 3+.

**How**: press `Shift+Tab` after team creation to cycle into delegate mode.

**What it does**: restricts the lead to coordination-only tools — spawning, messaging, shutting down teammates, and managing tasks. Prevents the lead from doing implementation work itself.

## Plan Approval

**When to require**: for teammates doing architectural design, risky refactoring, or changes that affect multiple modules.

**How**: include "require plan approval" in the spawn prompt.

**Criteria patterns**:
- "Only approve plans that include test coverage"
- "Reject plans that modify the database schema"
- "Approve plans that stay within the assigned directory"

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| **Over-teaming** | 5 teammates for a 2-file change | Use subagents or a single session |
| **Under-contexting** | Spawn prompt says "fix the bug" | Include file paths, error messages, constraints |
| **File collision** | Two teammates edit `index.ts` | Enforce file ownership, use task dependencies |
| **Lead does work** | Lead implements instead of delegating | Enable delegate mode (Shift+Tab) |
| **Orphan cleanup** | Team ends without `clean up the team` | Always clean up; check for orphaned tmux sessions |
| **No quality gates** | Tasks marked complete without verification | Use TeammateIdle and TaskCompleted hooks |
| **Broadcast spam** | Lead broadcasts every update to all | Use targeted messages; broadcast sparingly |

## Token Awareness

- N teammates ≈ N+1 concurrent context windows (N teammates + 1 lead)
- Each teammate loads CLAUDE.md, MCP servers, skills independently
- For cheaper parallelism on focused tasks, prefer subagents
- Use Sonnet for implementation teammates to reduce cost
- Reserve Opus for the lead and architect roles

## Keyboard Reference

| Key | Action |
|-----|--------|
| `Shift+Up/Down` | Select teammate (in-process mode) |
| `Enter` | View selected teammate's session |
| `Escape` | Interrupt teammate's current turn |
| `Ctrl+T` | Toggle task list |
| `Shift+Tab` | Cycle permission mode (enable delegate) |
