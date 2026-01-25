---
name: new-developer
description: New developer onboarding workflow
trigger: New team member
---

# New Developer Workflow

Onboarding process for new team members.

## Workflow Sequence

```
Day 1:
1. /onboarding                     → Full interactive intro
         ↓
2. Choose focus area               → Select starting point
         ↓
3. Explore codebase                → Guided exploration

Week 1:
4. /deep-prime "area" "focus"      → Before first task
         ↓
5. First contribution              → Small change

Ongoing:
6. /quick-prime                    → As needed refresher
```

## Step Details

### Day 1: Full Onboarding

**Command**: `/onboarding`
- Project overview
- Tech stack introduction
- Architecture walkthrough
- Key files and patterns
- Development setup

### Day 1: Focus Area Selection
- Review project areas
- Select starting point
- Understand team structure

### Day 1: Codebase Exploration
- Navigate key directories
- Read important files
- Understand conventions

### Week 1: First Task

**Command**: `/deep-prime "area" "focus"`
- Example: `/deep-prime "frontend" "component patterns"`
- Deep understanding before coding
- Find similar examples

### Week 1: First Contribution
- Small, well-defined task
- Follow discovered patterns
- Get code reviewed

### Ongoing: Quick Refreshers

**Command**: `/quick-prime`
- 4-point summary anytime
- Before switching areas
- After time away

## Progression Timeline

| When | Activity | Command/Agent |
|------|----------|---------------|
| Day 1 | Full onboarding | `/onboarding` |
| Day 2-3 | Explore, read | `codebase-analyst` |
| Day 4-5 | First task prep | `/deep-prime` |
| Week 2+ | Contributing | `/quick-prime` as needed |

## Tips for Success

1. **Don't rush** - Take time to understand
2. **Ask questions** - Use `/rca` for confusion
3. **Follow patterns** - Use `codebase-analyst` to find them
4. **Get reviews** - Use `code-reviewer` before PRs

## Related Components

- **Agents**: codebase-analyst, context-manager
- **Commands**: /onboarding, /quick-prime, /deep-prime
