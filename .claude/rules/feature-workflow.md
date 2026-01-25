---
description: "Feature development workflow"
globs: ["oh-my-opencode/src/**/*.ts", "docs/feature-tests/**/*"]
---

# Feature Workflow

| Step | Output | Location |
|------|--------|----------|
| 1. Baseline | BASELINE.md | `docs/feature-tests/NN-name/` |
| 2. Code | Implementation | `oh-my-opencode/src/` |
| 3. Test | SPEC.md + test.ts | `docs/feature-tests/NN-name/` |
| 4. Results | RESULTS.md (with delta) | Same folder |

**Baseline first:** Measure behavior WITHOUT the feature before building it.

Naming: `NN-feature-name` (01, 02, 03...)
Template: `docs/FEATURE_TEMPLATE_LITE.md`
