# Docs-to-Code Alignment Audit

Use this template when forking Gemini for docs-to-code verification during `/repo-audit` Phase 1.

## Variables

- `{REPO_PATH}` - Absolute path to the target repository
- `{REPO_NAME}` - Directory basename
- `{RUN_DIR}` - Run output directory (e.g., `/tmp/repo-audit/myapp/20260211_143022`)
- `{KNOWN_DRIFT}` - Contents of Known Drift section from INDEX.md (may be empty)

## Prompt Template

```
Audit documentation accuracy for the repository at {REPO_PATH}.

## Context

- Repository: {REPO_NAME}
- Path: {REPO_PATH}
- Known Drift (accepted mismatches, skip these): {KNOWN_DRIFT}

## Your Task

Systematically verify that every claim in the repository's documentation matches the actual codebase. This is a **verification audit**, not a needs analysis or code review.

## Methodology

### Step 1: Inventory All Documentation

List every documentation file found:
- `.claude/INDEX.md` (if present — highest priority)
- `CLAUDE.md` (root and any nested `.claude/CLAUDE.md`)
- `README.md`
- `docs/` directory contents
- `CONTRIBUTING.md`
- `API.md` or similar API documentation
- `CHANGELOG.md` (check if recent entries match reality)

### Step 2: Extract Verifiable Claims

For each doc, extract every factual claim that can be verified against the codebase:

| Claim Type | Example | How to Verify |
|-----------|---------|---------------|
| Build command | "Build with `npm run build`" | Check package.json scripts |
| Entry point | "Entry point is src/index.ts" | Check file exists |
| Dependency | "Uses PostgreSQL" | Check package.json/pyproject.toml |
| API endpoint | "POST /api/users" | Check route definitions |
| Test command | "Run tests with `pytest`" | Check test config and deps |
| Directory claim | "Services are in src/services/" | Check directory exists |
| Component reference | "Use the /deploy command" | Check .claude/commands/ |
| Configuration | "Set DATABASE_URL in .env" | Check if referenced in code |

### Step 3: Verify Each Claim

For every extracted claim, classify:

- **VERIFIED**: Claim matches reality exactly
- **STALE**: Was once true but no longer (file moved, dependency removed, API changed)
- **INACCURATE**: Never true or significantly wrong
- **PARTIAL**: Partially true (e.g., endpoint exists but method or path differs)

For each non-VERIFIED finding, provide:
- `source_path`: Which doc file contains the claim
- `source_line`: Line number (if possible)
- `claim`: What the doc says
- `reality`: What actually exists
- `fix_suggestion`: How to fix the doc

### Step 4: INDEX.md Deep Check (if present)

If `.claude/INDEX.md` exists, perform targeted verification:

1. **Line count**: Is it within the 80-line budget? Count actual lines.
2. **Purpose field**: Is it present and non-empty?
3. **"If you only read one file today"**: Does the referenced path exist?
4. **Quick Facts table**: Verify each row:
   - Stack → matches detected languages/frameworks
   - Deploy → matches detected deploy config (Dockerfile, Caddyfile, etc.)
   - Entry point → file exists at that path
   - Build → command exists in package.json/Makefile/etc.
   - Test → test framework and command are correct
   - Package mgr → matches lock file (package-lock.json → npm, uv.lock → uv, etc.)
5. **Documentation Map**: Every path in the table points to an existing file
6. **Critical Paths**: Every backtick-quoted path references existing dirs/files
7. **Anti-Patterns**: Check if the codebase actually follows these (or violates its own rules)
8. **Known Drift**: Entries have dates and describe real accepted mismatches

If `.claude/INDEX.md` does NOT exist:
- Flag as "INDEX.md missing"
- If CLAUDE.md > 200 lines, recommend creating INDEX.md for progressive disclosure

### Step 5: Cross-Document Consistency

Check for contradictions between documentation files:
- README says one thing, CLAUDE.md says another
- INDEX.md Quick Facts disagree with README
- Inline code comments contradict external docs
- Different versions of the same instruction in different files

### Step 6: .claude/ Component Documentation

If `.claude/` directory exists with commands, agents, or skills:
- Verify every component mentioned in CLAUDE.md actually exists as a file
- Verify every component file that exists is mentioned somewhere in documentation
- Check that `related` fields in component frontmatter reference existing components
- Check that `allowed-tools` are reasonable for each component's purpose

## Scoring

Apply the Docs-to-Code rubric (100 points):

| Criterion | Points | Check |
|-----------|--------|-------|
| Build/test commands accurate | +15 | Commands in docs run successfully |
| README project description current | +10 | Matches actual functionality |
| API docs match endpoints | +15 | Every documented endpoint exists |
| Directory structure matches docs | +10 | Documented paths exist |
| INDEX.md present and accurate | +15 | All fields verified (or -15 if missing with large CLAUDE.md) |
| Commands/agents referenced exist | +15 | Every named .claude/ component findable |
| Environment setup docs current | +10 | .env.example matches actual usage |
| Glossary terms match code usage | +10 | Terminology consistent |

Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)

## Output Requirements

Write your output as structured JSON to stdout. Use exactly this schema:

{
  "layer": "docs-to-code",
  "executive_summary": "2-3 sentences summarizing documentation accuracy",
  "score": 85,
  "grade": "B",
  "total_issues": 7,
  "by_severity": {"HIGH": 1, "MEDIUM": 3, "LOW": 3},
  "gating_issues": [],
  "findings": [
    {
      "severity": "HIGH",
      "category": "stale-doc",
      "description": "README claims PostgreSQL but no postgres dependency found",
      "source_path": "README.md",
      "source_line": 15,
      "claim": "Uses PostgreSQL for data storage",
      "reality": "No @prisma/client or pg in package.json; uses SQLite via better-sqlite3",
      "status": "STALE",
      "fix_suggestion": "Update README to reference SQLite"
    }
  ],
  "index_md_status": "present_with_issues",
  "index_md_findings": [
    {
      "check": "Quick Facts: Entry point exists",
      "passed": true,
      "details": "src/index.ts exists"
    }
  ],
  "evidence_index": ["README.md", "CLAUDE.md", ".claude/INDEX.md", "package.json", "src/routes/"],
  "scoring_breakdown": [
    {
      "criterion": "Build/test commands accurate",
      "points_possible": 15,
      "points_awarded": 15,
      "notes": "npm run build and npm test both valid"
    }
  ]
}
```

## Tips

1. **Read broadly** — check all documentation, not just CLAUDE.md and README
2. **Be precise** — cite exact file paths and line numbers for every finding
3. **Verify commands** by checking if the referenced tool exists in dependencies, not by running them
4. **INDEX.md is highest priority** — agents read it first, so inaccuracies there are HIGH severity
5. **Cross-doc contradictions are HIGH severity** — conflicting instructions cause agent confusion
6. **Skip Known Drift items** — these are accepted mismatches, don't flag them
7. **Score fairly** — a new project with minimal docs isn't the same as a mature project with stale docs
