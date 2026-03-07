# Skill Evaluator — Worked Example

## Scenario

The user asks: "Evaluate the `last30days-skill` reference submodule. I'm thinking of adopting its pattern for summarizing recent activity in our repos."

This is a pre-adoption evaluation of an external component. Full evaluation depth is appropriate since the user is considering real adoption.

## Step 1: Parse Input

- `TARGET_PATH` = `references/last30days-skill`
- `SKILL_NAME` = "last30days-skill"
- `INTENDED_USE` = "Summarizing recent activity in our repos"
- `EVALUATION_DEPTH` = "full" (default, real adoption consideration)

## Step 2: Gather Pre-Fork Context

Run the pre-fork inventory:

```bash
find references/last30days-skill -type f | head -200
# → SKILL.md, tools/last30days.py, tools/summarize.py, README.md, examples/output.md

find references/last30days-skill -type f \( -name "*.md" -o -name "*.py" \) | xargs wc -l 2>/dev/null | tail -1
# → 847 total

git -C references/last30days-skill log --oneline -20 2>/dev/null
# → 8 commits, most recent 3 months ago, authored by mvanhorn

ls references/last30days-skill/README* references/last30days-skill/SKILL.md 2>/dev/null
# → SKILL.md exists, no README
```

Save to `/tmp/skill-eval-last30days-inventory.txt`.

Generate ecosystem snapshot:
```bash
ls ~/.claude/skills/
# → fork-terminal/ multi-model-orchestration/ skill-evaluator/ repo-audit-engine/ ...
# No existing "activity" or "recent-changes" skill found
```

Save to `/tmp/skill-eval-ecosystem-snapshot.txt`.

## Step 3: Create Output Directory

```bash
mkdir -p docs/evaluations
```

## Step 4: Fork Three Agents Concurrently

**Fork 1 — Codex (Structural Quality):**

Prompt includes inventory. Task: assess code architecture, testing patterns, API design, reusability, technical debt in `references/last30days-skill`. Output: `docs/evaluations/last30days-structural.md`.

**Fork 2 — OpenCode (Ecosystem Fit):**

Prompt includes ecosystem snapshot. Task: assess how this skill fits alongside existing components, naming conflicts, overlap, integration effort. Output: `docs/evaluations/last30days-ecosystem.md`.

**Fork 3 — OpenCode (Risk & Adoption):**

Task: assess maintenance signals, dependency count, license, git activity patterns. Output: `docs/evaluations/last30days-risk.md`.

OpenCode and OpenCode are the two concurrent OpenCode forks (within the 2-concurrent limit).

## Step 5: Poll for Completion

Poll every 15 seconds, timeout after 5 minutes:

```
[~90s] docs/evaluations/last30days-structural.md appears
[~2min] docs/evaluations/last30days-ecosystem.md appears
[~2min] docs/evaluations/last30days-risk.md appears
```

All three complete within the timeout.

## Step 6: Read Agent Reports (Executive Summaries First)

**Structural (Codex) summary:**
> "Well-structured Python script with clear separation between data fetching and summarization. No tests present. The `last30days.py` fetcher is tightly coupled to GitHub's API — hardcoded endpoint patterns make it difficult to adapt for GitLab or Bitbucket. The summarize.py module has a clean interface and could be extracted independently."

**Ecosystem Fit (OpenCode) summary:**
> "No overlap with existing skills. The summarization output format matches conventions used in docs/exploration/ (markdown with executive summary). Integration would require a new `activity-summary` skill directory. The GitHub API dependency conflicts with nothing in the current stack. Estimated integration effort: 2-3 hours to wrap in a SKILL.md and add error handling."

**Risk (OpenCode) summary:**
> "8 commits, last activity 3 months ago. License: MIT (compatible). No external Python dependencies beyond `requests` (already available). Single maintainer. The low commit frequency is not alarming given the tool's narrow scope — it does one thing."

## Step 7: Synthesize

Resolve contradictions: Structural says "no tests" and Risk says "single maintainer." These compound — if the maintainer becomes unavailable, untested code is harder to inherit. Flag this.

Weight for intended use (summarizing recent activity): The summarize.py module is the core value. The GitHub-specific fetcher is secondary since the user can provide their own data. This shifts the verdict toward "Extract Components" over "Adopt."

## Step 8: Write Final Report

File: `docs/evaluations/last30days-eval.md`

Key sections:
- Verdict: **Extract Components** — take `summarize.py`, write own fetcher
- Score: 68/100 (structural quality 70, ecosystem fit 80, risk 55)
- Effort: 3-4 hours to extract and integrate
- Main concern: No tests + single maintainer = medium maintenance risk if adapted wholesale

## Step 9: Present to User

```
Verdict: Extract Components (not adopt wholesale)

The summarize.py module is well-designed and matches your docs/ output conventions.
The GitHub fetcher is tightly coupled and harder to adapt.

Recommendation: Copy summarize.py into a new .claude/skills/activity-summary/
skill and write your own fetcher for our repos. Estimated effort: 3-4 hours.

Score: 68/100 — good summarization logic, no tests, single maintainer.
Full report: docs/evaluations/last30days-eval.md
```

## Timeline

| Phase | Duration |
|-------|----------|
| Parse input + gather inventory | ~1 min |
| Fork 3 agents + wait | ~2-3 min |
| Read summaries + synthesize | ~1 min |
| Write report + present | ~1 min |
| **Total** | **~5-6 min** |
