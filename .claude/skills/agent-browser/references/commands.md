# Agent Browser Command Reference

Complete reference for all agent-browser CLI commands.

## Core Commands

### Navigation

```bash
agent-browser open <url>              # Navigate to URL (aliases: goto, navigate)
agent-browser close                   # Close browser (aliases: quit, exit)
agent-browser connect <port>          # Connect to browser via CDP
```

### Snapshot & Screenshots

```bash
agent-browser snapshot                # Accessibility tree with refs (best for AI)
agent-browser screenshot [path]       # Take screenshot
agent-browser screenshot --full [path] # Full page screenshot
agent-browser pdf <path>              # Save page as PDF
```

## Interaction Commands

### Click & Focus

```bash
agent-browser click <sel>             # Click element
agent-browser dblclick <sel>          # Double-click element
agent-browser focus <sel>             # Focus element
agent-browser hover <sel>             # Hover element
```

### Text Input

```bash
agent-browser type <sel> <text>       # Type into element (appends)
agent-browser fill <sel> <text>       # Clear and fill (replaces)
agent-browser press <key>             # Press key (Enter, Tab, Control+a)
agent-browser keydown <key>           # Hold key down
agent-browser keyup <key>             # Release key
```

### Form Controls

```bash
agent-browser select <sel> <val>      # Select dropdown option
agent-browser check <sel>             # Check checkbox
agent-browser uncheck <sel>           # Uncheck checkbox
agent-browser upload <sel> <files>    # Upload files
```

### Scrolling

```bash
agent-browser scroll <dir> [px]       # Scroll (up/down/left/right)
agent-browser scrollintoview <sel>    # Scroll element into view
```

### Drag & Drop

```bash
agent-browser drag <src> <tgt>        # Drag and drop
```

## Get Information

### Element Content

```bash
agent-browser get text <sel>          # Get text content
agent-browser get html <sel>          # Get innerHTML
agent-browser get value <sel>         # Get input value
agent-browser get attr <sel> <attr>   # Get attribute
agent-browser get count <sel>         # Count matching elements
agent-browser get box <sel>           # Get bounding box
```

### Page Information

```bash
agent-browser get title               # Get page title
agent-browser get url                 # Get current URL
```

## Check State

```bash
agent-browser is visible <sel>        # Check if visible
agent-browser is enabled <sel>        # Check if enabled
agent-browser is checked <sel>        # Check if checked
```

## Find Elements (Semantic Locators)

### By Role

```bash
agent-browser find role <role> <action> [value]
# Examples:
agent-browser find role button click --name "Submit"
agent-browser find role textbox fill "test@example.com"
agent-browser find role link click --name "Home"
```

### By Content

```bash
agent-browser find text <text> <action>
agent-browser find label <label> <action> [value]
agent-browser find placeholder <ph> <action> [value]
agent-browser find alt <text> <action>
agent-browser find title <text> <action>
agent-browser find testid <id> <action> [value]
```

### By Position

```bash
agent-browser find first <sel> <action> [value]
agent-browser find last <sel> <action> [value]
agent-browser find nth <n> <sel> <action> [value]
```

**Available actions:** `click`, `fill`, `check`, `hover`, `text`

## Wait Commands

```bash
agent-browser wait <selector>         # Wait for element visible
agent-browser wait <ms>               # Wait milliseconds
agent-browser wait --text "Welcome"   # Wait for text to appear
agent-browser wait --url "**/dash"    # Wait for URL pattern
agent-browser wait --load networkidle # Wait for load state
agent-browser wait --fn "window.ready === true"  # Wait for JS condition
```

**Load states:** `load`, `domcontentloaded`, `networkidle`

## Mouse Control

```bash
agent-browser mouse move <x> <y>      # Move mouse to coordinates
agent-browser mouse down [button]     # Press button (left/right/middle)
agent-browser mouse up [button]       # Release button
agent-browser mouse wheel <dy> [dx]   # Scroll wheel
```

## Browser Settings

```bash
agent-browser set viewport <w> <h>    # Set viewport size
agent-browser set device <name>       # Emulate device ("iPhone 14")
agent-browser set geo <lat> <lng>     # Set geolocation
agent-browser set offline [on|off]    # Toggle offline mode
agent-browser set headers <json>      # Extra HTTP headers
agent-browser set credentials <u> <p> # HTTP basic auth
agent-browser set media [dark|light]  # Emulate color scheme
```

## Cookies & Storage

### Cookies

```bash
agent-browser cookies                 # Get all cookies
agent-browser cookies set <name> <val> # Set cookie
agent-browser cookies clear           # Clear cookies
```

### Local Storage

```bash
agent-browser storage local           # Get all localStorage
agent-browser storage local <key>     # Get specific key
agent-browser storage local set <k> <v>  # Set value
agent-browser storage local clear     # Clear all
```

### Session Storage

```bash
agent-browser storage session         # Get all sessionStorage
agent-browser storage session <key>   # Get specific key
agent-browser storage session set <k> <v>  # Set value
agent-browser storage session clear   # Clear all
```

## Network Control

```bash
agent-browser network route <url>              # Intercept requests
agent-browser network route <url> --abort      # Block requests
agent-browser network route <url> --body <json>  # Mock response
agent-browser network unroute [url]            # Remove routes
agent-browser network requests                 # View tracked requests
agent-browser network requests --filter api    # Filter requests
```

## Tabs & Windows

```bash
agent-browser tab                     # List tabs
agent-browser tab new [url]           # New tab (optionally with URL)
agent-browser tab <n>                 # Switch to tab n
agent-browser tab close [n]           # Close tab
agent-browser window new              # New window
```

## JavaScript Execution

```bash
agent-browser eval <js>               # Run JavaScript and return result
# Examples:
agent-browser eval "document.title"
agent-browser eval "document.querySelectorAll('a').length"
agent-browser eval "window.scrollY"
```

## Selector Types

### Ref Selectors (Recommended)

From `snapshot` output, use refs directly:
```bash
agent-browser click @e1
agent-browser fill @e5 "text"
```

### CSS Selectors

```bash
agent-browser click "#submit"
agent-browser fill ".email-input" "test@example.com"
agent-browser click "button[type='submit']"
```

### XPath (if needed)

```bash
agent-browser click "xpath=//button[contains(text(), 'Submit')]"
```

## Command Aliases

| Primary | Aliases |
|---------|---------|
| `open` | `goto`, `navigate` |
| `close` | `quit`, `exit` |
| `press` | `key` |
| `scrollintoview` | `scrollinto` |
