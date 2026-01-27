#!/bin/bash
# Common agent-browser workflow examples
# These are reference patterns, not meant to be run directly

# =============================================================================
# PATTERN 1: Basic Page Scraping
# =============================================================================
scrape_page() {
    local url="$1"

    agent-browser open "$url"
    agent-browser wait --load networkidle
    agent-browser snapshot

    # After reviewing snapshot output, extract data by refs
    # agent-browser get text @e12
    # agent-browser get text @e15

    agent-browser close
}

# =============================================================================
# PATTERN 2: Form Login
# =============================================================================
login_form() {
    local url="$1"
    local email="$2"
    local password="$3"

    agent-browser open "$url"
    agent-browser wait --load networkidle
    agent-browser snapshot

    # Identify fields from snapshot, then:
    agent-browser fill @e3 "$email"      # Email field
    agent-browser fill @e5 "$password"   # Password field
    agent-browser click @e7              # Submit button

    agent-browser wait --load networkidle
    agent-browser snapshot  # Verify login success

    agent-browser close
}

# =============================================================================
# PATTERN 3: Multi-Step Form Wizard
# =============================================================================
multi_step_form() {
    agent-browser open "https://example.com/wizard"
    agent-browser wait --load networkidle

    # Step 1
    agent-browser snapshot
    agent-browser fill @e3 "John Doe"
    agent-browser click @e8  # Next button
    agent-browser wait --load networkidle

    # Step 2
    agent-browser snapshot
    agent-browser select @e4 "option1"
    agent-browser check @e6
    agent-browser click @e10  # Next button
    agent-browser wait --load networkidle

    # Step 3 - Submit
    agent-browser snapshot
    agent-browser click @e5  # Submit button
    agent-browser wait --text "Success"

    agent-browser screenshot confirmation.png
    agent-browser close
}

# =============================================================================
# PATTERN 4: Data Table Extraction
# =============================================================================
extract_table_data() {
    agent-browser open "https://example.com/data-table"
    agent-browser wait --load networkidle
    agent-browser snapshot

    # Get row count
    agent-browser get count "table tbody tr"

    # Extract specific cells (adjust refs from snapshot)
    agent-browser get text @e20  # First row, first column
    agent-browser get text @e21  # First row, second column

    # Or use JavaScript for bulk extraction
    agent-browser eval "JSON.stringify(Array.from(document.querySelectorAll('table tbody tr')).map(row => Array.from(row.cells).map(cell => cell.textContent)))"

    agent-browser close
}

# =============================================================================
# PATTERN 5: Screenshot Documentation
# =============================================================================
document_pages() {
    local base_url="$1"

    agent-browser open "$base_url"
    agent-browser wait --load networkidle
    agent-browser screenshot home.png

    agent-browser snapshot
    agent-browser click @e5  # About link
    agent-browser wait --load networkidle
    agent-browser screenshot about.png

    agent-browser snapshot
    agent-browser click @e6  # Contact link
    agent-browser wait --load networkidle
    agent-browser screenshot contact.png

    agent-browser close
}

# =============================================================================
# PATTERN 6: Search and Filter
# =============================================================================
search_and_filter() {
    agent-browser open "https://example.com/products"
    agent-browser wait --load networkidle
    agent-browser snapshot

    # Enter search term
    agent-browser fill @e3 "laptop"
    agent-browser press Enter
    agent-browser wait --load networkidle

    # Apply filter
    agent-browser snapshot
    agent-browser click @e15  # Filter dropdown
    agent-browser click @e18  # Price: Low to High
    agent-browser wait --load networkidle

    # Get results
    agent-browser snapshot
    agent-browser get text @e25  # First result title
    agent-browser get text @e26  # First result price

    agent-browser close
}

# =============================================================================
# PATTERN 7: Handling Modals/Dialogs
# =============================================================================
handle_modal() {
    agent-browser open "https://example.com/with-modal"
    agent-browser wait --load networkidle

    # Trigger modal
    agent-browser snapshot
    agent-browser click @e5  # Button that opens modal
    agent-browser wait "[role='dialog']"  # Wait for modal

    # Interact with modal
    agent-browser snapshot
    agent-browser fill @e20 "Modal input"
    agent-browser click @e22  # Confirm button

    agent-browser wait --load networkidle
    agent-browser close
}

# =============================================================================
# PATTERN 8: Infinite Scroll / Load More
# =============================================================================
handle_infinite_scroll() {
    agent-browser open "https://example.com/feed"
    agent-browser wait --load networkidle

    # Initial content
    agent-browser snapshot
    agent-browser get count ".feed-item"

    # Scroll to load more
    agent-browser scroll down 1000
    agent-browser wait --load networkidle
    agent-browser snapshot
    agent-browser get count ".feed-item"

    # Repeat as needed
    agent-browser scroll down 1000
    agent-browser wait --load networkidle

    agent-browser close
}

# =============================================================================
# PATTERN 9: File Download
# =============================================================================
download_file() {
    agent-browser open "https://example.com/downloads"
    agent-browser wait --load networkidle
    agent-browser snapshot

    # Click download link
    agent-browser click @e8  # Download button

    # Wait for download (may need adjustment based on site)
    agent-browser wait 3000

    agent-browser close
}

# =============================================================================
# PATTERN 10: Mobile Emulation
# =============================================================================
mobile_testing() {
    agent-browser set device "iPhone 14"
    agent-browser open "https://example.com"
    agent-browser wait --load networkidle

    agent-browser screenshot mobile-home.png
    agent-browser snapshot

    # Test mobile menu
    agent-browser click @e3  # Hamburger menu
    agent-browser wait ".mobile-menu"
    agent-browser screenshot mobile-menu.png

    agent-browser close
}

# =============================================================================
# PATTERN 11: Error Recovery
# =============================================================================
with_error_recovery() {
    agent-browser open "https://example.com/form"
    agent-browser wait --load networkidle

    agent-browser snapshot
    agent-browser fill @e3 "test@example.com"
    agent-browser click @e7

    # Check for error state
    if agent-browser is visible ".error-message"; then
        agent-browser screenshot error-state.png
        agent-browser get text ".error-message"
    else
        agent-browser wait --text "Success"
        agent-browser screenshot success.png
    fi

    agent-browser close
}
