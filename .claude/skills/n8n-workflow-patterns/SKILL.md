---
name: n8n-workflow-patterns
description: Architectural patterns for n8n workflows - webhook, API, database, AI agent, scheduled.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-mcp-tools-expert, n8n-node-configuration, n8n-validation-expert]
  agents: [n8n-mcp-tester]
---

# n8n Workflow Patterns

Proven architectural patterns for building n8n workflows.

## The 5 Core Patterns

| Pattern | Use When | Structure |
|---------|----------|-----------|
| **[Webhook Processing](webhook_processing.md)** | Receiving external data | Webhook → Validate → Transform → Respond |
| **[HTTP API Integration](http_api_integration.md)** | Fetching from REST APIs | Trigger → HTTP Request → Transform → Action |
| **[Database Operations](database_operations.md)** | Read/Write/Sync data | Schedule → Query → Transform → Write |
| **[AI Agent Workflow](ai_agent_workflow.md)** | AI with tools/memory | Trigger → AI Agent (Model+Tools+Memory) → Output |
| **[Scheduled Tasks](scheduled_tasks.md)** | Recurring automation | Schedule → Fetch → Process → Deliver |

## Pattern Selection

| Use Case | Pattern |
|----------|---------|
| Form submissions, payment webhooks, chat integrations | Webhook Processing |
| Fetching external data, third-party sync | HTTP API Integration |
| ETL, data sync, backups | Database Operations |
| Chatbots, content generation, data analysis | AI Agent Workflow |
| Reports, maintenance, periodic fetching | Scheduled Tasks |

## Building Blocks

### Triggers
- **Webhook** - HTTP endpoint (instant)
- **Schedule** - Cron-based (periodic)
- **Manual** - Click to execute (testing)
- **Polling** - Check for changes

### Transformation
- **Set** - Field mapping
- **Code** - Complex logic
- **IF/Switch** - Conditional routing
- **Merge** - Combine streams

### Error Handling
- **Error Trigger** - Catch errors
- **Continue On Fail** - Per-node setting
- **Stop and Error** - Explicit failure

## Data Flow Patterns

```
Linear:      Trigger → Transform → Action

Branching:   Trigger → IF → [True Path]
                        └→ [False Path]

Parallel:    Trigger → [Branch 1] → Merge
                    └→ [Branch 2] ↗

Loop:        Trigger → Split in Batches → Process → (repeat)
```

## Common Gotchas

| Issue | Fix |
|-------|-----|
| Can't access webhook data | Use `$json.body.field` (not `$json.field`) |
| Wrong node execution order | Check Execution Order in settings (v1 recommended) |
| Expression shows as text | Add `{{ }}` around expressions |
| API calls failing 401/403 | Configure credentials properly |

## Quick Examples

```
# Webhook → Slack
1. Webhook (POST /form-submit)
2. Set (map fields)
3. Slack (post to #notifications)

# Scheduled Report
1. Schedule (daily 9 AM)
2. HTTP Request (fetch analytics)
3. Code (aggregate)
4. Email (send report)

# AI Assistant
1. Webhook (receive chat)
2. AI Agent + OpenAI Model + Tools + Memory
3. Webhook Response (send reply)
```

## Workflow Creation Checklist

**Planning:**
- [ ] Identify pattern (webhook/API/database/AI/scheduled)
- [ ] List required nodes (`search_nodes`)
- [ ] Plan error handling

**Implementation:**
- [ ] Create with appropriate trigger
- [ ] Configure authentication
- [ ] Add transformation nodes
- [ ] Add error handling

**Validation:**
- [ ] `validate_node` for each node
- [ ] `validate_workflow` for complete flow
- [ ] Test with sample data

**Deployment:**
- [ ] Activate with `activateWorkflow` operation
- [ ] Monitor first executions

## Best Practices

1. **Start simple** - Use simplest pattern that solves problem
2. **Plan first** - Design structure before building
3. **Iterate** - Don't build one-shot (avg 56s between edits)
4. **Validate always** - Don't skip before activation
5. **Handle errors** - Every workflow needs error handling
6. **Document** - Use notes field for complex workflows

## Related Files

- [webhook_processing.md](webhook_processing.md) - Webhook patterns
- [http_api_integration.md](http_api_integration.md) - REST API patterns
- [database_operations.md](database_operations.md) - Database patterns
- [ai_agent_workflow.md](ai_agent_workflow.md) - AI agent patterns
- [scheduled_tasks.md](scheduled_tasks.md) - Scheduled task patterns
