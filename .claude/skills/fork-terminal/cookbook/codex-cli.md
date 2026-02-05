# Purpose

Create a new Codex CLI agent to execute the command in non-interactive mode.

## Variables

DEFAULT_MODEL: gpt-5.2-codex
HEAVY_MODEL: gpt-5.2-codex
BASE_MODEL: gpt-5.2-codex
FAST_MODEL: gpt-5.1-codex-mini

## Codex Strengths

- Long-context understanding with native compaction
- State-of-the-art on SWE-Bench Pro (agentic coding)
- Reliable tool calling
- Best for: Implementation, refactoring, code changes, bug fixes

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

## Installed Codex Skills

The following skills are available when forking to Codex. Reference them in prompts
to leverage their capabilities (e.g., "use the /playwright skill to test the form").

| Skill | Purpose | Best For |
|-------|---------|----------|
| `/doc` | Documentation generation | READMEs, API docs, inline docs |
| `/gh-address-comments` | Address PR review comments | Resolving reviewer feedback |
| `/gh-fix-ci` | Fix CI failures | Debugging failed checks/actions |
| `/openai-docs` | Query OpenAI documentation | API usage, SDK patterns |
| `/pdf` | PDF processing | Reading/extracting PDF content |
| `/playwright` | Browser automation & testing | E2E tests, UI validation |
| `/screenshot` | Take screenshots | Visual verification, bug reports |
| `/security-best-practices` | Security review | Code audit, OWASP checks |
| `/security-ownership-map` | Map code ownership & security | Attack surface analysis |
| `/security-threat-model` | Threat modeling | Risk assessment, security design |

### Skill-Aware Prompt Examples

**Fix CI with skill:**
```bash
codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "Use /gh-fix-ci to diagnose and fix the failing GitHub Actions workflow"
```

**Security review with skill:**
```bash
codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "Use /security-best-practices to review src/auth/ for vulnerabilities"
```

**E2E testing with skill:**
```bash
codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "Use /playwright to write E2E tests for the login flow"
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
