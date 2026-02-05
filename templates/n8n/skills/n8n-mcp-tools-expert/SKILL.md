---
name: n8n-mcp-tools-expert
description: Use n8n-mcp MCP tools for node search, validation, templates, and workflow management.
version: 1.2.0
category: n8n
user-invocable: true
allowed-tools:
  - mcp__n8n-mcp__*
related:
  skills: [n8n-node-configuration, n8n-validation-expert, n8n-workflow-patterns]
  agents: [n8n-mcp-tester]
---

# n8n MCP Tools Expert

Master guide for using n8n-mcp MCP server tools to build workflows.

## When to Use

- **Building n8n workflows programmatically** - create/update via MCP
- **Need to search nodes** - find nodes by keyword or capability
- **Validating configurations** - check before deployment
- **Deploying templates** - use pre-built workflow templates
- **Any n8n automation task** - this is the primary MCP interface

## When NOT to Use

- **Writing Code node logic** - use `n8n-code-javascript` or `n8n-code-python`
- **Expression syntax help** - use `n8n-expression-syntax`
- **Understanding node fields** - use `n8n-node-configuration` first
- **Choosing workflow architecture** - use `n8n-workflow-patterns` first
- **n8n not configured** - verify N8N_API_URL and N8N_API_KEY are set

## Quick Reference

| Tool | Use When | Speed |
|------|----------|-------|
| `search_nodes` | Finding nodes by keyword | <20ms |
| `get_node` | Understanding node config (default: standard detail) | <10ms |
| `validate_node` | Checking configurations | <100ms |
| `n8n_create_workflow` | Creating workflows | 100-500ms |
| `n8n_update_partial_workflow` | Editing workflows (most used!) | 50-200ms |
| `validate_workflow` | Checking complete workflow | 100-500ms |
| `n8n_deploy_template` | Deploy template to n8n | 200-500ms |

## Tool Selection Workflow

```
1. search_nodes({query: "slack"})     → Find nodes
2. get_node({nodeType: "nodes-base.slack"})  → Get config details
3. validate_node({nodeType, config, profile: "runtime"})  → Validate
4. n8n_create_workflow({...})         → Create workflow
5. n8n_validate_workflow({id})        → Verify
6. n8n_update_partial_workflow({...}) → Iterate (avg 56s between edits)
7. activateWorkflow operation         → Go live
```

## Critical: nodeType Formats

**Two different formats for different tools!**

| Tools | Format | Example |
|-------|--------|---------|
| search_nodes, get_node, validate_* | Short prefix | `nodes-base.slack` |
| n8n_create_workflow, n8n_update_* | Full prefix | `n8n-nodes-base.slack` |

```javascript
// search_nodes returns BOTH formats:
{
  "nodeType": "nodes-base.slack",           // For search/validate
  "workflowNodeType": "n8n-nodes-base.slack" // For workflow tools
}
```

## get_node Detail Levels

| Level | Tokens | Use When |
|-------|--------|----------|
| `standard` (default) | 1-2K | **95% of cases** - operations, properties |
| `minimal` | ~200 | Quick metadata lookup |
| `full` | 3-8K | Complete schema (use sparingly) |

```javascript
// Standard (recommended)
get_node({nodeType: "nodes-base.httpRequest"})

// Search for specific property
get_node({nodeType: "nodes-base.httpRequest", mode: "search_properties", propertyQuery: "auth"})

// Full documentation
get_node({nodeType: "nodes-base.webhook", mode: "docs"})
```

## Validation Profiles

| Profile | Use When |
|---------|----------|
| `runtime` (recommended) | Pre-deployment validation |
| `ai-friendly` | AI-generated configs (fewer false positives) |
| `minimal` | Quick checks during editing |
| `strict` | Production/critical workflows |

```javascript
validate_node({
  nodeType: "nodes-base.slack",
  config: {...},
  profile: "runtime"  // Always specify!
})
```

## Smart Parameters for Connections

```javascript
// IF node - use branch names
{type: "addConnection", source: "IF", target: "Handler", branch: "true"}
{type: "addConnection", source: "IF", target: "Handler", branch: "false"}

// Switch node - use case numbers
{type: "addConnection", source: "Switch", target: "Handler", case: 0}

// Include intent for better responses
n8n_update_partial_workflow({
  id: "abc",
  intent: "Add error handling for API failures",
  operations: [...]
})
```

## Template Usage

```javascript
// Search templates
search_templates({query: "webhook slack"})
search_templates({searchMode: "by_nodes", nodeTypes: ["n8n-nodes-base.slack"]})

// Deploy template directly
n8n_deploy_template({
  templateId: 2947,
  name: "My Weather to Slack",
  autoFix: true
})
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `get_node({nodeType: "slack"})` | Add prefix: `nodes-base.slack` |
| `get_node({nodeType: "n8n-nodes-base.slack"})` | Use short: `nodes-base.slack` |
| `get_node({detail: "full"})` | Use `standard` (default) unless needed |
| No validation profile | Specify `profile: "runtime"` |
| One-shot workflow build | Iterate! (avg 56s between edits) |

## Auto-Sanitization

Runs automatically on ANY workflow update:
- Binary operators (equals, contains) → removes singleValue
- Unary operators (isEmpty) → adds singleValue: true
- IF/Switch nodes → adds required metadata

**Cannot fix**: Broken connections, branch mismatches

## Tool Availability

**Always available** (no n8n API needed):
- search_nodes, get_node, validate_*
- search_templates, get_template
- tools_documentation, ai_agents_guide

**Requires n8n API** (N8N_API_URL + N8N_API_KEY):
- n8n_create_workflow, n8n_update_partial_workflow
- n8n_validate_workflow, n8n_list_workflows
- n8n_deploy_template, n8n_test_workflow

## Best Practices

1. **Use standard detail** (default) - covers 95% of cases
2. **Specify validation profile** - `runtime` recommended
3. **Use smart parameters** - `branch`, `case` for clarity
4. **Include intent** - Better AI responses
5. **Iterate workflows** - 56s avg between edits
6. **Validate after changes** - Don't skip validation

## Related Guides

- [SEARCH_GUIDE.md](SEARCH_GUIDE.md) - Node discovery
- [VALIDATION_GUIDE.md](VALIDATION_GUIDE.md) - Configuration validation
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Workflow management
