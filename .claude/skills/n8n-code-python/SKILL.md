---
name: n8n-code-python
description: Write Python in n8n Code nodes with _input/_json syntax and standard library.
version: 1.2.0
category: n8n
user-invocable: true
related:
  skills: [n8n-code-javascript, n8n-expression-syntax, n8n-validation-expert]
  agents: [n8n-mcp-tester]
---

# Python Code Node (Beta)

Expert guidance for writing Python code in n8n Code nodes.

> **Recommendation**: Use JavaScript for 95% of cases. Python only when you need specific stdlib functions or prefer Python syntax.

## Essential Rules

| Rule | Details |
|------|---------|
| **Mode** | Use "Run Once for All Items" (95% of cases) |
| **Data Access** | `_input.all()`, `_input.first()`, or `_input.item` |
| **Return Format** | Must return `[{"json": {...}}]` list |
| **Webhook Data** | Access via `_json["body"]["field"]` (NOT `_json["field"]`) |
| **Libraries** | Standard library ONLY (no requests, pandas, numpy) |

## Quick Start

```python
items = _input.all()

return [
    {"json": {**item["json"], "processed": True}}
    for item in items
]
```

## Standard Library Available

```python
import json          # JSON parsing
import datetime      # Date/time ops
import re            # Regular expressions
import base64        # Encoding
import hashlib       # Hashing
import urllib.parse  # URL parsing
import math          # Math functions
import random        # Random numbers
import statistics    # Stats (mean, median, stdev)
```

**NOT available**: requests, pandas, numpy, scipy, BeautifulSoup, lxml

## Data Access Patterns

```python
# _input.all() - Most common (arrays, batch ops)
all_items = _input.all()
valid = [item for item in all_items if item["json"].get("status") == "active"]

# _input.first() - Single object, API response
data = _input.first()["json"]

# _input.item - Each Item mode only
current = _input.item["json"]

# _node - Reference other nodes
webhook_data = _node["Webhook"]["json"]
http_data = _node["HTTP Request"]["json"]
```

See [DATA_ACCESS.md](DATA_ACCESS.md) for complete patterns.

## Webhook Data (Critical)

Webhook data is nested under `["body"]` - most common mistake:

```python
# ❌ WRONG                    # ✅ CORRECT
_json["name"]                 _json["body"]["name"]
_json["email"]                _json["body"]["email"]

# Safe access with .get()
name = _json.get("body", {}).get("name", "Unknown")
```

## Return Format (Critical)

Always return `[{"json": {...}}]` list format:

```python
# ✅ Single result
return [{"json": {"field1": value1}}]

# ✅ Multiple results (list comprehension)
return [{"json": {**item["json"], "processed": True}} for item in items]

# ✅ Empty result
return []

# ❌ WRONG formats
return {"json": {...}}        # Missing list wrapper
return [{"field": value}]     # Missing "json" key
```

See [ERROR_PATTERNS.md](ERROR_PATTERNS.md) for common mistakes.

## Common Patterns

```python
# Aggregation
items = _input.all()
total = sum(item["json"].get("amount", 0) for item in items)
return [{"json": {"total": total, "count": len(items)}}]

# Filtering with list comprehension
valid = [
    {"json": item["json"]}
    for item in _input.all()
    if item["json"].get("status") == "active"
]
return valid

# Regex extraction
import re
emails = re.findall(r'\b[\w.+-]+@[\w.-]+\.\w+\b', text)
return [{"json": {"emails": list(set(emails))}}]

# Statistics
from statistics import mean, median
values = [item["json"]["value"] for item in _input.all()]
return [{"json": {"mean": mean(values), "median": median(values)}}]
```

See [COMMON_PATTERNS.md](COMMON_PATTERNS.md) for 10 production patterns.

## Top 5 Mistakes

| Mistake | Wrong | Correct |
|---------|-------|---------|
| External imports | `import requests` | Use HTTP Request node |
| Missing return | `x = process()` | `return [{"json": x}]` |
| Dict instead of list | `return {"json": {...}}` | `return [{"json": {...}}]` |
| KeyError | `_json["user"]["email"]` | `_json.get("user", {}).get("email")` |
| Webhook direct access | `_json["email"]` | `_json["body"]["email"]` |

See [ERROR_PATTERNS.md](ERROR_PATTERNS.md) for solutions.

## Python vs JavaScript

| Use Python | Use JavaScript |
|------------|----------------|
| Need `statistics` module | Need HTTP requests (`$helpers`) |
| Prefer list comprehensions | Need `DateTime` (Luxon) |
| Specific stdlib functions | Better n8n integration |
| | **95% of use cases** |

## Best Practices

1. **Always use `.get()`**: Avoid KeyError with `item["json"].get("field", default)`
2. **Handle None explicitly**: `value = item.get("field") or 0`
3. **Use list comprehensions**: More Pythonic and readable
4. **Import at top**: Place imports at the beginning of code

## Pre-Deploy Checklist

- [ ] No external library imports (stdlib only)
- [ ] Return statement exists with `[{"json": {...}}]` format
- [ ] Data access uses `_input.all()`, `_input.first()`, or `_input.item`
- [ ] Safe dict access with `.get()` methods
- [ ] Webhook data accessed via `["body"]`

## Related Files

- [DATA_ACCESS.md](DATA_ACCESS.md) - Data access patterns
- [COMMON_PATTERNS.md](COMMON_PATTERNS.md) - Production patterns
- [ERROR_PATTERNS.md](ERROR_PATTERNS.md) - Error solutions
- [STANDARD_LIBRARY.md](STANDARD_LIBRARY.md) - Available modules
