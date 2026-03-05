---
name: repo-audit
description: |
  Multi-layer repo alignment audit using forked Gemini + Codex analysis and Opus synthesis.
  Checks docs-to-code accuracy, internal consistency, and deploy alignment.

  Usage: /repo-audit "<path to repo>" ["layer filter"]

  Examples:
  /repo-audit "/home/mdc159/projects/cbass"
  /repo-audit "/home/mdc159/projects/api-server" "docs"
  /repo-audit "/home/mdc159/projects/mac-manage" "deploy"
  /repo-audit "/home/mdc159/projects/myapp" "dry-run"

  Layer filters: docs, internal, deploy, all (default), dry-run
  Best for: Comprehensive alignment check before releases, after major refactors
  Use instead: /repo-optimize for gaps and upgrades (builds things)
  See also: /repo-optimize, /code-review
argument-hint: "<repo path>" ["docs|internal|deploy|all|dry-run"]
user-invocable: true
related:
  commands: [workflow/repo-optimize, workflow/code-review]
  skills: [repo-audit-engine, fork-terminal, multi-model-orchestration]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Task
  - AskUserQuestion
---

# Multi-Layer Repo Alignment Audit

Read `.claude/skills/repo-audit-engine/SKILL.md` for scoring rubrics, fork allocation, and cross-reference rules.

## Phase 0: Validate and Configure

### Parse Arguments

```
REPO_PATH = first argument from $ARGUMENTS (required — error if missing)
LAYER_FILTER = second argument from $ARGUMENTS (optional, default "all")
```

Valid layer filters: `docs`, `internal`, `deploy`, `all`, `dry-run`

### Validate Target

1. Verify `REPO_PATH` exists and is a directory
2. Verify it's a git repo (`test -d $REPO_PATH/.git`)
3. Set `REPO_NAME` = basename of `REPO_PATH`
4. Verify this is NOT the claude-code-templates repo itself (compare resolved paths)

If validation fails, report the error and stop.

### Detect Applicable Layers

Check which layers apply:

- **docs-to-code**: Always applicable
- **internal-consistency**: Always applicable
- **code-to-deploy**: Check for deploy config signals:
  ```bash
  # Any of these existing enables the deploy layer
  test -f "$REPO_PATH/Dockerfile" || \
  test -f "$REPO_PATH/docker-compose.yml" || \
  test -f "$REPO_PATH/docker-compose.yaml" || \
  test -d "$REPO_PATH/.github/workflows" || \
  test -f "$REPO_PATH/Caddyfile" || \
  test -f "$REPO_PATH/nginx.conf" || \
  test -f "$REPO_PATH/vercel.json" || \
  test -f "$REPO_PATH/netlify.toml" || \
  test -f "$REPO_PATH/fly.toml" || \
  test -f "$REPO_PATH/Procfile" || \
  test -d "$REPO_PATH/k8s" || \
  test -d "$REPO_PATH/kubernetes" || \
  test -f "$REPO_PATH/serverless.yml" || \
  test -f "$REPO_PATH/render.yaml"
  ```

Collect list of detected deploy config files for the prompt template.

### Apply Layer Filter

If `LAYER_FILTER` is not `all` or `dry-run`, only run the specified layer:
- `docs` → only Fork A (Gemini docs-to-code)
- `internal` → only Fork B (Codex internal consistency)
- `deploy` → only Fork C (Gemini code-to-deploy, if applicable)

### Check for Known Drift

Read `.claude/INDEX.md` in the target repo. If it exists and has a `## Known Drift` section, extract its contents for the `{KNOWN_DRIFT}` variable.

### Report Configuration

Tell the user:
```
## Audit Target: {REPO_NAME}
- **Path**: {REPO_PATH}
- **Layers**: {list of applicable layers}
- **Filter**: {LAYER_FILTER}
- **Deploy configs**: {list or "none detected"}
- **Known drift items**: {count or "none"}
```

### Dry-Run Exit

If `LAYER_FILTER` is `dry-run`:
1. Show the configuration above
2. List which forks would be launched (model, layer, estimated duration)
3. Show filled prompt templates (read and fill, but don't launch)
4. Report: "Dry run complete. No LLMs were invoked."
5. **STOP HERE** — do not proceed to Phase 1

---

## Phase 1: Fork Gemini + Codex

### Setup Run Directory

```bash
RUN_ID=$(date +%Y%m%d_%H%M%S)
RUN_DIR="/tmp/repo-audit/${REPO_NAME}/${RUN_ID}"
mkdir -p "$RUN_DIR"
```

### Read and Fill Prompt Templates

Read the fork-terminal skill: `.claude/skills/fork-terminal/SKILL.md`

For each applicable layer, read the prompt template and fill variables:

1. **Fork A** (docs-to-code): Read `.claude/skills/repo-audit-engine/prompts/gemini-docs-to-code.md`
   - Fill: `{REPO_PATH}`, `{REPO_NAME}`, `{RUN_DIR}`, `{KNOWN_DRIFT}`
   - Write filled prompt to temp file: `DOCS_PROMPT=$(mktemp /tmp/repo-audit-docs-XXXXXX.md)`

2. **Fork B** (internal consistency): Read `.claude/skills/repo-audit-engine/prompts/codex-internal-consistency.md`
   - Fill: `{REPO_PATH}`, `{REPO_NAME}`, `{RUN_DIR}`
   - Write filled prompt to temp file: `INTERNAL_PROMPT=$(mktemp /tmp/repo-audit-internal-XXXXXX.md)`

3. **Fork C** (code-to-deploy, if applicable): Read `.claude/skills/repo-audit-engine/prompts/gemini-code-to-deploy.md`
   - Fill: `{REPO_PATH}`, `{REPO_NAME}`, `{RUN_DIR}`, `{DEPLOY_CONFIGS}`
   - Write filled prompt to temp file: `DEPLOY_PROMPT=$(mktemp /tmp/repo-audit-deploy-XXXXXX.md)`

### Launch Forks

**Complementary model allocation** — each model plays to its strengths:

| Fork | Model | Layer | Why |
|------|-------|-------|-----|
| A | Gemini (`gemini-2.5-flash`) | Docs-to-Code | 1M context for cross-referencing all docs against all code |
| B | Codex (`gpt-5.2-codex`) | Internal Consistency | SWE-bench leader for finding dead code, broken imports |
| C | Gemini (`gemini-2.5-flash`) | Code-to-Deploy | Broad context for deploy config cross-referencing |

**Launch Fork A + Fork B concurrently** (different providers, no rate conflict):

Read the fork-terminal cookbook for the appropriate tools, then:

**Fork A** (Gemini):
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool gemini \
  "gemini -p \"$(cat $DOCS_PROMPT)\" --model gemini-2.5-flash --approval-mode yolo"
```

**Fork B** (Codex):
```bash
python3 ~/.claude/skills/fork-terminal/tools/fork_terminal.py --log --tool codex \
  "codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex \"$(cat $INTERNAL_PROMPT)\""
```

Report to user: "Launched Fork A (Gemini → docs-to-code) and Fork B (Codex → internal consistency)"

### Poll for Results

Monitor fork output files. For Gemini, check the task executor output. For Codex, check its output files.

```bash
# Poll loop — 15s intervals, 20 iterations (5 min timeout)
for i in $(seq 1 20); do
  FOUND=0
  # Check Gemini fork A (look for output in /tmp/fork_gemini_*.log or task executor done files)
  # Check Codex fork B
  # Report progress: "Waiting for audit results... ($i/20)"
  sleep 15
done
```

**After Fork A completes**: If Fork C is applicable, launch it now (stays under 2 concurrent Gemini limit).

### Read Fork Results

For each completed fork, read the response:
- Gemini: Check `/tmp/fork_gemini_*.log` for JSON output
- Codex: Check `/tmp/fork_codex_*.log` or output summary
- Parse JSON response from each fork

### Fallback Chain

If a fork fails (timeout or error):
1. Check log files for error details
2. Dispatch a **Sonnet subagent** via Task tool with the same filled prompt
3. The subagent type should be `general-purpose` (it has all tools needed)
4. Note "Sonnet (fallback)" in models used

Track which models actually ran: `MODELS_USED` list.

---

## Phase 2: Opus Synthesis (Context-Light)

**Goal**: Synthesize fork results while keeping Opus context under 50%.

### Read Results Progressively

1. **First pass** — read only `executive_summary`, `score`, `grade`, and `gating_issues` from each fork result
2. **Cross-reference** — check for overlapping findings using the rules from SKILL.md:
   - If docs-to-code says "doc claims X exists" AND internal says "X is dead/missing" → promote to HIGH
   - Overlapping findings across layers get promoted one severity level
3. **Deep read** — only read full findings arrays if needed for cross-referencing

### Calculate Overall Score

- **Weighted average**: docs-to-code (35%), internal-consistency (35%), code-to-deploy (30%)
- If code-to-deploy was not applicable: docs-to-code (50%), internal-consistency (50%)
- **Gating check**: If ANY gating issue exists across any layer, cap overall grade at C

### Generate Fix First List

From all findings across all layers, select top 5 by:
1. Gating issues first (always top priority)
2. HIGH severity next, sorted by effort (S before M before L)
3. Include reproduction command or fix instruction for each

---

## Phase 3: Generate Report and Present

### Create Report

1. Read the report template: `.claude/skills/repo-audit-engine/templates/audit-report.md`
2. Fill all template variables with synthesized results
3. Create output directory if needed: `mkdir -p $REPO_PATH/docs/audit/`
4. Write report to: `$REPO_PATH/docs/audit/${REPO_NAME}-audit-$(date +%Y-%m-%d).md`

### Present Executive Summary

Show the user:
- Alignment scores table
- INDEX.md status
- Fix First top 5
- Link to full report

### Suggest Next Steps

Based on findings, suggest actions:

- **If critical issues found**: "Fix the {N} critical issues in the Fix First list"
- **If INDEX.md missing and CLAUDE.md > 200 lines**: "Create `.claude/INDEX.md` for progressive context disclosure — template at `.claude/skills/repo-audit-engine/templates/index-md.md`"
- **If grade is D or F**: "Run `/repo-optimize \"$REPO_PATH\"` to rebuild .claude/ components"
- **If deploy layer had issues**: "Review deployment configuration — port/env var mismatches can cause production failures"
- **If all layers grade A/B**: "Repo is in good shape. Consider scheduling periodic audits."

### Cleanup

Remove temporary prompt files:
```bash
rm -f /tmp/repo-audit-docs-*.md /tmp/repo-audit-internal-*.md /tmp/repo-audit-deploy-*.md
```

Keep the run directory (`/tmp/repo-audit/${REPO_NAME}/${RUN_ID}/`) for debugging — it will be cleaned up on next reboot.

---

## Important Notes

- **This command is read-only** — it never modifies the target repo's source code. The only file it creates is the audit report in `docs/audit/`.
- **Fork-terminal first** — use Gemini/Codex forks for all heavy analysis. Only use Opus for synthesis from result files.
- **Context discipline** — read executive summaries first, only deep-dive when cross-referencing requires it.
- **Stagger Gemini forks** — max 2 concurrent Gemini forks. Launch Fork C only after Fork A completes.
- **Fallback is Sonnet** — not Opus. If a fork fails, dispatch a Sonnet subagent with the same prompt.
