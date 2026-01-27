---
name: n8n-expression-syntax
description: Write n8n expressions with {{}} syntax, $json/$node variables, and webhook data access.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-code-javascript, n8n-validation-expert, n8n-workflow-patterns]
  agents: [n8n-mcp-tester]
---

# n8n Expression Syntax

Expert guide for writing correct n8n expressions in workflows.

## When to Use

- **Dynamic field values** - insert data from previous nodes
- **String interpolation in URLs** - `https://api.example.com/{{$json.id}}`
- **Conditional text** - ternary expressions in text fields
- **Date formatting** - `{{$now.toFormat('yyyy-MM-dd')}}`
- **Cross-node references** - `{{$node["Other Node"].json.field}}`

## When NOT to Use

- **Code nodes** - use direct JavaScript: `$json.field` (no `{{ }}`)
- **Webhook paths** - static paths only, no expressions
- **Credential fields** - use n8n credential system
- **Complex logic** - use Code node for multi-step operations

## Expression Format

All dynamic content uses **double curly braces**: `{{expression}}`

```javascript
✅ {{$json.email}}
✅ {{$json.body.name}}
✅ {{$node["HTTP Request"].json.data}}
❌ $json.email  (no braces - literal text)
❌ {$json.email}  (single braces - invalid)
```

## Core Variables

| Variable | Use | Example |
|----------|-----|---------|
| `$json` | Current node data | `{{$json.fieldName}}` |
| `$node` | Other node data | `{{$node["Node Name"].json.field}}` |
| `$now` | Current timestamp | `{{$now.toFormat('yyyy-MM-dd')}}` |
| `$env` | Environment vars | `{{$env.API_KEY}}` |

## Webhook Data (Critical)

**Most common mistake**: Webhook data is nested under `.body`!

```javascript
// Webhook node output structure:
{
  "headers": {...},
  "params": {...},
  "query": {...},
  "body": {           // ⚠️ USER DATA IS HERE
    "name": "John",
    "email": "john@example.com"
  }
}

// ❌ WRONG          ✅ CORRECT
{{$json.name}}       {{$json.body.name}}
{{$json.email}}      {{$json.body.email}}
```

## Common Patterns

```javascript
// Access nested fields
{{$json.user.email}}
{{$json.data[0].name}}
{{$json['field with spaces']}}

// Reference other nodes (quotes required!)
{{$node["HTTP Request"].json.data}}
{{$node["Webhook"].json.body.email}}

// In URLs
https://api.example.com/users/{{$json.body.user_id}}

// Date formatting
{{$now.toFormat('yyyy-MM-dd')}}
{{$now.plus({days: 7}).toISO()}}

// Conditionals
{{$json.status === 'active' ? 'Yes' : 'No'}}
{{$json.email || 'no-email@example.com'}}
```

## When NOT to Use Expressions

| Location | Use Instead |
|----------|-------------|
| **Code nodes** | Direct JavaScript: `$json.email` (no `{{ }}`) |
| **Webhook paths** | Static paths only |
| **Credential fields** | Use n8n credential system |

```javascript
// ❌ WRONG in Code node    ✅ CORRECT in Code node
'={{$json.email}}'          $json.email
'{{$json.body.name}}'       $input.first().json.body.name
```

## Validation Rules

| Rule | Wrong | Correct |
|------|-------|---------|
| Must use `{{ }}` | `$json.field` | `{{$json.field}}` |
| Quotes for spaces | `{{$json.field name}}` | `{{$json['field name']}}` |
| Node names in quotes | `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| Case-sensitive nodes | `{{$node["http request"]}}` | `{{$node["HTTP Request"]}}` |
| No nested `{{ }}` | `{{{$json.field}}}` | `{{$json.field}}` |

## Quick Fixes

| Mistake | Fix |
|---------|-----|
| `$json.field` | `{{$json.field}}` |
| `{{$json.name}}` (webhook) | `{{$json.body.name}}` |
| `{{$node.HTTP Request}}` | `{{$node["HTTP Request"]}}` |
| `'={{$json.email}}'` (Code) | `$json.email` |

## Expression Helpers

**String**: `.toLowerCase()`, `.toUpperCase()`, `.trim()`, `.replace()`, `.split()`
**Array**: `.length`, `.map()`, `.filter()`, `.find()`, `.join()`
**DateTime**: `.toFormat()`, `.toISO()`, `.plus()`, `.minus()`
**Number**: `.toFixed()`, math ops (`+`, `-`, `*`, `/`)

## Debugging

1. Click field with expression
2. Open expression editor (fx icon)
3. See live preview
4. Red highlights = errors

**Common errors**:
- "Cannot read property 'X' of undefined" → Check data path
- Expression shows as literal text → Missing `{{ }}`

## Related Files

- [COMMON_MISTAKES.md](COMMON_MISTAKES.md) - Complete error catalog
- [EXAMPLES.md](EXAMPLES.md) - Real workflow examples
