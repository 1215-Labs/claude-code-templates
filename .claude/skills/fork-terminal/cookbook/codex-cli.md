# Purpose

Create a new Codex CLI agent to execute the command in non-interactive mode.

## Variables

DEFAULT_MODEL: gpt-5.2-codex
HEAVY_MODEL: gpt-5.2-codex
BASE_MODEL: gpt-5.2-codex
FAST_MODEL: gpt-5.2-codex-mini

## Fallback Chain

If the primary model fails, try models in this order:
1. gpt-5.2-codex (default)
2. gpt-5.1-codex-max (fallback)
3. gpt-4o (emergency fallback)

## Instructions

- Use the `exec` subcommand for true non-interactive execution (not the default interactive mode)
- Always use `--full-auto` for automatic approvals with sandboxed execution
- Always use `--skip-git-repo-check` to avoid "not inside trusted directory" errors
- For the -m (model) argument, use DEFAULT_MODEL if not specified. If 'fast' is requested, use FAST_MODEL. If 'heavy' is requested, use HEAVY_MODEL.

## Command Template

```bash
codex exec --full-auto --skip-git-repo-check -m MODEL "PROMPT"
```

## Examples

**Basic execution:**
```bash
codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "analyze this codebase and summarize the architecture"
```

**With output logging:**
```bash
codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "PROMPT" 2>&1 | tee /tmp/fork_codex_$(date +%s).log
```

**With custom working directory:**
```bash
codex exec --full-auto --skip-git-repo-check -C /path/to/dir -m gpt-5.2-codex "PROMPT"
```

## Known Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Upgrade to gpt-5.2?" prompt | Use `exec` subcommand (non-interactive) |
| "Not inside trusted directory" | Add `--skip-git-repo-check` |
| Command hangs | Check if API key is valid, use timeout |
| Model not available | Fall back to next model in chain |

## Deprecated Flags

Do NOT use these deprecated patterns:
- `--dangerously-bypass-approvals-and-sandbox` - Use `--full-auto` instead
- Interactive mode without `exec` - Always use `codex exec` for forked terminals
