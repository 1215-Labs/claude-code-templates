---
name: n8n-node-configuration
description: Configure n8n nodes with operation-aware property dependencies and required fields.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-mcp-tools-expert, n8n-validation-expert]
  agents: [n8n-mcp-tester]
---

# n8n Node Configuration

Expert guidance for operation-aware node configuration with property dependencies.

## Core Concepts

### 1. Operation-Aware Configuration

**Different operations need different fields!**

```javascript
// Slack: Post message
{resource: "message", operation: "post", channel: "#general", text: "Hello!"}

// Slack: Update message (different required fields!)
{resource: "message", operation: "update", messageId: "123", text: "Updated!"}
```

### 2. Property Dependencies

**Fields appear/disappear based on other field values:**

```javascript
// HTTP Request: GET (no body)
{method: "GET", url: "https://api.example.com"}

// HTTP Request: POST (sendBody → body required)
{method: "POST", url: "...", sendBody: true, body: {contentType: "json", content: {...}}}
```

## Configuration Workflow

```
1. get_node({nodeType: "..."})        → See requirements (standard detail)
2. Configure required fields          → Start minimal
3. validate_node({..., profile: "runtime"})  → Check config
4. Fix errors → Validate again        → Iterate (2-3 cycles normal)
5. Deploy                             → When valid
```

## get_node Detail Levels

| Level | Use When | Tokens |
|-------|----------|--------|
| `standard` (default) | **Starting configuration** (95% of cases) | 1-2K |
| `search_properties` mode | Looking for specific field | varies |
| `full` | Need complete schema | 3-8K |

```javascript
// Start here (default)
get_node({nodeType: "nodes-base.slack"})

// Find specific property
get_node({nodeType: "nodes-base.httpRequest", mode: "search_properties", propertyQuery: "auth"})

// Only if standard isn't enough
get_node({nodeType: "nodes-base.slack", detail: "full"})
```

## Common Node Patterns

### Resource/Operation Nodes (Slack, Google Sheets, Airtable)

```javascript
{
  resource: "<entity>",      // What type of thing
  operation: "<action>",     // What to do with it
  // ... operation-specific fields
}
```

### HTTP-Based Nodes (HTTP Request, Webhook)

```javascript
{
  method: "POST",
  url: "https://...",
  authentication: "none",
  sendBody: true,            // Required for POST/PUT/PATCH
  body: {...}                // Required when sendBody=true
}
```

### Conditional Nodes (IF, Switch)

```javascript
{
  conditions: {
    string: [{
      value1: "={{$json.status}}",
      operation: "equals",
      value2: "active"       // Binary operators need value2
    }]
  }
}
// Unary operators (isEmpty) → singleValue: true (auto-added)
```

## Example: HTTP Request Configuration

```javascript
// Step 1: Minimal config
{method: "POST", url: "...", authentication: "none"}

// Step 2: Validate → Error: "sendBody required for POST"
{method: "POST", url: "...", authentication: "none", sendBody: true}

// Step 3: Validate → Error: "body required when sendBody=true"
{method: "POST", url: "...", authentication: "none", sendBody: true,
 body: {contentType: "json", content: {...}}}

// Step 4: Valid! ✅
```

## Property Dependency Patterns

| Pattern | Example |
|---------|---------|
| **Boolean toggle** | `sendBody: true` → shows body field |
| **Operation switch** | `operation: "post"` → shows channel, text |
| **Type selection** | `type: "string"` → shows string operators |

## Best Practices

1. **Start with standard detail** (default) - covers 95% of cases
2. **Configure iteratively** - validate after each change
3. **Use search_properties mode** - when stuck on specific field
4. **Respect operation context** - different operations = different fields
5. **Trust auto-sanitization** - handles operator structure automatically

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Jump to `detail: "full"` | Try `standard` first |
| Configure without validation | Validate after each change |
| Same config for all operations | Check requirements per operation |
| Manually fix singleValue | Let auto-sanitization handle it |

## Related Files

- [DEPENDENCIES.md](DEPENDENCIES.md) - Property dependency deep dive
- [OPERATION_PATTERNS.md](OPERATION_PATTERNS.md) - Configuration patterns by node type
