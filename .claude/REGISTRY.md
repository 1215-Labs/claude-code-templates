# Claude Components Registry

Central index of all .claude components for quick discovery.

## Quick Lookup

| Task | Use |
|------|-----|
| New to project | `/onboarding` |
| Quick context | `/quick-prime` |
| Deep dive into area | `/deep-prime "area" "focus"` |
| Review code | `/code-review` or `code-reviewer` agent |
| Debug issue | `/rca "error"` or `debugger` agent |
| Sync with reference | `/sync-reference` |
| Check types | `type-checker` agent |
| Map dependencies | `dependency-analyzer` agent |
| Find patterns | `codebase-analyst` agent |
| Create tests | `test-automator` agent |
| n8n workflows | n8n-* skills |

## By Category

### Analysis & Exploration
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `codebase-analyst` | Pattern discovery, conventions |
| Agent | `dependency-analyzer` | Map code dependencies |
| Agent | `lsp-navigator` | LSP-based navigation |
| Agent | `context-manager` | Track context across sessions |
| Command | `/quick-prime` | Fast 4-point context |
| Command | `/deep-prime` | Deep area analysis |
| Command | `/sync-reference` | Compare against claude-code reference |
| Skill | `lsp-symbol-navigation` | Symbol lookup patterns |
| Skill | `lsp-dependency-analysis` | Dependency mapping |

### Code Quality
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `code-reviewer` | Quality, security review |
| Agent | `type-checker` | Type safety verification |
| Agent | `test-automator` | Test creation |
| Command | `/code-review` | Comprehensive review + report |
| Command | `/ui-review` | UI consistency check |
| Skill | `lsp-type-safety-check` | Type validation patterns |
| Hook | `lsp-type-validator` | Pre-commit type check |

### Debugging
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `debugger` | Root cause analysis |
| Command | `/rca` | Error investigation |
| Hook | `lsp-reference-checker` | Reference impact warning |

### Session Management
| Type | Component | Purpose |
|------|-----------|---------|
| Hook | `session-init` | Initialize session context |

### Onboarding
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/onboarding` | Full interactive intro |
| Command | `/quick-prime` | Quick refresher |
| Command | `/deep-prime` | Before working on area |

### n8n Development
| Type | Component | Purpose |
|------|-----------|---------|
| Skill | `n8n-code-javascript` | JS in Code nodes |
| Skill | `n8n-code-python` | Python in Code nodes |
| Skill | `n8n-expression-syntax` | Expression patterns |
| Skill | `n8n-mcp-tools-expert` | MCP tool usage |
| Skill | `n8n-node-configuration` | Node setup |
| Skill | `n8n-validation-expert` | Validation errors |
| Skill | `n8n-workflow-patterns` | Workflow architecture |
| Agent | `n8n-mcp-tester` | n8n MCP testing |

### Research
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `library-researcher` | External library docs |
| Agent | `technical-researcher` | Technical research |

### Infrastructure
| Type | Component | Purpose |
|------|-----------|---------|
| Agent | `deployment-engineer` | CI/CD, containerization |
| Agent | `mcp-backend-engineer` | MCP implementation |

## Workflow Chains

Multi-step workflows for complex tasks:

| Workflow | Start | Purpose |
|----------|-------|---------|
| [feature-development](workflows/feature-development.md) | `/onboarding` | End-to-end feature implementation |
| [bug-investigation](workflows/bug-investigation.md) | `/rca` | Systematic debugging |
| [code-quality](workflows/code-quality.md) | `/code-review` | Pre-merge validation |
| [new-developer](workflows/new-developer.md) | `/onboarding` | Onboarding progression |

### PRP (Prompt Request Protocol)
| Type | Component | Purpose |
|------|-----------|---------|
| Command | `/prp-any-cli-create` | Create PRP for any CLI agent |
| Command | `/prp-any-cli-execute` | Execute PRP with any CLI agent |
| Command | `/prp-claude-code-create` | Create PRP for Claude Code |
| Command | `/prp-claude-code-execute` | Execute PRP with Claude Code |
| Command | `/prp-story-task-create` | Create PRP from user story/task |
| Command | `/prp-story-task-execute` | Execute story-based PRP |

## Component Counts

| Type | Count | Location |
|------|-------|----------|
| Agents | 13 | `.claude/agents/` |
| Commands | 16 | `.claude/commands/` |
| Skills | 11 | `.claude/skills/` |
| Rules | 1 | `.claude/rules/` |
| Hooks | 3 | `.claude/hooks/` |
| Workflows | 4 | `.claude/workflows/` |

## Cross-Reference Map

```
codebase-analyst ←→ /deep-prime ←→ lsp-navigator
       ↓                              ↓
code-reviewer ←→ /code-review ←→ type-checker
       ↓                              ↓
test-automator ←----------------→ lsp-type-validator

debugger ←→ /rca ←→ lsp-reference-checker
```
