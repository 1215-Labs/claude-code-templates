#!/bin/bash
# Shell aliases for fork-terminal skill v2.0.0
# Source this file in your .bashrc or .zshrc:
#   source ~/.claude/skills/fork-terminal/tools/fork_aliases.sh

# =============================================================================
# Codex Aliases - Full auto with git check skip
# =============================================================================

# Basic codex exec with optimal settings
alias codex-auto='codex exec --full-auto --skip-git-repo-check'

# Codex with specific models
alias codex-52='codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex'
alias codex-51='codex exec --full-auto --skip-git-repo-check -m gpt-5.1-codex-max'
alias codex-4o='codex exec --full-auto --skip-git-repo-check -m gpt-4o'

# Codex review (uses exec review subcommand)
alias codex-review='codex exec review --full-auto'

# =============================================================================
# Gemini Aliases - Prompt mode with yolo
# =============================================================================

# Basic gemini with optimal settings
alias gemini-auto='gemini -p --approval-mode yolo'

# Gemini with specific models
alias gemini-pro='gemini -p --model gemini-3-pro-preview --approval-mode yolo'
alias gemini-flash='gemini -p --model gemini-2.5-flash --approval-mode yolo'
alias gemini-exp='gemini -p --model gemini-2.0-flash-exp --approval-mode yolo'

# =============================================================================
# Claude Code Aliases - Skip permissions
# =============================================================================

# Basic claude with optimal settings
alias claude-auto='claude --dangerously-skip-permissions'

# Claude with specific models
alias claude-opus='claude --dangerously-skip-permissions --model opus'
alias claude-sonnet='claude --dangerously-skip-permissions --model sonnet'
alias claude-haiku='claude --dangerously-skip-permissions --model haiku'

# =============================================================================
# Combined Launcher Functions
# =============================================================================

# Fork agent with timeout and model selection
# Usage: fork-agent <cli> "<prompt>" [timeout_seconds]
fork-agent() {
    local cli="$1"
    local prompt="$2"
    local timeout_secs="${3:-300}"

    if [[ -z "$cli" || -z "$prompt" ]]; then
        echo "Usage: fork-agent <codex|gemini|claude> \"<prompt>\" [timeout_seconds]"
        echo "Example: fork-agent codex \"Analyze this codebase\" 600"
        return 1
    fi

    case "$cli" in
        codex)
            echo "[$(date)] Starting Codex with ${timeout_secs}s timeout..."
            timeout "$timeout_secs" codex exec --full-auto --skip-git-repo-check -m gpt-5.2-codex "$prompt"
            ;;
        gemini)
            echo "[$(date)] Starting Gemini with ${timeout_secs}s timeout..."
            timeout "$timeout_secs" gemini -p "$prompt" --model gemini-3-pro-preview --approval-mode yolo
            ;;
        claude)
            echo "[$(date)] Starting Claude Code with ${timeout_secs}s timeout..."
            timeout "$timeout_secs" claude --dangerously-skip-permissions --model opus "$prompt"
            ;;
        *)
            echo "Unknown CLI: $cli"
            echo "Supported: codex, gemini, claude"
            return 1
            ;;
    esac

    local exit_code=$?
    if [[ $exit_code -eq 124 ]]; then
        echo "[$(date)] TIMEOUT: Command exceeded ${timeout_secs} seconds"
    elif [[ $exit_code -ne 0 ]]; then
        echo "[$(date)] FAILED: Exit code $exit_code"
    else
        echo "[$(date)] COMPLETED successfully"
    fi
    return $exit_code
}

# Fork agent with fallback chain
# Usage: fork-agent-fallback <cli> "<prompt>" [timeout_seconds]
fork-agent-fallback() {
    local cli="$1"
    local prompt="$2"
    local timeout_secs="${3:-300}"

    if [[ -z "$cli" || -z "$prompt" ]]; then
        echo "Usage: fork-agent-fallback <codex|gemini|claude> \"<prompt>\" [timeout_seconds]"
        return 1
    fi

    local models
    case "$cli" in
        codex)
            models=("gpt-5.2-codex" "gpt-5.1-codex-max" "gpt-4o")
            ;;
        gemini)
            models=("gemini-3-pro-preview" "gemini-2.5-flash" "gemini-2.0-flash-exp")
            ;;
        claude)
            models=("opus" "sonnet" "haiku")
            ;;
        *)
            echo "Unknown CLI: $cli"
            return 1
            ;;
    esac

    for model in "${models[@]}"; do
        echo "[$(date)] Trying $cli with model $model..."

        case "$cli" in
            codex)
                timeout "$timeout_secs" codex exec --full-auto --skip-git-repo-check -m "$model" "$prompt"
                ;;
            gemini)
                timeout "$timeout_secs" gemini -p "$prompt" --model "$model" --approval-mode yolo
                ;;
            claude)
                timeout "$timeout_secs" claude --dangerously-skip-permissions --model "$model" "$prompt"
                ;;
        esac

        local exit_code=$?
        if [[ $exit_code -eq 0 ]]; then
            echo "[$(date)] SUCCESS with $model"
            return 0
        fi

        echo "[$(date)] FAILED with $model (exit code $exit_code), trying next..."
    done

    echo "[$(date)] ALL MODELS FAILED for $cli"
    return 1
}

# Quick status check for CLI tools
fork-check() {
    echo "=== Fork Terminal CLI Status ==="
    echo ""

    # Check Codex
    if command -v codex &>/dev/null; then
        local codex_ver=$(codex --version 2>/dev/null | head -1)
        echo "Codex: INSTALLED ($codex_ver)"
    else
        echo "Codex: NOT FOUND"
    fi

    # Check Gemini
    if command -v gemini &>/dev/null; then
        echo "Gemini: INSTALLED"
        if [[ -n "$GEMINI_API_KEY" ]]; then
            echo "  GEMINI_API_KEY: SET"
        else
            echo "  GEMINI_API_KEY: NOT SET (may use OAuth)"
        fi
    else
        echo "Gemini: NOT FOUND"
    fi

    # Check Claude
    if command -v claude &>/dev/null; then
        local claude_ver=$(claude --version 2>/dev/null | head -1)
        echo "Claude: INSTALLED ($claude_ver)"
    else
        echo "Claude: NOT FOUND"
    fi

    # Check OpenAI key for Codex
    if [[ -n "$OPENAI_API_KEY" ]]; then
        echo ""
        echo "OPENAI_API_KEY: SET"
    fi

    # Check Anthropic key for Claude
    if [[ -n "$ANTHROPIC_API_KEY" ]]; then
        echo "ANTHROPIC_API_KEY: SET"
    fi

    echo ""
    echo "=== Available Aliases ==="
    echo "codex-auto, codex-52, codex-51, codex-4o, codex-review"
    echo "gemini-auto, gemini-pro, gemini-flash, gemini-exp"
    echo "claude-auto, claude-opus, claude-sonnet, claude-haiku"
    echo ""
    echo "=== Functions ==="
    echo "fork-agent <cli> \"<prompt>\" [timeout]     - Run with timeout"
    echo "fork-agent-fallback <cli> \"<prompt>\"      - Run with model fallback"
    echo "fork-check                                 - Show this status"
}

echo "Fork-terminal aliases loaded. Run 'fork-check' for status."
