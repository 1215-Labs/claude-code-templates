#!/bin/bash
# Resilient fork wrapper with model fallback chains
# Usage: resilient_fork.sh <cli> "<prompt>" [timeout_seconds]

set -o pipefail

# Configuration
DEFAULT_TIMEOUT=300
LOG_DIR="/tmp"

# Fallback chains
CODEX_MODELS=("gpt-5.2-codex" "gpt-5.1-codex-max" "gpt-4o")
GEMINI_MODELS=("gemini-3-pro-preview" "gemini-2.5-flash" "gemini-2.0-flash-exp")
CLAUDE_MODELS=("opus" "sonnet" "haiku")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

show_usage() {
    cat << EOF
Resilient Fork - Run CLI agents with automatic model fallback

Usage: $(basename "$0") <cli> "<prompt>" [timeout_seconds]

Arguments:
  cli             Target CLI: codex, gemini, or claude
  prompt          The prompt/task to execute
  timeout         Timeout in seconds (default: $DEFAULT_TIMEOUT)

Fallback Chains:
  codex:  ${CODEX_MODELS[*]}
  gemini: ${GEMINI_MODELS[*]}
  claude: ${CLAUDE_MODELS[*]}

Examples:
  $(basename "$0") codex "Analyze this codebase" 600
  $(basename "$0") gemini "Generate test cases" 300
  $(basename "$0") claude "Fix the bug in auth.py"

Environment:
  OPENAI_API_KEY     Required for Codex
  GEMINI_API_KEY     Required for Gemini (or OAuth)
  ANTHROPIC_API_KEY  Required for Claude
EOF
}

run_codex() {
    local model="$1"
    local prompt="$2"
    local timeout="$3"
    local log_file="${LOG_DIR}/fork_codex_$(date +%Y%m%d_%H%M%S).log"

    log "Running Codex with model: $model"
    timeout "$timeout" codex exec --full-auto --skip-git-repo-check -m "$model" "$prompt" 2>&1 | tee "$log_file"
    return ${PIPESTATUS[0]}
}

run_gemini() {
    local model="$1"
    local prompt="$2"
    local timeout="$3"
    local log_file="${LOG_DIR}/fork_gemini_$(date +%Y%m%d_%H%M%S).log"

    log "Running Gemini with model: $model"
    timeout "$timeout" gemini -p "$prompt" --model "$model" --approval-mode yolo 2>&1 | tee "$log_file"
    return ${PIPESTATUS[0]}
}

run_claude() {
    local model="$1"
    local prompt="$2"
    local timeout="$3"
    local log_file="${LOG_DIR}/fork_claude_$(date +%Y%m%d_%H%M%S).log"

    log "Running Claude with model: $model"
    timeout "$timeout" claude --dangerously-skip-permissions --model "$model" "$prompt" 2>&1 | tee "$log_file"
    return ${PIPESTATUS[0]}
}

run_with_fallback() {
    local cli="$1"
    local prompt="$2"
    local timeout="$3"

    local -a models
    case "$cli" in
        codex)
            models=("${CODEX_MODELS[@]}")
            ;;
        gemini)
            models=("${GEMINI_MODELS[@]}")
            ;;
        claude)
            models=("${CLAUDE_MODELS[@]}")
            ;;
        *)
            log_fail "Unknown CLI: $cli"
            return 1
            ;;
    esac

    local attempt=1
    local total=${#models[@]}

    for model in "${models[@]}"; do
        log "Attempt $attempt/$total: $cli with $model"

        local exit_code
        case "$cli" in
            codex) run_codex "$model" "$prompt" "$timeout"; exit_code=$? ;;
            gemini) run_gemini "$model" "$prompt" "$timeout"; exit_code=$? ;;
            claude) run_claude "$model" "$prompt" "$timeout"; exit_code=$? ;;
        esac

        if [[ $exit_code -eq 0 ]]; then
            log_success "Completed with $model"
            return 0
        elif [[ $exit_code -eq 124 ]]; then
            log_warn "Timeout with $model after ${timeout}s"
        else
            log_warn "Failed with $model (exit code: $exit_code)"
        fi

        ((attempt++))

        if [[ $attempt -le $total ]]; then
            log "Falling back to next model..."
            sleep 2  # Brief pause between attempts
        fi
    done

    log_fail "All models failed for $cli"
    return 1
}

# Main
main() {
    if [[ $# -lt 2 ]]; then
        show_usage
        exit 1
    fi

    local cli="$1"
    local prompt="$2"
    local timeout="${3:-$DEFAULT_TIMEOUT}"

    # Validate CLI
    if [[ ! "$cli" =~ ^(codex|gemini|claude)$ ]]; then
        log_fail "Invalid CLI: $cli"
        echo "Supported: codex, gemini, claude"
        exit 1
    fi

    # Check for required tools
    if ! command -v "$cli" &>/dev/null; then
        log_fail "$cli CLI not found"
        exit 1
    fi

    log "Starting resilient fork: $cli"
    log "Prompt: $prompt"
    log "Timeout: ${timeout}s"
    echo ""

    run_with_fallback "$cli" "$prompt" "$timeout"
    exit $?
}

main "$@"
