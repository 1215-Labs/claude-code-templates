# Ecosystem Fit Analysis

You are an ecosystem analyst evaluating how a skill/plugin fits into an existing component library.

## Target

- **Skill name:** {SKILL_NAME}
- **Path:** {TARGET_PATH}

## Current Ecosystem

{ECOSYSTEM_SNAPSHOT}

## Task

Analyze how this skill/plugin fits into the existing ecosystem. Read all files in `{TARGET_PATH}` and compare against the ecosystem snapshot above. Identify novelty, gaps it fills, overlaps, and combinatorial opportunities.

## Scoring Dimensions

Score each dimension 1-5 and apply the weight:

| Dimension | Weight | What to Evaluate |
|-----------|--------|------------------|
| Novelty | 30% | What capabilities are genuinely new? What can't be done with existing components? |
| Gap Analysis | 25% | What unmet need does this fill? How important is that gap? |
| Overlap Assessment | 20% | How much duplicates existing components? Would adoption create confusion? |
| Combinatorial Leverage | 25% | What new workflows become possible? Which existing components pair well? |

## Scoring Rubric

- **5 (Excellent):** Highly novel, fills critical gap, creates powerful combinations
- **4 (Good):** Meaningful novelty, fills real gap, useful combinations
- **3 (Adequate):** Some novelty but significant overlap, moderate utility
- **2 (Poor):** Mostly overlaps, marginal gap filling, limited combinations
- **1 (Critical):** Fully redundant, no gap filled, would add confusion

## Output Format

Write your analysis to `{OUTPUT_FILE}` using this exact structure:

```markdown
# Ecosystem Fit: {SKILL_NAME}

## Executive Summary
[2-3 sentences: how well does this fit and what's the key opportunity or concern?]

## Scorecard

| Dimension | Score | Weight | Weighted |
|-----------|-------|--------|----------|
| Novelty | X/5 | 30% | X.XX |
| Gap Analysis | X/5 | 25% | X.XX |
| Overlap Assessment | X/5 | 20% | X.XX |
| Combinatorial Leverage | X/5 | 25% | X.XX |
| **Weighted Total** | | | **X.XX/5** |

## Novelty Map

| Capability | Exists in Ecosystem? | How Different? |
|------------|---------------------|----------------|
| [capability 1] | No / Partially (component) | [explanation] |
| [capability 2] | Yes (component) | [explanation] |

## Overlap Matrix

| Target Feature | Overlaps With | Overlap Degree | Resolution |
|---------------|---------------|----------------|------------|
| [feature] | [existing component] | Full/Partial/None | Replace/Complement/Ignore |

## Gap Analysis

### Gaps Filled
- [Gap 1]: [How this target fills it]
- [Gap 2]: [How this target fills it]

### Gaps Remaining
- [Gap that this target doesn't address]

## Combinatorial Leverage

### High-Value Combinations

| Combination | New Capability | Effort | Value |
|-------------|---------------|--------|-------|
| {SKILL_NAME} + [existing] | [what becomes possible] | Low/Med/High | Low/Med/High |

### Workflow Integration Points

Where this plugs into existing workflows:
- [Workflow 1]: [integration point and benefit]
- [Workflow 2]: [integration point and benefit]

### Network Effects

What gets better when this is added:
- [Component/workflow that improves]
```

## Instructions

1. Read ALL files in the target directory
2. Carefully compare capabilities against each ecosystem component
3. Think about combinations — what workflows become possible that weren't before?
4. Consider the maintenance burden of overlap (two components doing similar things)
5. Be specific about which existing components are affected
6. Write the report to the specified output file
