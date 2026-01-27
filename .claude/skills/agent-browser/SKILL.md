---
name: agent-browser
description: This skill should be used when the user asks to "automate a browser", "scrape a website", "fill out a form", "click a button on a page", "test UI interactions", "take a screenshot of a webpage", "extract data from a website", "use agent-browser", or needs headless browser automation. Provides guidance for using the Vercel agent-browser CLI tool.
version: 1.0.0
category: browser-automation
user-invocable: true
related:
  skills:
    - fork-terminal
  agents:
    - test-automator
---

# Agent Browser Automation

Guidance for using Vercel's `agent-browser` CLI tool for headless browser automation. This tool is designed specifically for AI agents, providing a fast Rust CLI with accessibility-tree-based navigation.

## Prerequisites

Before using agent-browser, verify installation:

```bash
# Check if installed
agent-browser --version

# If not installed:
npm install -g agent-browser
agent-browser install  # Downloads Chromium

# On Linux, also run:
agent-browser install --with-deps
```

## When to Use

- **Testing your own sites** - no Cloudflare blocking, full control
- **Public website scraping** - data extraction from accessible sites
- **Form automation** - filling and submitting forms
- **Screenshot documentation** - capturing page states
- **Accessibility auditing** - snapshot reveals a11y tree issues

## When NOT to Use

- **Cloudflare-protected sites** - will be blocked (use Playwright MCP instead)
- **Sites requiring login persistence** - no session management between runs
- **Multi-tab complex workflows** - use Playwright MCP for advanced scenarios
- **Existing authenticated sessions** - can't attach to running browser

## Core Workflow

The recommended workflow for AI agents uses **snapshot-based navigation**:

1. **Open URL**: `agent-browser open <url>`
2. **Get snapshot**: `agent-browser snapshot` - Returns accessibility tree with refs (@e1, @e2, etc.)
3. **Interact via refs**: `agent-browser click @e3` or `agent-browser fill @e5 "text"`
4. **Repeat** snapshot → interact as needed
5. **Close**: `agent-browser close`

### Why Snapshot-Based Navigation

The `snapshot` command returns an accessibility tree where each interactive element has a ref like `@e1`, `@e2`. This approach:

- Avoids brittle CSS selectors
- Works with dynamic content
- Provides semantic element descriptions
- Designed for AI agent comprehension

## Essential Commands

### Navigation & State

| Command | Purpose |
|---------|---------|
| `agent-browser open <url>` | Navigate to URL |
| `agent-browser snapshot` | Get accessibility tree with refs |
| `agent-browser screenshot [path]` | Capture screenshot |
| `agent-browser get url` | Get current URL |
| `agent-browser get title` | Get page title |
| `agent-browser close` | Close browser |

### Interaction

| Command | Purpose |
|---------|---------|
| `agent-browser click @ref` | Click element |
| `agent-browser fill @ref "text"` | Clear and fill input |
| `agent-browser type @ref "text"` | Type without clearing |
| `agent-browser press Enter` | Press key |
| `agent-browser select @ref "value"` | Select dropdown option |
| `agent-browser check @ref` | Check checkbox |
| `agent-browser scroll down 500` | Scroll page |

### Data Extraction

| Command | Purpose |
|---------|---------|
| `agent-browser get text @ref` | Get element text |
| `agent-browser get html @ref` | Get element HTML |
| `agent-browser get value @ref` | Get input value |
| `agent-browser get attr @ref href` | Get attribute |
| `agent-browser eval "document.title"` | Run JavaScript |

### Waiting

| Command | Purpose |
|---------|---------|
| `agent-browser wait @ref` | Wait for element visible |
| `agent-browser wait 2000` | Wait milliseconds |
| `agent-browser wait --text "Welcome"` | Wait for text |
| `agent-browser wait --load networkidle` | Wait for network idle |

## Common Patterns

### Form Submission

```bash
agent-browser open "https://example.com/form"
agent-browser snapshot
# Identify form fields from snapshot output
agent-browser fill @e3 "user@example.com"
agent-browser fill @e5 "password123"
agent-browser click @e7  # Submit button
agent-browser wait --load networkidle
agent-browser snapshot  # Check result
```

### Data Extraction

```bash
agent-browser open "https://example.com/data"
agent-browser wait --load networkidle
agent-browser snapshot
# Identify data elements from snapshot
agent-browser get text @e12
agent-browser get text @e15
```

### Screenshot Documentation

```bash
agent-browser open "https://example.com"
agent-browser wait --load networkidle
agent-browser screenshot page.png
agent-browser screenshot --full fullpage.png  # Full page
```

### Multi-Page Navigation

```bash
agent-browser open "https://example.com"
agent-browser snapshot
agent-browser click @e5  # Navigation link
agent-browser wait --load networkidle
agent-browser snapshot  # New page content
```

## Best Practices

### Always Use Snapshots

After any navigation or interaction that changes the page, run `snapshot` again to get updated refs. Refs are invalidated when page content changes.

### Handle Dynamic Content

For SPAs and dynamic pages:
```bash
agent-browser wait --load networkidle
agent-browser snapshot
```

### Error Recovery

If an interaction fails, take a screenshot for debugging:
```bash
agent-browser screenshot debug.png
```

### Clean Up

Always close the browser when done:
```bash
agent-browser close
```

## Traditional Selectors

While refs are preferred, CSS selectors also work:

```bash
agent-browser click "#submit-button"
agent-browser fill "input[name='email']" "user@example.com"
```

### Semantic Locators

Find elements by semantic properties:

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "test@example.com"
```

## Additional Resources

### Reference Files

For complete command documentation:
- **`references/commands.md`** - Full command reference with all options

### Example Files

Working automation examples:
- **`examples/common-workflows.sh`** - Common automation patterns

## agent-browser vs Playwright MCP

When to use each tool:

### agent-browser Advantages

- **AI-optimized output** - `snapshot` returns an accessibility tree with refs (`@e1`, `@e2`) designed for LLM comprehension
- **Simpler mental model** - snapshot → interact → snapshot loop
- **Fast** - Rust CLI with minimal overhead
- **Semantic navigation** - refs avoid brittle CSS selectors

### agent-browser Disadvantages

- **Cloudflare blocks it** - Can't automate many SaaS sites
- **No session persistence** - Cookies/auth don't carry between runs
- **Headless only** - Can't attach to your existing browser

### Playwright MCP Advantages

- **Can use existing browser sessions** - Attach to your authenticated Chrome/Firefox
- **Bypasses Cloudflare** - If you're already logged in manually
- **Full Playwright power** - Network interception, multiple contexts, traces
- **Session persistence** - Can maintain auth state

### Playwright MCP Disadvantages

- **Verbose output** - Not optimized for LLM token efficiency
- **More complex** - Full browser automation API

### Decision Guide

| Scenario | Recommended Tool |
|----------|------------------|
| **Testing your own sites** | **agent-browser** (ideal) |
| Public sites, scraping, forms | agent-browser |
| Cloudflare-protected sites | Playwright MCP |
| Sites requiring login | Playwright MCP (attach to authenticated session) |
| Quick screenshots/data extraction | agent-browser |
| Complex multi-tab workflows | Playwright MCP |

**Bottom line:** Use agent-browser for simple automation on public sites and testing your own apps. Use Playwright MCP when you hit Cloudflare or need authenticated sessions.

### Ideal Use Case: Validating Your Own Sites

agent-browser is perfect for testing sites you build because:
- No Cloudflare blocking (you control the site)
- Snapshot output verifies element accessibility and semantics
- Quick form validation, navigation testing, screenshot capture
- Accessibility tree from `snapshot` helps catch a11y issues - missing refs/roles indicate problems

```bash
# Test a local dev site
agent-browser open "http://localhost:3000"
agent-browser wait --load networkidle
agent-browser snapshot  # Verify page structure

# Test form submission
agent-browser fill @e5 "test@example.com"
agent-browser click @e8
agent-browser wait --text "Success"
agent-browser screenshot form-success.png

# Verify mobile responsive
agent-browser set device "iPhone 14"
agent-browser open "http://localhost:3000"
agent-browser screenshot mobile-view.png

agent-browser close
```

## Troubleshooting

**Element not found**: Run `snapshot` to see current page state and verify ref exists.

**Timeout errors**: Increase wait time or use `wait --load networkidle`.

**Browser not starting**: Run `agent-browser install` to ensure Chromium is downloaded.

**Linux dependencies**: Run `agent-browser install --with-deps` for system libraries.

**Cloudflare bot protection**: Sites with Cloudflare protection (e.g., ChatGPT, many SaaS apps) will block agent-browser's headless Chromium. The captcha checkbox renders in an iframe that isn't accessible via the accessibility tree. **Workaround**: Use Playwright MCP with an existing authenticated browser session instead, or use a service that handles captcha solving.

## Known Limitations

- **Cloudflare-protected sites**: Cannot automate sites behind Cloudflare bot detection (chatgpt.com, etc.)
- **Captcha iframes**: Captcha elements in iframes are not accessible via `snapshot`
- **Session persistence**: No built-in cookie/session management between runs
