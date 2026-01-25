---
name: n8n-validation-expert
description: Interpret n8n validation errors, warnings, and profiles to fix workflow issues.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-mcp-tools-expert, n8n-node-configuration, n8n-expression-syntax]
  agents: [n8n-mcp-tester]
---

# n8n Validation Expert

Expert guide for interpreting and fixing n8n validation errors.

## Validation Philosophy

**Validation is iterative** - expect 2-3 cycles:
1. Configure → Validate (~23s thinking)
2. Fix errors → Validate (~58s fixing)
3. Repeat until valid

## Error Severity

| Level | Meaning | Action |
|-------|---------|--------|
| **Error** | Blocks workflow | Must fix before activation |
| **Warning** | Won't block | Should review, may be acceptable |
| **Suggestion** | Nice to have | Optional improvements |

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

## Common Error Types

| Type | Meaning | Fix |
|------|---------|-----|
| `missing_required` | Required field missing | Add the field |
| `invalid_value` | Value not in allowed options | Use valid option |
| `type_mismatch` | Wrong data type | Convert to correct type |
| `invalid_expression` | Expression syntax error | Fix expression (see n8n-expression-syntax) |
| `invalid_reference` | Referenced node doesn't exist | Check node name spelling |

## The Validation Loop

```javascript
// Iteration 1
const result = validate_node({nodeType: "nodes-base.slack", config: {resource: "channel", operation: "create"}, profile: "runtime"});
// → Error: Missing "name"

// Iteration 2
config.name = "general";
validate_node({...});
// → Error: Missing "text" (different operation needs different fields!)

// Iteration 3 (check correct operation requirements)
// → Valid! ✅
```

**This is normal!** Don't be discouraged by iterations.

## Auto-Sanitization

Runs automatically on ANY workflow update:

| What | Fix Applied |
|------|-------------|
| Binary operators (equals, contains) | Removes singleValue |
| Unary operators (isEmpty) | Adds singleValue: true |
| IF/Switch nodes | Adds required metadata |

**Cannot fix**: Broken connections, branch count mismatches, paradoxical states

## False Positives

Some warnings are acceptable in your context:

| Warning | When Acceptable |
|---------|-----------------|
| "Missing error handling" | Simple/test workflows |
| "No retry logic" | Idempotent operations |
| "Missing rate limiting" | Low-volume workflows |
| "Unbounded query" | Small known datasets |

Use `ai-friendly` profile for fewer false positives.

## Workflow Validation

`validate_workflow` checks entire workflow:
- Node configurations
- Connections (no broken refs)
- Expressions
- Flow structure

Common workflow errors:
- **Broken connections** → Use `cleanStaleConnections` operation
- **Circular dependencies** → Restructure workflow
- **Disconnected nodes** → Connect or remove

## Recovery Strategies

| Strategy | When |
|----------|------|
| **Start fresh** | Config severely broken |
| **Binary search** | Workflow validates but executes wrong |
| **cleanStaleConnections** | "Node not found" errors |
| **n8n_autofix_workflow** | Operator structure errors |

```javascript
// Preview fixes first
n8n_autofix_workflow({id: "...", applyFixes: false})

// Then apply
n8n_autofix_workflow({id: "...", applyFixes: true})
```

## Best Practices

1. **Validate after every change** - Don't batch changes
2. **Read errors completely** - They contain fix guidance
3. **Use runtime profile** - Balanced validation
4. **Fix one error at a time** - Easier to track
5. **Trust auto-sanitization** - Don't manually fix operator structure
6. **Check valid field first** - Before assuming success

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skip validation | Always validate before deployment |
| Use `strict` during dev | Too noisy, use `runtime` |
| Ignore all warnings | Some are important! |
| Batch multiple fixes | Fix one at a time |

## Related Files

- [ERROR_CATALOG.md](ERROR_CATALOG.md) - Complete error list
- [FALSE_POSITIVES.md](FALSE_POSITIVES.md) - When warnings are OK
