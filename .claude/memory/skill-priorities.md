# Skill Priorities

## Always (invoke proactively every session)
- `/catchup` - Resume session with briefing (run first thing)
- `/repo-equip` - When the user mentions another repo or equipping

## Context-Triggered (invoke when topic matches)
- `/sync-reference` - When discussing reference repos or upstream changes
- `/deep-prime "area"` - When diving into a specific component type
- `/code-review` - Before committing or merging changes
- `/all_skills` - When the user asks what's available

## Available (use when explicitly relevant)
- `/remember "fact"` - When discovering reusable knowledge
- `/onboarding` - When the user is new to this repo
- `/rca "error"` - When diagnosing failures

## Repo Context
- **Primary domain**: Claude Code template library, plugin architecture
- **Key commands prefix**: `/workflow/*`
- **Context skill**: N/A (this IS the templates repo)
