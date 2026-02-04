#!/bin/bash
# Fork-Terminal Dependency Checker
# Checks for required and optional tools, provides install commands

set -o pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "========================================"
echo "Fork-Terminal v2.0.0 Dependency Check"
echo "========================================"
echo ""

# Track missing dependencies
MISSING_REQUIRED=()
MISSING_OPTIONAL=()
INSTALL_APT=()
INSTALL_BREW=()

# =============================================================================
# Required Dependencies (Core functionality)
# =============================================================================
echo -e "${BLUE}=== Required (Core Functionality) ===${NC}"

# Python 3
if command -v python3 &>/dev/null; then
    version=$(python3 --version 2>&1)
    echo -e "${GREEN}[OK]${NC} python3 ($version)"
else
    echo -e "${RED}[MISSING]${NC} python3"
    MISSING_REQUIRED+=("python3")
    INSTALL_APT+=("python3")
fi

# Bash
if command -v bash &>/dev/null; then
    version=$(bash --version | head -1)
    echo -e "${GREEN}[OK]${NC} bash"
else
    echo -e "${RED}[MISSING]${NC} bash"
    MISSING_REQUIRED+=("bash")
fi

# Terminal emulator (at least one)
TERMINAL_FOUND=false
for term in xterm gnome-terminal konsole alacritty kitty xfce4-terminal; do
    if command -v "$term" &>/dev/null; then
        echo -e "${GREEN}[OK]${NC} $term (terminal emulator)"
        TERMINAL_FOUND=true
        break
    fi
done
if ! $TERMINAL_FOUND; then
    echo -e "${RED}[MISSING]${NC} terminal emulator (xterm, gnome-terminal, etc.)"
    MISSING_REQUIRED+=("terminal")
    INSTALL_APT+=("xterm")
fi

echo ""

# =============================================================================
# Agentic CLI Tools
# =============================================================================
echo -e "${BLUE}=== Agentic CLI Tools ===${NC}"

# Codex CLI
if command -v codex &>/dev/null; then
    version=$(codex --version 2>&1 | head -1)
    echo -e "${GREEN}[OK]${NC} codex ($version)"
else
    echo -e "${YELLOW}[NOT INSTALLED]${NC} codex - Install: npm install -g @openai/codex"
fi

# Gemini CLI
if command -v gemini &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} gemini"
else
    echo -e "${YELLOW}[NOT INSTALLED]${NC} gemini - Install: npm install -g @anthropic-ai/gemini-cli"
fi

# Claude Code
if command -v claude &>/dev/null; then
    version=$(claude --version 2>&1 | head -1)
    echo -e "${GREEN}[OK]${NC} claude ($version)"
else
    echo -e "${YELLOW}[NOT INSTALLED]${NC} claude - Install: npm install -g @anthropic-ai/claude-code"
fi

echo ""

# =============================================================================
# Optional Dependencies (Enhanced features)
# =============================================================================
echo -e "${BLUE}=== Optional (Enhanced Features) ===${NC}"

# xdotool - Window detection
if command -v xdotool &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} xdotool (window detection)"
else
    echo -e "${YELLOW}[MISSING]${NC} xdotool (window detection)"
    MISSING_OPTIONAL+=("xdotool")
    INSTALL_APT+=("xdotool")
fi

# scrot - Screenshots
if command -v scrot &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} scrot (screenshots)"
else
    echo -e "${YELLOW}[MISSING]${NC} scrot (screenshots)"
    MISSING_OPTIONAL+=("scrot")
    INSTALL_APT+=("scrot")
fi

# imagemagick - Image processing
if command -v convert &>/dev/null || command -v magick &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} imagemagick (image processing)"
else
    echo -e "${YELLOW}[MISSING]${NC} imagemagick (image processing)"
    MISSING_OPTIONAL+=("imagemagick")
    INSTALL_APT+=("imagemagick")
    INSTALL_BREW+=("imagemagick")
fi

# tree - Directory visualization
if command -v tree &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} tree (directory visualization)"
else
    echo -e "${YELLOW}[MISSING]${NC} tree (directory visualization)"
    MISSING_OPTIONAL+=("tree")
    INSTALL_APT+=("tree")
    INSTALL_BREW+=("tree")
fi

# jq - JSON processing
if command -v jq &>/dev/null; then
    echo -e "${GREEN}[OK]${NC} jq (JSON processing)"
else
    echo -e "${YELLOW}[MISSING]${NC} jq (JSON processing)"
    MISSING_OPTIONAL+=("jq")
    INSTALL_APT+=("jq")
    INSTALL_BREW+=("jq")
fi

echo ""

# =============================================================================
# API Keys Check
# =============================================================================
echo -e "${BLUE}=== API Keys ===${NC}"

check_key() {
    local key_name="$1"
    local cli_name="$2"
    if [[ -n "${!key_name}" ]]; then
        echo -e "${GREEN}[SET]${NC} $key_name (for $cli_name)"
    else
        echo -e "${YELLOW}[NOT SET]${NC} $key_name (for $cli_name)"
    fi
}

check_key "OPENAI_API_KEY" "Codex"
check_key "GEMINI_API_KEY" "Gemini"
check_key "ANTHROPIC_API_KEY" "Claude"
check_key "GOOGLE_API_KEY" "Google services"

echo ""

# =============================================================================
# Summary and Install Commands
# =============================================================================
echo "========================================"
echo "Summary"
echo "========================================"

if [[ ${#MISSING_REQUIRED[@]} -eq 0 ]]; then
    echo -e "${GREEN}All required dependencies installed!${NC}"
else
    echo -e "${RED}Missing required: ${MISSING_REQUIRED[*]}${NC}"
fi

if [[ ${#MISSING_OPTIONAL[@]} -gt 0 ]]; then
    echo -e "${YELLOW}Missing optional: ${MISSING_OPTIONAL[*]}${NC}"
fi

echo ""

# Generate install commands if anything is missing
if [[ ${#INSTALL_APT[@]} -gt 0 ]] || [[ ${#INSTALL_BREW[@]} -gt 0 ]]; then
    echo "========================================"
    echo "Install Commands"
    echo "========================================"
    echo ""

    if [[ ${#INSTALL_APT[@]} -gt 0 ]]; then
        # Remove duplicates
        UNIQUE_APT=($(echo "${INSTALL_APT[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
        echo -e "${BLUE}APT (Ubuntu/Debian):${NC}"
        echo "  sudo apt install -y ${UNIQUE_APT[*]}"
        echo ""
    fi

    if [[ ${#INSTALL_BREW[@]} -gt 0 ]]; then
        # Remove duplicates
        UNIQUE_BREW=($(echo "${INSTALL_BREW[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
        echo -e "${BLUE}Homebrew (alternative):${NC}"
        echo "  brew install ${UNIQUE_BREW[*]}"
        echo ""
    fi
fi

# Exit with appropriate code
if [[ ${#MISSING_REQUIRED[@]} -gt 0 ]]; then
    exit 1
fi
exit 0
