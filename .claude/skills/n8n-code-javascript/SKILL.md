---
name: n8n-code-javascript
description: Write JavaScript in n8n Code nodes with $input/$json syntax, $helpers, and DateTime.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-expression-syntax, n8n-node-configuration, n8n-validation-expert]
  agents: [n8n-mcp-tester]
---

# JavaScript Code Node

Expert guidance for writing JavaScript code in n8n Code nodes.

## Essential Rules

| Rule | Details |
|------|---------|
| **Mode** | Use "Run Once for All Items" (95% of cases) |
| **Data Access** | `$input.all()`, `$input.first()`, or `$input.item` |
| **Return Format** | Must return `[{json: {...}}]` array |
| **Webhook Data** | Access via `$json.body.field` (NOT `$json.field`) |
| **Built-ins** | `$helpers.httpRequest()`, `DateTime` (Luxon), `$jmespath()` |

## Quick Start

```javascript
const items = $input.all();

return items.map(item => ({
  json: {
    ...item.json,
    processed: true,
    timestamp: new Date().toISOString()
  }
}));
```

## Mode Selection

| Mode | Use When | Data Access |
|------|----------|-------------|
| **Run Once for All Items** | Aggregation, filtering, batch ops (95% of cases) | `$input.all()` |
| **Run Once for Each Item** | Per-item API calls, independent validation | `$input.item` |

**Decision:** Need multiple items? → All Items. Each item independent? → Each Item. Unsure? → All Items.

## Data Access Patterns

```javascript
// $input.all() - Most common (arrays, batch ops)
const allItems = $input.all();
const valid = allItems.filter(item => item.json.status === 'active');

// $input.first() - Single object, API response
const data = $input.first().json;

// $input.item - Each Item mode only
const current = $input.item.json;

// $node - Reference other nodes
const webhookData = $node["Webhook"].json;
const httpData = $node["HTTP Request"].json;
```

See [DATA_ACCESS.md](DATA_ACCESS.md) for complete patterns.

## Webhook Data (Critical)

Webhook data is nested under `.body` - this is the most common mistake:

```javascript
// ❌ WRONG          // ✅ CORRECT
$json.name           $json.body.name
$json.email          $json.body.email
```

## Return Format (Critical)

Always return `[{json: {...}}]` array format:

```javascript
// ✅ Single result
return [{json: {field1: value1}}];

// ✅ Multiple results
return items.map(item => ({json: {...item.json, processed: true}}));

// ✅ Empty result
return [];

// ❌ WRONG formats
return {json: {...}};      // Missing array wrapper
return [{field: value}];   // Missing json key
return $input.all();       // Raw data without .map()
```

See [ERROR_PATTERNS.md](ERROR_PATTERNS.md) for common mistakes.

## Common Patterns

```javascript
// Aggregation
const total = $input.all().reduce((sum, item) => sum + (item.json.amount || 0), 0);
return [{json: {total, count: items.length}}];

// Filtering
const active = $input.all().filter(item => item.json.status === 'active');
return active.map(item => ({json: item.json}));

// Transformation
return $input.all().map(item => ({
  json: {
    ...item.json,
    processed_at: new Date().toISOString()
  }
}));

// Top N
const top10 = $input.all()
  .sort((a, b) => b.json.score - a.json.score)
  .slice(0, 10);
return top10.map(item => ({json: item.json}));
```

See [COMMON_PATTERNS.md](COMMON_PATTERNS.md) for 10 production patterns.

## Top 5 Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| Missing return | `const x = process();` | `return [{json: x}];` |
| Expression syntax in code | `"{{ $json.field }}"` | `$input.first().json.field` |
| Object instead of array | `return {json: {...}}` | `return [{json: {...}}]` |
| No null checks | `item.json.user.email` | `item.json?.user?.email \|\| ''` |
| Webhook direct access | `$json.email` | `$json.body.email` |

See [ERROR_PATTERNS.md](ERROR_PATTERNS.md) for solutions.

## Built-in Helpers

```javascript
// HTTP requests
const response = await $helpers.httpRequest({
  method: 'GET',
  url: 'https://api.example.com/data',
  headers: {'Authorization': 'Bearer token'}
});

// DateTime (Luxon)
const now = DateTime.now();
const formatted = now.toFormat('yyyy-MM-dd');
const tomorrow = now.plus({days: 1});

// JMESPath queries
const adults = $jmespath(data, 'users[?age >= `18`]');
const names = $jmespath(data, 'users[*].name');
```

See [BUILTIN_FUNCTIONS.md](BUILTIN_FUNCTIONS.md) for complete reference.

## Best Practices

1. **Validate input first**: Check `items.length > 0` before processing
2. **Use try-catch**: Wrap `$helpers.httpRequest()` and risky operations
3. **Prefer array methods**: `.filter().map()` over manual loops
4. **Filter early**: Reduce dataset before expensive transformations
5. **Use optional chaining**: `item.json?.user?.email` for safe access
6. **Debug with console.log**: Output appears in browser console

## When to Use Code Node

| Use Code Node | Use Other Nodes |
|--------------|-----------------|
| Complex transformations | Simple field mapping → **Set** |
| Custom business logic | Basic filtering → **Filter** |
| Data aggregation | Simple conditionals → **IF/Switch** |
| API response parsing | HTTP only → **HTTP Request** |

## Pre-Deploy Checklist

- [ ] Return statement exists with `[{json: {...}}]` format
- [ ] Data access uses `$input.all()`, `$input.first()`, or `$input.item`
- [ ] No `{{ }}` expressions (use JavaScript directly)
- [ ] Null checks for optional fields
- [ ] Webhook data accessed via `.body`

## Related Files

- [DATA_ACCESS.md](DATA_ACCESS.md) - Data access patterns
- [COMMON_PATTERNS.md](COMMON_PATTERNS.md) - Production patterns
- [ERROR_PATTERNS.md](ERROR_PATTERNS.md) - Error solutions
- [BUILTIN_FUNCTIONS.md](BUILTIN_FUNCTIONS.md) - Built-in reference
