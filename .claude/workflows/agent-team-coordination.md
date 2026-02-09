---
name: agent-team-coordination
description: End-to-end workflow for coordinating agent teams from creation through cleanup
trigger: Complex task requiring parallel work
---

# Agent Team Coordination Workflow

Complete workflow for creating, managing, and cleaning up agent teams.

## Workflow Sequence

```
1. /quick-prime                     → Project context
         ↓
2. /spawn-team "task"               → Create team (roles, tasks, ownership)
         ↓
3. [Lead coordinates]               → Task assignment + delegation
         ↓
4. [TeammateIdle hook]              → Per-teammate quality gate
         ↓
5. [TaskCompleted hook]             → Per-task build/lint gate
         ↓
6. [Lead synthesizes]               → Consolidate findings
         ↓
7. /code-review                     → Final review of all changes
         ↓
8. [Clean up team]                  → Shutdown teammates + cleanup
```

## Step Details

### Step 1: Project Context
**Command**: `/quick-prime`
- Get project overview and conventions
- Identify key directories for file ownership
- Understand tech stack and test patterns

### Step 2: Team Creation
**Command**: `/spawn-team "task description"`
- Analyzes task to determine team size and roles
- Verifies agent teams feature is enabled
- Creates team with context-rich spawn prompts
- Seeds task list with 5-6 tasks per teammate

### Step 3: Lead Coordination
The team lead:
- Assigns tasks to teammates (or teammates self-claim)
- Monitors progress via the shared task list (Ctrl+T)
- Redirects teammates if they go off track
- Does NOT implement — stays in delegate mode (Shift+Tab)

### Step 4: TeammateIdle Quality Gate
**Hook**: `teammate-idle-gate.py` (TeammateIdle event)
- Checks for uncommitted changes before allowing idle
- Checks for unclaimed pending tasks
- Blocks idle with feedback if issues found

### Step 5: TaskCompleted Quality Gate
**Hook**: `task-completed-gate.py` (TaskCompleted event)
- Detects project type (Node, Python, Rust, Go)
- Runs build/lint if available
- Checks for uncommitted changes
- Blocks completion with feedback if quality checks fail

### Step 6: Synthesis
The team lead:
- Collects deliverables from all teammates
- Identifies conflicts or contradictions
- Produces a consolidated summary
- Recommends next actions

### Step 7: Final Review
**Command**: `/code-review`
- Comprehensive review of all team changes
- Verify no file conflicts between teammates
- Check that all tasks are actually complete

### Step 8: Cleanup
Tell the lead: "Clean up the team"
- Shuts down all teammates
- Removes shared team resources
- Check for orphaned tmux sessions: `tmux ls`

## Decision Points

| Situation | Action |
|-----------|--------|
| Teammate stuck on a task | Message them directly (Shift+Up/Down), or reassign the task |
| File conflict between teammates | Lead resolves; reassign file ownership for remaining work |
| Lead starts implementing | Press Shift+Tab to re-enable delegate mode |
| Teammate finishes early | They self-claim the next pending task |
| Task dependency blocked | Check if blocking task is actually done; update status if so |
| Build fails in quality gate | Teammate must fix before task can be marked complete |
| Teammate goes idle with pending work | TeammateIdle hook sends them back to work |
| All teammates done but lead hasn't synthesized | Message the lead: "Synthesize all findings" |
| Orphaned tmux session after cleanup | `tmux kill-session -t <name>` |

## Related Components

- **Command**: `/spawn-team` — team creation entry point
- **Skill**: `agent-teams` — best practices reference
- **Hooks**: `teammate-idle-gate.py`, `task-completed-gate.py` — quality gates
- **Command**: `/code-review` — final validation
- **Command**: `/quick-prime` — project context
