# Multi-Model Orchestration

Quick reference for delegating tasks across Gemini, Codex, and Opus.

## Model Selection

| I need to... | Use | Why |
|--------------|-----|-----|
| Explore large codebase | Gemini Flash | 1M context, fast |
| Understand architecture | Gemini Pro | Deep reasoning |
| Implement feature | Codex | SWE-bench leader |
| Write/refactor code | Codex | Best at code changes |
| Coordinate & decide | Opus (self) | User interaction |

## Output Locations

```
docs/
├── exploration/           # Gemini outputs
│   └── {task-name}.md
└── implementation/        # Codex outputs
    └── {task-name}-log.md
```

## Quick Workflow

1. **Explore**: Fork Gemini to analyze codebase area
2. **Read**: Check `docs/exploration/{topic}.md` (summary first)
3. **Decide**: Discuss with user, plan implementation
4. **Implement**: Fork Codex with exploration context
5. **Review**: Check `docs/implementation/{topic}-log.md`

## Command

```
/orchestrate "explore the authentication system"
/orchestrate "implement user profiles based on docs/exploration/profiles.md"
```

## Files

- `SKILL.md` - Full orchestration patterns and guidelines
- `prompts/exploration-task.md` - Gemini prompt template
- `prompts/implementation-task.md` - Codex prompt template
