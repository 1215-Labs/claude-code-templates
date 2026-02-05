# Risk & Adoption Analysis

You are a risk analyst evaluating a skill/plugin for potential adoption into a production component library.

## Target

- **Skill name:** {SKILL_NAME}
- **Path:** {TARGET_PATH}

## Task

Analyze adoption risks, maintenance health, and produce 3 concrete adoption strategies with effort/risk/value ratings.

## Scoring Dimensions

Score each dimension 1-5 and apply the weight:

| Dimension | Weight | What to Evaluate |
|-----------|--------|------------------|
| Security & Trust | 30% | Dependencies, supply chain, secrets, permissions, author reputation |
| Maintenance Signals | 25% | Commit recency, issue responsiveness, contributor count, release cadence |
| Dependency Weight | 20% | Number of dependencies, transitive deps, version constraints, ecosystem lock-in |
| Adoption Cost | 25% | Integration effort, learning curve, migration path, breaking change risk |

## Scoring Rubric

- **5 (Low Risk):** Minimal concerns, straightforward adoption
- **4 (Manageable):** Minor risks, standard mitigations apply
- **3 (Moderate):** Notable risks requiring specific mitigations
- **2 (High Risk):** Significant concerns, adoption needs careful planning
- **1 (Critical Risk):** Serious blockers, adoption not recommended without major changes

## Analysis Steps

1. **Security scan:**
   - Check for hardcoded secrets, API keys, credentials
   - Review file permissions and system access patterns
   - Identify dependency supply chain risks
   - Check for command injection, path traversal, unsafe eval

2. **Maintenance health:**
   ```bash
   git -C {TARGET_PATH} log --oneline -20 2>/dev/null
   git -C {TARGET_PATH} log --format="%ai" -1 2>/dev/null  # last commit date
   git -C {TARGET_PATH} shortlog -sn 2>/dev/null            # contributor count
   ```

3. **Dependency weight:**
   - Count direct and transitive dependencies
   - Check for version pinning
   - Identify ecosystem lock-in (single-vendor, platform-specific)

4. **Adoption cost estimation:**
   - Files that need modification in our codebase
   - New dependencies to add
   - Configuration changes needed
   - Learning curve for team

## Output Format

Write your analysis to `{OUTPUT_FILE}` using this exact structure:

```markdown
# Risk & Adoption: {SKILL_NAME}

## Executive Summary
[2-3 sentences: key risks and recommended adoption approach]

## Risk Scorecard

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Security & Trust | X/5 | 30% | X.XX |
| Maintenance Signals | X/5 | 25% | X.XX |
| Dependency Weight | X/5 | 20% | X.XX |
| Adoption Cost | X/5 | 25% | X.XX |
| **Weighted Total** | | | **X.XX/5** |

## Security Findings

| Finding | Severity | Location | Mitigation |
|---------|----------|----------|------------|
| [issue] | Critical/High/Medium/Low | file:line | [fix] |

## Maintenance Health

| Signal | Value | Assessment |
|--------|-------|------------|
| Last commit | YYYY-MM-DD | Active/Stale/Abandoned |
| Contributors | N | Bus factor risk? |
| Release cadence | X/year | Regular/Sporadic/None |
| Open issues | N | Healthy/Concerning |
| Breaking changes | Y/N | Stability risk |

## Dependency Analysis

| Dependency | Version | Risk | Notes |
|------------|---------|------|-------|
| [dep name] | ^X.Y.Z | Low/Med/High | [concern] |

**Total direct deps:** N
**Total transitive deps:** ~N (estimate)

## Adoption Strategies

### Strategy A: Adopt As-Is

Full integration — install the component as a first-class part of the ecosystem.

**Steps:**
1. [Specific integration step]
2. [Specific integration step]
3. [Specific integration step]

| Metric | Rating |
|--------|--------|
| Effort | Low / Medium / High |
| Risk | Low / Medium / High |
| Value | Low / Medium / High |

**When to choose:** [conditions that favor this approach]

### Strategy B: Extract Components

Cherry-pick specific valuable pieces rather than adopting the whole thing.

**Extract:**
- [Specific file/pattern]: [why it's valuable]
- [Specific file/pattern]: [why it's valuable]

**Place in:**
- [Where in our ecosystem each piece goes]

| Metric | Rating |
|--------|--------|
| Effort | Low / Medium / High |
| Risk | Low / Medium / High |
| Value | Low / Medium / High |

**When to choose:** [conditions that favor this approach]

### Strategy C: Adapt Patterns

Learn from the approach without importing code — use ideas and patterns.

**Patterns to adopt:**
- [Pattern 1]: [how to apply in our ecosystem]
- [Pattern 2]: [how to apply in our ecosystem]

| Metric | Rating |
|--------|--------|
| Effort | Low / Medium / High |
| Risk | Low / Medium / High |
| Value | Low / Medium / High |

**When to choose:** [conditions that favor this approach]

## Recommendation

[Which strategy and why, considering the user's intended use case]
```

## Instructions

1. Read ALL files in the target directory
2. Run the git commands listed above for maintenance signals
3. Actually check for security issues — don't just say "no issues found" without looking
4. Make adoption strategies concrete and actionable, not generic
5. Tailor the recommendation to practical adoption, not theoretical best practices
6. Write the report to the specified output file
