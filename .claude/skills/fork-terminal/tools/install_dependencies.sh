#!/bin/bash
# Fork-Terminal Dependency Installer
# Run with: bash install_dependencies.sh [--all|--required|--optional|--brew]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Package lists
APT_REQUIRED=(
    "python3"
    "xterm"
)

APT_OPTIONAL=(
    "xdotool"
    "scrot"
    "imagemagick"
    "tree"
    "jq"
)

BREW_PACKAGES=(
    "tree"
    "imagemagick"
    "jq"
)

show_help() {
    cat << EOF
Fork-Terminal Dependency Installer

Usage: $(basename "$0") [OPTIONS]

Options:
  --all         Install all dependencies (required + optional) via apt
  --required    Install only required dependencies via apt
  --optional    Install only optional dependencies via apt
  --brew        Install optional dependencies via Homebrew (no sudo)
  --check       Just check dependencies without installing
  --help        Show this help message

Examples:
  $(basename "$0") --all          # Full install via apt
  $(basename "$0") --brew         # Install via Homebrew (no sudo needed)
  $(basename "$0") --check        # Check what's missing

Note: apt installations require sudo privileges.
      Homebrew is recommended if you have network issues with apt.
EOF
}

check_only() {
    echo -e "${BLUE}Running dependency check...${NC}"
    echo ""
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    bash "$SCRIPT_DIR/check_dependencies.sh"
}

install_apt_required() {
    echo -e "${BLUE}Installing required packages via apt...${NC}"
    echo "Packages: ${APT_REQUIRED[*]}"
    echo ""
    sudo apt update
    sudo apt install -y "${APT_REQUIRED[@]}"
    echo -e "${GREEN}Required packages installed!${NC}"
}

install_apt_optional() {
    echo -e "${BLUE}Installing optional packages via apt...${NC}"
    echo "Packages: ${APT_OPTIONAL[*]}"
    echo ""
    sudo apt update
    sudo apt install -y "${APT_OPTIONAL[@]}"
    echo -e "${GREEN}Optional packages installed!${NC}"
}

install_apt_all() {
    echo -e "${BLUE}Installing all packages via apt...${NC}"
    ALL_PACKAGES=("${APT_REQUIRED[@]}" "${APT_OPTIONAL[@]}")
    echo "Packages: ${ALL_PACKAGES[*]}"
    echo ""
    sudo apt update
    sudo apt install -y "${ALL_PACKAGES[@]}"
    echo -e "${GREEN}All packages installed!${NC}"
}

install_brew() {
    if ! command -v brew &>/dev/null; then
        echo -e "${RED}Homebrew not found!${NC}"
        echo "Install Homebrew first: https://brew.sh"
        exit 1
    fi

    echo -e "${BLUE}Installing packages via Homebrew...${NC}"
    echo "Packages: ${BREW_PACKAGES[*]}"
    echo ""

    for pkg in "${BREW_PACKAGES[@]}"; do
        if brew list "$pkg" &>/dev/null; then
            echo -e "${GREEN}[OK]${NC} $pkg already installed"
        else
            echo -e "${YELLOW}Installing $pkg...${NC}"
            brew install "$pkg"
        fi
    done

    echo ""
    echo -e "${GREEN}Homebrew packages installed!${NC}"
    echo ""
    echo -e "${YELLOW}Note:${NC} xdotool and scrot are X11-specific and not available via brew."
    echo "For screenshot/window detection, install via apt:"
    echo "  sudo apt install -y xdotool scrot"
}

# Main
case "${1:-}" in
    --all)
        install_apt_all
        ;;
    --required)
        install_apt_required
        ;;
    --optional)
        install_apt_optional
        ;;
    --brew)
        install_brew
        ;;
    --check)
        check_only
        ;;
    --help|-h|"")
        show_help
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
