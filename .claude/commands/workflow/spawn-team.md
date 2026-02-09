---
name: spawn-team
description: |
  Create and coordinate an agent team for parallel work

  Usage: /spawn-team "<task description>"

  Examples:
  /spawn-team "Review PR #42 from security, performance, and test angles"
  /spawn-team "Investigate why websocket connections drop after 5 minutes"
  /spawn-team "Build user profile feature: API, UI, and tests in parallel"
  /spawn-team "Research caching strategies: Redis vs Memcached vs in-memory"

  Best for: Parallel review, multi-angle investigation, cross-layer features
  Use instead: /orchestrate for delegating to Gemini/Codex
  Use instead: /rca for focused debugging (single session)
argument-hint: "<task description>"
user-invocable: true
related:
  skills: [agent-teams, multi-model-orchestration]
  workflows: [agent-team-coordination]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Write
  - Task
---

# Agent Team Orchestration

**Task**: $ARGUMENTS

Create and coordinate an agent team to tackle this task with parallel work. Follow the agent-teams skill for best practices.

## Phase 1: Task Analysis

Analyze the task to determine the optimal team structure:

1. **Classify task type**:
   - `review` — parallel review from different angles (security, performance, tests)
   - `investigation` — competing hypotheses or multi-angle debugging
   - `implementation` — cross-layer feature with clear module boundaries
   - `research` — parallel research on different aspects of a topic

2. **Determine team size** (2-5 teammates):
   - 2: paired review, research + implementation
   - 3: multi-angle review, cross-layer feature
   - 4: large feature with clear module boundaries
   - 5: competing hypotheses, broad investigation

3. **Assign roles** — name each teammate and define their focus area. Use descriptive names like `security-reviewer`, `backend-impl`, `hypothesis-connection-pool`.

4. **Choose display mode**:
   - `in-process` (default) — works everywhere, use Shift+Up/Down to navigate
   - `tmux` — if user is already in tmux or on macOS with iTerm2

5. **Flag coordination needs**:
   - Enable delegate mode for teams of 3+ (prevents lead from implementing)
   - Require plan approval for architect/refactoring roles

## Phase 2: Environment Check

Before creating the team, verify the environment:

1. **Check agent teams is enabled**:
   ```bash
   # Verify CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is set
   echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
   ```
   If not set, inform the user they need to enable it in settings.json:
   ```json
   { "env": { "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1" } }
   ```

2. **Check display mode availability**:
   - On WSL: recommend `in-process` (tmux can be unreliable)
   - If tmux requested: verify `which tmux`
   - Default: `in-process`

3. **Get project context** (quick scan):
   - Read CLAUDE.md for project conventions
   - Check project type (package.json, pyproject.toml, etc.)
   - Identify key directories for file ownership assignment

## Phase 3: Team Creation

Tell Claude to create the agent team. Structure the prompt with rich context for each teammate:

For each teammate, the spawn prompt should include:
- **Role and objective** — what they're responsible for
- **File/directory ownership** — which files they can modify (prevents conflicts)
- **Specific instructions** — what to look for, what to produce
- **Constraints** — what NOT to do (e.g., don't modify files outside ownership)
- **Deliverable** — what the output should look like
- **Model selection** — Opus for lead/architect, Sonnet for implementation/review

Example team creation prompt:
```
Create an agent team with 3 teammates:

1. "security-reviewer" (Sonnet): Review src/auth/ for security vulnerabilities.
   Focus on token handling, session management, input validation.
   Produce a findings report with severity ratings.

2. "perf-reviewer" (Sonnet): Review src/api/ for performance issues.
   Focus on N+1 queries, missing indexes, unnecessary serialization.
   Produce a findings report with impact estimates.

3. "test-reviewer" (Sonnet): Review tests/ for coverage gaps.
   Focus on edge cases, error paths, integration tests.
   Produce a coverage gap report with recommended test additions.
```

## Phase 4: Task Seeding

Break the work into 5-6 tasks per teammate with:
- Clear task titles
- Explicit file paths
- Dependencies between tasks (use `blockedBy` for ordering)
- Quality criteria (what "done" looks like)

Example task structure:
```
security-reviewer tasks:
  1. Scan auth module for OWASP Top 10 patterns
  2. Check JWT token handling and expiration
  3. Review input validation on all endpoints
  4. Check for information leakage in error responses
  5. Verify CORS and CSP configuration
  6. Write consolidated security findings report [blocked by 1-5]
```

## Phase 5: Coordination

After team creation:

1. **Enable delegate mode** (for teams of 3+):
   Remind the user to press `Shift+Tab` to prevent the lead from implementing.

2. **Set plan approval criteria** (if applicable):
   "Only approve plans that include test coverage and stay within assigned directories."

3. **Wait instruction**:
   Tell the lead: "Wait for all teammates to complete their tasks before synthesizing."

4. **Synthesis plan**:
   Once all teammates finish, the lead should:
   - Collect all deliverables
   - Identify conflicts or contradictions
   - Produce a consolidated summary
   - Recommend next actions

## Phase 6: User Guidance

Report the team structure to the user:

```
Agent Team Created
==================
Task: [task description]
Type: [review/investigation/implementation/research]
Display: [in-process/split-pane]

Teammates:
  1. [name] — [role] (model)
  2. [name] — [role] (model)
  3. [name] — [role] (model)

Quick controls:
  Shift+Up/Down  — Select teammate
  Enter          — View teammate session
  Escape         — Interrupt teammate
  Ctrl+T         — Toggle task list
  Shift+Tab      — Enable delegate mode

Quality gates active:
  TeammateIdle   — Checks for uncommitted changes + pending tasks
  TaskCompleted  — Runs build/lint before allowing task completion
```

## Related Commands

- `/orchestrate` — Delegate to Gemini/Codex via forked terminals
- `/code-review` — Run after team finishes for final validation
- `/rca` — Use instead for focused single-session debugging
