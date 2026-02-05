# Purpose

Create a new Codex CLI agent to execute the command.

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

## Installed Codex Skills

Reference these in prompts to leverage Codex's installed capabilities:

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

## Instructions

- Before executing the command, run `codex --help` to understand the command and its options.
- Always use interactive mode (so leave off -p and use positional prompt if needed)
- For the -m (model) argument, use the DEFAULT_MODEL if not specified. If 'fast' is requested, use the FAST_MODEL. If 'heavy' is requested, use the HEAVY_MODEL.
- Always run with `--dangerously-bypass-approvals-and-sandbox`
