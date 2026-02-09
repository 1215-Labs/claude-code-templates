---
name: repo-optimize
description: |
  Multi-model repo optimization with Gemini Pro + Codex analysis and 3-agent team execution.
  Analyzes a target repo, identifies gaps and stale components, and executes an upgrade plan.

  Usage: /repo-optimize "<path to repo>" ["optional focus hint"]

  Examples:
  /repo-optimize "/home/mdc159/projects/cbass"
  /repo-optimize "/home/mdc159/projects/api-server" "focus on testing and deployment"
  /repo-optimize "/home/mdc159/projects/mac-manage" "CLI wrapper commands"

  Best for: Deep multi-model analysis and parallel team optimization of any repo
  Use instead: /repo-equip for quick single-agent initial setup
  See also: /spawn-team, /orchestrate, /repo-equip
argument-hint: "<repo path>" ["focus hint"]
user-invocable: true
related:
  commands: [workflow/repo-equip, workflow/spawn-team, workflow/orchestrate]
  skills: [repo-optimize-engine, repo-equip-engine, skill-evaluator,
           multi-model-orchestration, agent-teams, fork-terminal]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Write
  - Grep
  - Glob
  - Task
  - AskUserQuestion
  - TeamCreate
  - TaskCreate
  - TaskUpdate
  - TaskList
  - SendMessage
---

# Repo Optimization

**Target**: $ARGUMENTS

Reference the `repo-optimize-engine` skill for mode detection, freshness scoring, impact scoring, task graph generation rules, and team configuration. Reference the `repo-equip-engine` skill for Component Applicability Matrix, Gap Detection Heuristics, Complexity Scoring, and all Templates.

---

## Phase 0: Validate & Detect Mode

### Parse Arguments

Extract from `$ARGUMENTS`:
- **First argument**: Target repo path (required) — strip surrounding quotes if present
- **Second argument**: Focus hint (optional) — strip surrounding quotes if present

If no arguments provided, ask the user for the repo path using `AskUserQuestion`.

### Validate Target

1. **Path exists**: Verify the directory exists and is accessible. If not, error with clear message.
2. **Not this repo**: Resolve the path to absolute. If it resolves to the claude-code-templates repo, decline and suggest: "This is the templates repo itself. Use `/sync-reference` to update it."
3. **Is a git repo**: Check for `.git/` directory. Warn if absent but don't block.

### Set Working Variables

- `REPO_PATH`: Absolute path to target repo
- `REPO_NAME`: Directory basename (e.g., `cbass`, `mac-manage`)
- `FOCUS_HINT`: Second argument or empty string
- `TEMPLATES_REPO`: Path to this claude-code-templates repo (use `git rev-parse --show-toplevel`)

### Detect Mode

Follow the mode detection logic from `repo-optimize-engine`:

1. Check if `REPO_PATH/.claude/` exists
   - **No** → `MODE = greenfield`
2. If yes, read `TEMPLATES_REPO/MANIFEST.json` and check if any component name starts with `REPO_NAME` or description mentions `REPO_NAME`
   - **Found** → `MODE = upgrade`
   - **Not found** → `MODE = audit`

Report to user:
```
## Optimization Target: {REPO_NAME}
- **Path**: {REPO_PATH}
- **Mode**: {MODE}
- **Focus**: {FOCUS_HINT or "none (full analysis)"}
```

---

## Phase 1: Multi-Model Analysis

### Prepare

1. Create output directory:
   ```bash
   mkdir -p docs/optimization
   ```

2. If MODE is `upgrade` or `audit`, build `EXISTING_COMPONENTS` list:
   - List all files in `REPO_PATH/.claude/agents/`, `REPO_PATH/.claude/commands/`, `REPO_PATH/.claude/skills/`, `REPO_PATH/.claude/hooks/`, `REPO_PATH/.claude/workflows/`
   - Format as a simple list of relative paths

### Fork Gemini Pro — Needs Analysis

1. Read the prompt template: `.claude/skills/repo-optimize-engine/prompts/gemini-needs-analysis.md`
2. Extract the prompt template section (between the ``` fences under "Prompt Template")
3. Fill variables: `{REPO_PATH}`, `{REPO_NAME}`, `{FOCUS_HINT}`, `{MODE}`
4. Write the filled prompt to a temp file:
   ```bash
   GEMINI_PROMPT_FILE=$(mktemp /tmp/repo-optimize-gemini-XXXXXX.md)
   ```
5. Fork Gemini:
   ```bash
   python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
     "gemini -p \"$(cat $GEMINI_PROMPT_FILE)\" --model gemini-3-pro-preview --approval-mode yolo"
   ```

### Fork Codex — Quality Audit

1. Read the prompt template: `.claude/skills/repo-optimize-engine/prompts/codex-quality-audit.md`
2. Extract and fill variables: `{REPO_PATH}`, `{REPO_NAME}`, `{TEMPLATES_REPO}`, `{MODE}`, `{EXISTING_COMPONENTS}`
3. Write filled prompt to temp file:
   ```bash
   CODEX_PROMPT_FILE=$(mktemp /tmp/repo-optimize-codex-XXXXXX.md)
   ```
4. Fork Codex:
   ```bash
   python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex \
     "codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex \"$(cat $CODEX_PROMPT_FILE)\""
   ```

### Poll for Completion

Both forks should produce output files. Poll every 15 seconds, timeout after 5 minutes:

```bash
NEEDS_FILE="docs/optimization/${REPO_NAME}-needs.md"
AUDIT_FILE="docs/optimization/${REPO_NAME}-audit.md"

for i in $(seq 1 20); do
  FOUND=0
  [ -f "$NEEDS_FILE" ] && FOUND=$((FOUND+1))
  [ -f "$AUDIT_FILE" ] && FOUND=$((FOUND+1))
  [ "$FOUND" -ge 2 ] && break
  echo "Waiting for analysis... ($i/20)"
  sleep 15
done
```

Report progress to user as each file appears.

### Fallback

If either output file is missing after timeout:

**Gemini fallback**: Check logs at `/tmp/fork_gemini_*.log`. If Gemini failed, dispatch a Sonnet subagent via the Task tool with the same filled prompt. Note "Sonnet (Gemini fallback)" in models used.

**Codex fallback**: Check logs at `/tmp/fork_codex_*.log`. If Codex failed, dispatch a Sonnet subagent via the Task tool with the same filled prompt. Note "Sonnet (Codex fallback)" in models used.

Track which models actually contributed in a `MODELS_USED` variable.

---

## Phase 2: Synthesis & Task Graph

### Read Analysis Results

1. Read `docs/optimization/{REPO_NAME}-needs.md` — start with Executive Summary and Quick Reference
2. Read `docs/optimization/{REPO_NAME}-audit.md` — start with Executive Summary and Overall Scores
3. Deep-read remaining sections as needed for cross-referencing

### Cross-Reference Findings

Apply the priority rules from `repo-optimize-engine`:

| Gemini Says | Codex Says | Priority |
|-------------|-----------|----------|
| "Repo needs X" | "X is stale/missing/weak" | **High** |
| "Repo needs Y" | (no mention) | **Medium** — new addition |
| (no mention) | "Z has quality issues" | **Medium** — quality fix |

### Generate Task List

For each identified upgrade, assign:
- **Impact**: high / medium / low (per `repo-optimize-engine` rules)
- **Effort**: simple (1-3) or complex (4+) (per `repo-equip-engine` complexity scoring)
- **Category**: config / command / docs (determines teammate)

Apply the task graph generation rules from `repo-optimize-engine`:
- Context skill = always T1 (if needed), no blockers
- Hooks = no blockers
- MANIFEST + REGISTRY = no blockers
- Commands = blocked by T1 (context skill)
- Workflows = blocked by T1
- PRPs = no blockers
- CLAUDE.md = blocked by commands + workflows
- Skill-priorities = blocked by commands + workflows
- Validation = blocked by CLAUDE.md + skill-priorities

Use dynamic task generation: skip task slots that aren't needed. If no context skill is needed, remove the T1 blocker from commands.

### Present Plan

1. Read the plan template: `.claude/skills/repo-optimize-engine/templates/optimization-plan.md`
2. Fill all variables with synthesized data
3. Present the filled plan to the user

### Get Approval

Use `AskUserQuestion` with options:
- **Proceed with full plan** — execute all tasks including PRPs
- **Modify plan** — let user adjust tasks/priorities before proceeding
- **Proceed without PRPs** — only direct work, skip complex gaps

If user chooses "Modify plan", discuss changes and re-present. Loop until approved.

### Save Plan

Write the approved plan to `docs/optimization/{REPO_NAME}-plan.md` for teammate reference.

---

## Phase 3: Agent Team Execution

### Environment Check

Verify agent teams are available:
```bash
echo $CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS
```

If not set, inform the user: "Agent teams require the `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS` environment variable. Set it and restart Claude Code, or I can execute the plan sequentially instead."

If agent teams unavailable, fall back to sequential execution: run config tasks, then command tasks, then docs tasks, all as the lead agent. Skip team creation.

### Create Team

```
TeamCreate: {REPO_NAME}-optimize
Description: "Optimizing {REPO_NAME} Claude Code configuration"
```

### Seed Tasks

Use `TaskCreate` for each task in the approved plan. Wire `blockedBy` using the actual returned task IDs (not assumed numbers).

**Important**: Capture each TaskCreate return value to get the real task ID. Use these IDs for blockedBy references.

Example sequence:
1. Create T1 (context skill, no blockers) → get ID_1
2. Create T2 (hooks, no blockers) → get ID_2
3. Create T3 (MANIFEST, no blockers) → get ID_3
4. Create T4 (commands, blockedBy: [ID_1]) → get ID_4
5. Create T5 (workflows, blockedBy: [ID_1]) → get ID_5
6. Create T6 (PRPs, no blockers) → get ID_6
7. Create T7 (CLAUDE.md, blockedBy: [ID_4, ID_5]) → get ID_7
8. Create T8 (skill-priorities, blockedBy: [ID_4, ID_5]) → get ID_8
9. Create T9 (validation, blockedBy: [ID_7, ID_8]) → get ID_9

Assign task ownership via TaskUpdate:
- T1, T2, T3 → owner: "config-upgrader"
- T4, T5, T6 → owner: "command-builder"
- T7, T8, T9 → owner: "docs-finalizer"

### Spawn Teammates

Read the spawn template: `.claude/skills/repo-optimize-engine/templates/teammate-spawn.md`

For each teammate, fill the template variables and spawn via the Task tool:

**config-upgrader** (Sonnet, general-purpose subagent):
- Fill: REPO_PATH, REPO_NAME, TEMPLATES_REPO, NEEDS_DOC, AUDIT_DOC, PLAN_DOC, ASSIGNED_TASKS (T1, T2, T3 details)
- Include team_name: `{REPO_NAME}-optimize`
- Name: `config-upgrader`

**command-builder** (Sonnet, general-purpose subagent):
- Fill: same variables, ASSIGNED_TASKS (T4, T5, T6 details)
- Include team_name: `{REPO_NAME}-optimize`
- Name: `command-builder`

**docs-finalizer** (Sonnet, general-purpose subagent):
- Fill: same variables, ASSIGNED_TASKS (T7, T8, T9 details)
- Include team_name: `{REPO_NAME}-optimize`
- Name: `docs-finalizer`

### Lead Behavior

After spawning teammates:

1. **Enter delegate mode** — remind user: "Press Shift+Tab to enable delegate mode so teammates can work autonomously."
2. **Monitor task list** — check TaskList periodically for completions
3. **Handle messages** — respond to teammate questions or conflicts
4. **Do NOT implement** — the lead coordinates only, no file editing

### Progress Tracking

As teammates complete tasks:
- T1 completion → notify user: "Context skill created. command-builder unblocked."
- T4+T5 completion → notify user: "Commands and workflows done. docs-finalizer unblocked."
- T9 completion → proceed to Phase 4

---

## Phase 4: Summary & Teardown

### Run Installer

After all tasks complete:
```bash
python3 scripts/install-global.py
```

Verify output shows new components installed without errors.

### Verify Symlinks

```bash
ls -la ~/.claude/skills/${REPO_NAME}-context 2>/dev/null
ls -la ~/.claude/commands/${REPO_NAME}/ 2>/dev/null
```

Check for broken symlinks.

### Compile Final Summary

Read the validation results from docs-finalizer (T9). Present:

```markdown
# Optimization Complete: {REPO_NAME}

## Mode: {MODE}
## Models Used: {MODELS_USED}

## What Changed
- {N} components created, {N} updated, {N} unchanged
- Freshness score: {before}/100 → {after}/100  (upgrade/audit modes only)
- Coverage: {before}% → {after}% of detected needs addressed

## Components

| Component | Action | Status |
|-----------|--------|--------|
| {component} | Created/Updated/Unchanged | Installed globally / In target repo |

## Deferred (PRPs)

| PRP | Purpose | Next Step |
|-----|---------|-----------|
| PRPs/{REPO_NAME}-{feature}.md | {purpose} | `/prp-claude-code-execute "PRPs/{file}"` |

## Next Steps
1. Run `/all_skills` in {REPO_NAME} to verify installed components
2. Test new commands: `/{REPO_NAME}-status`, `/{REPO_NAME}-*`
3. Execute PRPs if generated: `/prp-claude-code-execute "PRPs/{file}"`
4. Run `/repo-optimize` again in 2-4 weeks to catch drift
```

### Shutdown Team

Send shutdown requests to all teammates:
```
SendMessage: type=shutdown_request, recipient=config-upgrader
SendMessage: type=shutdown_request, recipient=command-builder
SendMessage: type=shutdown_request, recipient=docs-finalizer
```

Wait for shutdown confirmations before finishing.

### Cleanup

- Remove temp prompt files: `/tmp/repo-optimize-gemini-*.md`, `/tmp/repo-optimize-codex-*.md`
- Analysis artifacts stay in `docs/optimization/` for future reference

---

## Sequential Fallback (No Agent Teams)

If agent teams are unavailable, execute the plan sequentially as the lead agent:

1. **Config tasks** (T1, T2, T3): Create context skill, hooks, update MANIFEST + REGISTRY
2. **Command tasks** (T4, T5, T6): Create commands, workflows, PRPs
3. **Run installer**: `python3 scripts/install-global.py`
4. **Docs tasks** (T7, T8, T9): Update CLAUDE.md, generate skill-priorities, validate

Follow the same templates and patterns as the team execution, just executed serially.

---

## Related Commands

- `/repo-equip` — Quick single-agent initial setup (simpler, faster, less thorough)
- `/spawn-team` — Generic agent team creation
- `/orchestrate` — Single-model delegation (Gemini or Codex)
- `/sync-reference` — Sync the templates repo itself against references
- `/all_skills` — Verify installed components after optimization
