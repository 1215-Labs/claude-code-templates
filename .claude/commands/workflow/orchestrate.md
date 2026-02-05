---
name: orchestrate
description: |
  Delegate tasks to Gemini (exploration) or Codex (implementation) via forked terminals.

  Usage: /orchestrate "<task description>"

  Examples:
  /orchestrate "explore the authentication system"
  /orchestrate "analyze the database schema and relationships"
  /orchestrate "implement user profiles based on docs/exploration/profiles.md"
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
- **Exploration** - Understanding, analyzing, discovering patterns
- **Implementation** - Building, coding, changing, fixing

**Exploration indicators**: "explore", "analyze", "understand", "find", "discover", "how does", "what is", "architecture", "patterns"

**Implementation indicators**: "implement", "build", "add", "create", "fix", "refactor", "update", "change", "based on"

### Step 2: Select Model & Prepare

#### If Exploration Task

1. **Model**: Gemini (gemini-3-flash for quick, gemini-3-pro for deep analysis)
2. **Output location**: `docs/exploration/{topic-slug}.md`
3. **Read prompt template**: `.claude/skills/multi-model-orchestration/prompts/exploration-task.md`
4. **Prepare structured prompt** with:
   - Clear scope of exploration
   - Specific questions to answer
   - Output format (progressive disclosure)
   - Output file location

#### If Implementation Task

1. **Model**: Codex (gpt-5.2-codex)
2. **Output location**: `docs/implementation/{feature-slug}-log.md`
3. **Read prompt template**: `.claude/skills/multi-model-orchestration/prompts/implementation-task.md`
4. **Check for exploration context**: Look for referenced `docs/exploration/*.md`
5. **Prepare structured prompt** with:
   - Reference to exploration doc (if exists)
   - Clear requirements
   - Validation commands
   - Output log location

### Step 3: Create Output Directories

```bash
mkdir -p docs/exploration docs/implementation
```

### Step 4: Fork Terminal

Invoke the `fork-terminal` skill with the appropriate tool:

**For Exploration (Gemini)**:
- Use Gemini CLI with structured exploration prompt
- Include `--thinking-level medium` for analysis tasks
- Include `--thinking-level high` for architecture reviews

**For Implementation (Codex)**:
- Use Codex CLI with structured implementation prompt
- Reference any relevant exploration docs in the prompt

### Step 5: Report to User

After forking, report:
1. **Task type identified** (exploration/implementation)
2. **Model selected** and why
3. **Expected output location**
4. **How to check results** when complete

## Quick Reference

| Task Type | Model | Thinking | Output |
|-----------|-------|----------|--------|
| Quick exploration | gemini-3-flash | minimal | docs/exploration/ |
| Deep analysis | gemini-3-flash | medium | docs/exploration/ |
| Architecture review | gemini-3-pro | high | docs/exploration/ |
| Implementation | gpt-5.2-codex | - | docs/implementation/ |

## Related

- `fork-terminal` skill - Terminal forking mechanics
- `multi-model-orchestration` skill - Full orchestration patterns
- `/deep-prime` - Alternative for Opus-native exploration
