# Adoptions

Provenance tracking for components adopted from evaluated reference submodules.

- **Written by**: `/reference-distill`
- **Read by**: `/repo-equip`, `/repo-optimize` for propagation
- **Numbering**: Sequential ADO-NNN, never reuse
- **Statuses**: `adopted` | `deferred-to-prp` | `propagated` | `tested`

## Records

| ID | Component | Source | Target | Status | Propagated |
|----|-----------|--------|--------|--------|------------|
| ADO-001 | dangerous-command-blocker | hooks-mastery | `.claude/hooks/dangerous-command-blocker.py` | adopted (PRP, Codex 169s, 8/8) | — |
| ADO-002 | prompt-validator | hooks-mastery | `.claude/hooks/prompt-validator.py` | adopted (PRP, Codex 158s, 6/6) | — |
| ADO-003 | uv-hook-template | hooks-mastery | `.claude/skills/uv-hook-template/` | adopted (PRP, Codex 189s, 8/8) | — |
| ADO-004 | ruff-validator | hooks-mastery | `.claude/hooks/ruff-validator.py` | tested (E2B 5/5) | — |
| ADO-005 | ty-validator | hooks-mastery | `.claude/hooks/ty-validator.py` | tested (E2B 5/5) | — |
| ADO-006 | status-line-context | hooks-mastery | `.claude/hooks/status-line-context.py` | adopted (PRP, Codex 157s, 7/7) | — |
| ADO-007 | meta-agent | hooks-mastery | `.claude/agents/meta-agent.md` | tested (E2B 2/2) | — |
| ADO-008 | team-builder | hooks-mastery | `.claude/agents/team-builder.md` | tested (E2B 2/2) | — |
| ADO-009 | team-validator | hooks-mastery | `.claude/agents/team-validator.md` | tested (E2B 3/3) | — |
| ADO-010 | agent-sandboxes | agent-sandbox-skill | `.claude/skills/agent-sandboxes/` | adopted (extracted, browser removed) | — |

All sourced from `references/` submodules. ADO-001–009 eval: hooks-mastery 3.50/5. ADO-010 eval: agent-sandbox-skill 4.10/5. All dated 2026-02-09.
