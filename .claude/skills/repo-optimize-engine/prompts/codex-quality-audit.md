# Quality Audit

Use this template when forking Codex for quality audit during `/repo-optimize` Phase 1.

## Variables

- `{REPO_PATH}` - Absolute path to the target repository
- `{REPO_NAME}` - Directory basename (e.g., `cbass`, `mac-manage`)
- `{TEMPLATES_REPO}` - Path to the claude-code-templates repo
- `{MODE}` - `greenfield`, `upgrade`, or `audit`
- `{EXISTING_COMPONENTS}` - List of existing .claude/ components found (may be empty for greenfield)

## Prompt Template

```
Audit the Claude Code configuration for the repository at {REPO_PATH}.

## Context

- Repository: {REPO_NAME}
- Path: {REPO_PATH}
- Templates repo: {TEMPLATES_REPO}
- Mode: {MODE}
- Existing components: {EXISTING_COMPONENTS}

## Your Task

Perform a comprehensive quality audit of the existing .claude/ directory (or determine what should exist for a greenfield repo). Score every existing component using the freshness rubric. Your audit will be used alongside a Gemini needs analysis to build an optimization plan.

## Audit Areas

### 1. Component Inventory

List every component found in {REPO_PATH}/.claude/:
- Agents (.claude/agents/*.md)
- Commands (.claude/commands/**/*.md)
- Skills (.claude/skills/*/SKILL.md)
- Hooks (.claude/hooks/)
- Workflows (.claude/workflows/*.md)
- Rules (.claude/rules/*.md)
- CLAUDE.md files (root, .claude/, any nested)

For each, note: name, type, last modified, file size.

### 2. Freshness Scores

Score each component on the 100-point freshness rubric:

| Criterion | Points | Check |
|-----------|--------|-------|
| Current frontmatter schema | +10 | Uses latest YAML fields (name, description, related, etc.) |
| `related` fields present | +5 | Cross-references other components |
| Tools properly restricted | +10 | Uses allowed-tools, not over-permissioned |
| `$ARGUMENTS` usage correct | +5 | Commands accept and parse input properly |
| Prompt specificity | +15 | Specific instructions vs generic/vague |
| Matches latest template | +15 | Compare against templates in {TEMPLATES_REPO}/.claude/skills/repo-equip-engine/SKILL.md |
| Has completion criteria | +10 | Defines what "done" looks like |
| Error handling present | +10 | Handles edge cases, validates input |
| References context skill | +10 | Uses shared knowledge base when applicable |
| Documentation quality | +10 | Clear, concise, actionable |

To score "matches latest template": read the templates in the repo-equip-engine SKILL.md (Context Skill Template, Command Template) and compare structural alignment.

### 3. Coverage Gaps

Based on the repo's tech stack, determine what SHOULD be configured vs what IS:

**Check for these signals:**
- tsconfig.json / *.ts files → needs type-checker, LSP agents, LSP skills
- Dockerfile / .github/workflows/ → needs deployment-engineer agent
- Frontend files (React/Vue/Svelte/HTML) → needs /ui-review, agent-browser
- MCP server code (@modelcontextprotocol) → needs mcp-backend-engineer
- CLI with subcommands → needs wrapper commands
- Domain terminology → needs context skill with glossary

### 4. Quality Issues

Flag specific problems:
- Vague prompts ("help with code" vs "analyze TypeScript files for type safety violations")
- Missing tool restrictions (allowed-tools not specified)
- No `related` fields (components not cross-referenced)
- Broken references (references to files/skills that don't exist)
- Stale content (references to tools/patterns that have changed)
- Over-permissioned hooks (Bash(*) when more restricted would suffice)

### 5. Hook Effectiveness

If hooks exist, evaluate:
- Do they trigger on the right events?
- Are timeouts reasonable?
- Do they catch what they should (formatting, linting, security)?
- Are there missing hooks the repo would benefit from?

### 6. CLAUDE.md Quality

Score the root CLAUDE.md (and any nested ones) on:
- Commands/workflows documented (are build/test/deploy present?)
- Architecture clarity (can Claude understand the structure?)
- Non-obvious patterns (gotchas, quirks documented?)
- Conciseness (not verbose, not obvious info?)
- Currency (reflects current state?)
- Actionability (instructions are executable, not vague?)

Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)

## Mode-Specific Instructions

### If MODE is greenfield:
There is no .claude/ directory. Instead, audit against "what should exist":
- Read the repo's README, package.json, config files
- Determine tech stack
- List what components SHOULD be configured based on the tech stack
- Score the gap as if every missing component scores 0/100

### If MODE is upgrade:
The repo was previously equipped from our templates. Focus on:
- Which components have fallen behind the latest template versions
- Whether new template features are missing (e.g., new frontmatter fields)
- Whether the repo has evolved and now needs components that weren't relevant before

### If MODE is audit:
The repo has a hand-built .claude/ directory. Focus on:
- Quality of what exists (using the freshness rubric)
- Whether patterns match our conventions or are idiosyncratic
- How to migrate toward our template patterns without losing custom value

## Output Requirements

Write your audit to docs/optimization/{REPO_NAME}-audit.md using this exact format:

# {REPO_NAME} Quality Audit

## Executive Summary
[2-3 sentences: overall quality assessment, most critical finding, recommended action]

## Overall Scores

| Metric | Score |
|--------|-------|
| Average freshness | XX/100 (Grade: X) |
| CLAUDE.md quality | XX/100 (Grade: X) |
| Coverage | XX% of detected needs addressed |
| Components audited | N |
| Components missing | N |

## Component Scorecard

| Component | Type | Freshness | Grade | Key Issue |
|-----------|------|-----------|-------|-----------|
| [name] | agent/command/skill/hook | XX/100 | A-F | [one-line issue] |

## Detailed Findings

### [Component Name] (XX/100, Grade X)

| Criterion | Score | Notes |
|-----------|-------|-------|
| Current frontmatter | X/10 | [specific finding] |
| Related fields | X/5 | [specific finding] |
| Tools restricted | X/10 | [specific finding] |
| $ARGUMENTS usage | X/5 | [specific finding] |
| Prompt specificity | X/15 | [specific finding] |
| Matches template | X/15 | [specific finding] |
| Completion criteria | X/10 | [specific finding] |
| Error handling | X/10 | [specific finding] |
| Context skill ref | X/10 | [specific finding] |
| Documentation | X/10 | [specific finding] |
| **Total** | **XX/100** | |

[Repeat for each component]

## Coverage Gaps

| Need (from tech stack) | Expected Component | Status |
|------------------------|--------------------|--------|
| [e.g., TypeScript] | type-checker agent | Missing / Present / Stale |

## Quality Issues

| Severity | Component | Issue | Fix |
|----------|-----------|-------|-----|
| High | [name] | [problem] | [recommended fix] |
| Medium | [name] | [problem] | [recommended fix] |
| Low | [name] | [problem] | [recommended fix] |

## CLAUDE.md Assessment

| Criterion | Score | Notes |
|-----------|-------|-------|
| Commands documented | X/20 | [finding] |
| Architecture clarity | X/20 | [finding] |
| Non-obvious patterns | X/15 | [finding] |
| Conciseness | X/15 | [finding] |
| Currency | X/15 | [finding] |
| Actionability | X/15 | [finding] |
| **Total** | **XX/100** | **Grade: X** |

## Recommendations (Priority Order)

### Critical (fix immediately)
[Issues that actively hurt the Claude experience]

### Important (fix soon)
[Issues that leave significant gaps]

### Nice to Have (fix when convenient)
[Polish and completeness improvements]
```

## Tips

1. **Read the actual templates** — compare against {TEMPLATES_REPO}/.claude/skills/repo-equip-engine/SKILL.md templates
2. **Be specific** — cite file paths and line numbers for every finding
3. **Score fairly** — components that predate a convention shouldn't be penalized as harshly
4. **Coverage matters** — a missing component that the tech stack demands is a bigger issue than a slightly outdated one
5. **Greenfield is hardest** — you're auditing absence, so be thorough about what the tech stack signals
