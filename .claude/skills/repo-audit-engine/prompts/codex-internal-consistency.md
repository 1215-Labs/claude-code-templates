# Internal Consistency Audit

Use this template when forking Codex for internal consistency verification during `/repo-audit` Phase 1.

## Variables

- `{REPO_PATH}` - Absolute path to the target repository
- `{REPO_NAME}` - Directory basename
- `{RUN_DIR}` - Run output directory

## Prompt Template

```
Audit internal consistency of the repository at {REPO_PATH}.

## Context

- Repository: {REPO_NAME}
- Path: {REPO_PATH}

## Your Task

Find dead code, orphaned configs, broken imports, stale references, and unused components. This is a **hygiene audit** focused on internal consistency — not documentation or deployment.

For every finding, include a **reproduction command** so engineers can verify and fix it.

## Checks

### 1. Dead Code Detection

Find code that exists but is never used:

- **Exported symbols with no importers** — functions, classes, constants exported but never imported elsewhere
- **Files with no imports** — source files that nothing imports from
- **Functions defined but never called** — especially in utility/helper files
- **Test files for deleted source** — test files whose source counterpart no longer exists
- **Commented-out code blocks** — large blocks of commented code (>10 lines)

Reproduction commands:
- TypeScript: `npx tsc --noEmit` (type errors often reveal dead code)
- JavaScript/TypeScript: `npx knip` or `npx ts-prune` (dead export detection)
- Python: `vulture {REPO_PATH}/src/` (unused code detection)
- General: `grep -r "import.*from.*<module>" {REPO_PATH}/src/` (check import counts)

### 2. Orphaned Configuration

Find config files for tools that aren't installed or used:

- **Config without dependency**: `.eslintrc*` without eslint in deps, `jest.config.*` without jest, `.prettierrc` without prettier
- **Env vars not referenced**: Variables in `.env.example` that no source file reads
- **Docker configs referencing missing files**: Dockerfile COPY/ADD for paths that don't exist
- **CI steps for missing scripts**: Workflow files calling scripts that don't exist

Reproduction commands:
- `npx depcheck` (Node.js — finds unused deps and missing deps)
- `grep -r "process.env.VAR_NAME" src/` (check if env var is referenced)
- `test -f path/referenced/in/dockerfile` (check Docker path)

### 3. Import/Reference Integrity

Verify all code references resolve:

- **All import paths resolve** to existing files/modules
- **All require() calls** reference existing modules
- **TypeScript path aliases** in tsconfig.json point to existing directories
- **Symlinks** point to existing targets
- **Package.json bin entries** point to existing scripts

Reproduction commands:
- TypeScript: `npx tsc --noEmit` (catches broken imports)
- Node.js: `node -e "require('./path')"` (test require resolution)
- Symlinks: `find {REPO_PATH} -type l -exec test ! -e {} \; -print` (find broken symlinks)

### 4. .claude/ Component Consistency (if .claude/ exists)

Check internal consistency of Claude Code components:

- **Commands reference existing skills**: If a command prompt mentions reading a skill, that skill exists
- **Skills' `related` fields**: Every command/agent listed in `related` exists
- **Hooks reference existing scripts**: Hook commands point to existing executables
- **MANIFEST.json paths**: Every path in MANIFEST.json resolves to a real file
- **REGISTRY.md entries**: Match what actually exists in .claude/ subdirectories
- **Frontmatter references**: `allowed-tools`, `related`, `argument-hint` are consistent

Reproduction commands:
- `find {REPO_PATH}/.claude/commands -name "*.md" | head -20` (list all commands)
- `grep -r "related:" {REPO_PATH}/.claude/ --include="*.md"` (find all related fields)
- `cat {REPO_PATH}/.claude/MANIFEST.json | jq '.components[].path'` (list manifest paths)

### 5. Dependency Hygiene

Check package dependency health:

- **Unused dependencies**: Packages in dependencies that are never imported
- **Phantom dependencies**: Packages imported but not in package.json (relying on transitive)
- **Lock file freshness**: Lock file exists and matches package.json version ranges
- **Duplicate dependencies**: Same package at multiple versions
- **Security advisories**: Known vulnerabilities (check without running network requests — just note if `npm audit` or similar should be run)

Reproduction commands:
- `npx depcheck` (unused and missing deps)
- `npm ls --depth=0 2>&1 | grep "UNMET"` (unmet peer deps)
- `diff <(jq -r '.dependencies | keys[]' package.json) <(jq -r '.packages | keys[] | sub("node_modules/";"")' package-lock.json | sort -u)` (lock drift)

### 6. Naming Consistency

Check for naming convention violations:

- **File naming**: Is it consistent? (kebab-case, camelCase, PascalCase, snake_case)
- **Directory naming**: Matches file convention
- **Export naming**: Consistent with file names (e.g., `user-service.ts` exports `UserService`)
- **Mixed conventions**: Files in the same directory using different patterns

Note: only flag if there's clear inconsistency within the same directory or layer. Different conventions between, say, config files and source files are acceptable.

## Scoring

Apply the Internal Consistency rubric (100 points):

| Criterion | Points | Check |
|-----------|--------|-------|
| No dead code | +15 | No unreachable exported symbols |
| No orphaned configs | +10 | Config files match installed tools |
| All imports resolve | +20 | Every import/require points to existing module |
| No stale .claude/ references | +15 | Commands, skills, agents reference existing files |
| Package scripts work | +10 | All scripts in package.json/Makefile are valid |
| No unused dependencies | +10 | Every dep is imported somewhere |
| Consistent naming | +10 | File and variable naming is uniform |
| No stale TODOs | +10 | No TODO/FIXME in runtime paths older than 90 days |

Grade: A (90-100), B (80-89), C (70-79), D (60-69), F (<60)

## Gating Issues

These cap the overall audit grade at C:
- Critical import paths are broken (app won't start)
- Package.json scripts reference non-existent files/commands

## Output Requirements

Write your output as structured JSON to stdout. Use exactly this schema:

{
  "layer": "internal-consistency",
  "executive_summary": "2-3 sentences summarizing internal hygiene",
  "score": 72,
  "grade": "C",
  "total_issues": 12,
  "by_severity": {"HIGH": 2, "MEDIUM": 5, "LOW": 5},
  "gating_issues": [
    {
      "issue": "src/index.ts imports from ./services/auth which does not exist",
      "evidence": "File src/services/auth.ts was deleted in commit abc123 but import remains"
    }
  ],
  "findings": [
    {
      "severity": "MEDIUM",
      "category": "dead-code",
      "description": "exportedHelper in src/utils/legacy.ts has no importers",
      "source_path": "src/utils/legacy.ts",
      "source_line": 42,
      "status": "ORPHANED",
      "reproduction_command": "grep -r 'exportedHelper' src/ --include='*.ts'",
      "fix_suggestion": "Remove exportedHelper or add import where needed"
    }
  ],
  "evidence_index": ["src/**/*.ts", "package.json", "tsconfig.json", ".claude/"],
  "scoring_breakdown": [
    {
      "criterion": "No dead code",
      "points_possible": 15,
      "points_awarded": 10,
      "notes": "3 unused exports found in utils/"
    }
  ]
}
```

## Tips

1. **Run static analysis mentally** — trace imports, check exports, verify references
2. **Be specific** — cite file paths and line numbers, not vague descriptions
3. **Include reproduction commands** — every finding should have a command to verify it
4. **Dynamic imports are LOW severity** — flag but don't penalize heavily (plugin systems use them)
5. **Distinguish layers** — test files having different conventions than source is fine
6. **Check .claude/ if present** — component consistency is important for Claude Code repos
7. **Focus on runtime paths** — dead code in tests is less critical than dead code in src/
