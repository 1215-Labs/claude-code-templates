---
name: orchestrate
description: |
  Delegate tasks to OpenCode (exploration/validation) or Codex (implementation) via forked terminals.
  Supports tag-team mode: Codex implements, then OpenCode oracle validates.

  Usage: /orchestrate "<task description>"

  Examples:
  /orchestrate "explore the authentication system"
  /orchestrate "analyze the database schema and relationships"
  /orchestrate "implement user profiles based on docs/exploration/profiles.md"
  /orchestrate "implement and validate the new API endpoint"
argument-hint: <task or directive>
user-invocable: true
thinking: auto
allowed-tools:
  - Read
  - Write
  - Bash(*)
  - Glob
  - Grep
  - Skill
---

# Multi-Model Orchestration Command

Delegate tasks to specialized models via forked terminals, keeping Opus context clean.

## Task Analysis

**User Request**: $ARGUMENTS

### Step 1: Classify Task Type

Determine if this is:
- **Exploration** — Understanding, analyzing, discovering patterns
- **Implementation** — Building, coding, changing, fixing
- **Tag-team** — Implement then validate (detected by "and validate", "and review", "implement and check")
- **Validation** — Review or validate existing code/changes

**Exploration indicators**: "explore", "analyze", "understand", "find", "discover", "how does", "what is", "architecture", "patterns", "research"

**Implementation indicators**: "implement", "build", "add", "create", "fix", "refactor", "update", "change", "based on"

**Tag-team indicators**: "implement and validate", "build and review", "code then check", "implement and verify"

**Validation indicators**: "review", "validate", "audit", "check", "verify"

### Step 2: Select Model & Prepare

#### If Exploration Task

1. **Agent**: OpenCode `oracle` (openai/gpt-5.2, strong reasoning, flat rate)
2. **Output location**: `docs/exploration/{topic-slug}.md`
3. **Prepare structured prompt** with:
   - Clear scope of exploration
   - Specific questions to answer
   - Output format (progressive disclosure)
   - Output file location

#### If Implementation Task

1. **Agent**: Codex `gpt-5.3-codex` (SWE-bench leader, flat rate)
2. **Output location**: `docs/implementation/{feature-slug}-log.md`
3. **Check for exploration context**: Look for referenced `docs/exploration/*.md`
4. **Prepare structured prompt** with:
   - Reference to exploration doc (if exists)
   - Clear requirements
   - Validation commands
   - Output log location

#### If Tag-Team (Implement + Validate)

Execute both phases sequentially:
1. **Phase 1 — Codex implements** (gpt-5.3-codex)
2. **Phase 2 — OpenCode oracle validates** (openai/gpt-5.2 via `momus` agent)
   - Launched after Codex completes (monitor done.json)
   - Receives: list of files Codex changed, the original task description
   - Reviews: code quality, correctness, potential issues

#### If Validation Task

1. **Agent**: OpenCode `momus` (openai/gpt-5.2, code review, flat rate)
2. **Output location**: `docs/validation/{topic-slug}.md`
3. **Prepare structured prompt** with:
   - Files to review
   - What to check for
   - Output format (issues found, recommendations)

### Step 3: Create Output Directories

```bash
mkdir -p docs/exploration docs/implementation docs/validation
```

### Step 4: Fork Terminal

Read the appropriate agent definition and follow its fork instructions:

**For Exploration/Validation (OpenCode)**:
- Read `.claude/agents/opencode-delegator.md`
- Use `oracle` agent for exploration, `momus` agent for validation
- Fork via: `py -3 .claude/skills/fork-terminal/tools/fork_terminal.py --log --tool opencode-task "uv run .claude/skills/fork-terminal/tools/opencode_task_executor.py {prompt_file} -n {slug} --agent {agent}"`

**For Implementation (Codex)**:
- Read `.claude/agents/codex-delegator.md`
- Fork via: `py -3 .claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex-task "uv run .claude/skills/fork-terminal/tools/codex_task_executor.py {prompt_file} -n {slug} -m gpt-5.3-codex"`

**For Tag-Team**:
1. Fork Codex first (implementation)
2. Monitor Codex done.json until complete
3. Read Codex summary to get list of changed files
4. Fork OpenCode `momus` with validation prompt referencing those files
5. Monitor OpenCode done.json until complete
6. Report both results

### Step 5: Report to User

After forking, report:
1. **Task type identified** (exploration/implementation/tag-team/validation)
2. **Agent selected** and why
3. **Expected output location**
4. **How to check results** when complete

For tag-team, report after each phase completes.

## Quick Reference

| Task Type | Agent | Model | Output |
|-----------|-------|-------|--------|
| Quick exploration | OpenCode `oracle` | openai/gpt-5.2 | docs/exploration/ |
| Deep analysis | OpenCode `oracle` | openai/gpt-5.2 | docs/exploration/ |
| Implementation | Codex | gpt-5.3-codex | docs/implementation/ |
| Code review | OpenCode `momus` | openai/gpt-5.2 | docs/validation/ |
| Tag-team | Codex → OpenCode `momus` | Both | docs/implementation/ + docs/validation/ |

## Oh-My-OpenCode Agents

| Agent | Model | Best For |
|-------|-------|----------|
| `hephaestus` | openai/gpt-5.3-codex | Implementation (flat rate) |
| `oracle` | openai/gpt-5.2 | Analysis, reasoning (flat rate) |
| `momus` | openai/gpt-5.2 | Code review, critique (flat rate) |
| `librarian` | opencode/glm-4.7-free | Lookup, search (free) |
| `atlas` | opencode/kimi-k2.5-free | General tasks (free) |

## Related

- `fork-terminal` skill — Terminal forking mechanics
- `opencode-delegator` agent — Full OpenCode orchestration logic
- `codex-delegator` agent — Full Codex orchestration logic
- `/opencode` — Direct OpenCode delegation
- `/codex` — Direct Codex delegation
- `/deep-prime` — Alternative for Opus-native exploration
