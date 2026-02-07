---
name: mac-discover
description: |
  Find configuration files, apps, and preference domains not yet tracked by mac-manage

  Usage: /mac-discover [focus]

  Examples:
  /mac-discover
  /mac-discover "dotfiles"
  /mac-discover "apps"
  /mac-discover "defaults"

  Best for: Expanding mac-manage coverage, finding config drift
  See also: /mac-status (snapshot management), /mac-health (system health)
argument-hint: "[optional focus: dotfiles | apps | defaults]"
user-invocable: true
related:
  commands: [mac-manage/mac-health, mac-manage/mac-status, mac-manage/mac-diff]
  skills: [mac-manage-context]
thinking: auto
allowed-tools:
  - Bash(*)
  - Read
  - Grep
  - Glob
  - Task
---

# Configuration Discovery

**Focus area**: $ARGUMENTS

Reference the `mac-manage-context` skill for paths, output formats, and glossaries.

Parse `$ARGUMENTS` for focus. If empty, run all three discovery scans.

## Step 1: Read Current Baselines

Read the current tracking configuration:

- `/Users/mike/mac-manage/baseline/dotfiles.list` — currently tracked dotfiles
- `/Users/mike/mac-manage/baseline/defaults-domains.list` — currently tracked preference domains
- `/Users/mike/mac-manage/baseline/apps-manual.list` — manually tracked apps

## Step 2: Dotfile Discovery

**Skip if focus is "apps" or "defaults" only.**

Scan `$HOME` for common configuration files not already in `dotfiles.list`:

```bash
# Common dotfiles to check for
for f in .zshrc .bashrc .bash_profile .zprofile .tmux.conf .vimrc .inputrc \
         .gitconfig .gitignore_global .npmrc .yarnrc .pyenv/version \
         .ssh/config .gnupg/gpg.conf .curlrc .wgetrc .editorconfig \
         .tool-versions .mise.toml .config/starship.toml \
         .config/nvim/init.lua .config/nvim/init.vim \
         .config/gh/config.yml .config/bat/config \
         .config/kitty/kitty.conf .config/alacritty/alacritty.yml \
         .config/wezterm/wezterm.lua .config/karabiner/karabiner.json \
         .config/raycast/config.json .hammerspoon/init.lua; do
  [ -e "$HOME/$f" ] && echo "FOUND: $f"
done
```

Compare against `dotfiles.list` to find untracked files.

### Rate Each Discovery

- **Recommended**: Files that are commonly personalized and important to preserve (`.ssh/config`, `.tmux.conf`, `.config/nvim/init.lua`)
- **Optional**: Files that exist but may be auto-generated or rarely customized (`.inputrc`, `.curlrc`)
- **Skip**: Files that contain secrets or are too volatile (`.npmrc` with auth tokens, `.pyenv/version`)

**Sensitive file warning**: Flag files that may contain secrets (`.npmrc`, `.netrc`, `.env`, SSH keys). These should NOT be added to tracking without sanitization.

## Step 3: Defaults Domain Discovery

**Skip if focus is "dotfiles" or "apps" only.**

```bash
# Get all defaults domains on the system
defaults domains 2>/dev/null | tr ',' '\n' | sed 's/^ *//' | sort
```

Compare against `defaults-domains.list`. Identify domains for:

### Installed Apps with Preference Domains

Check which installed apps (from Homebrew casks and /Applications) have corresponding defaults domains. Commonly valuable:

| App | Domain | Worth Tracking? |
|-----|--------|----------------|
| iTerm2 | `com.googlecode.iterm2` | Recommended — extensive customization |
| VS Code | `com.microsoft.VSCode` | Optional — settings sync handles this |
| Raycast | `com.raycast.macos` | Recommended — shortcuts and extensions |
| Rectangle | `com.knollsoft.Rectangle` | Recommended — window management shortcuts |
| Alfred | `com.runningwithcrayons.Alfred-Preferences` | Recommended |
| 1Password | `com.1password.1password` | Skip — managed by service |
| Slack | `com.tinyspeck.slackmacgap` | Optional |
| Arc | `company.thebrowser.Browser` | Optional |

### Rate Each Domain

- **Recommended**: Apps where you customize behavior (window managers, terminal emulators, text editors)
- **Optional**: Apps with some customization but also cloud sync
- **Skip**: Apps managed entirely by cloud services, or system domains with no user-facing settings

## Step 4: Application Discovery

**Skip if focus is "dotfiles" or "defaults" only.**

```bash
# Applications in /Applications
ls -1 /Applications/ 2>/dev/null

# Homebrew casks
brew list --cask 2>/dev/null

# Mac App Store apps
mas list 2>/dev/null
```

Cross-reference to find:
- Apps in `/Applications` that are NOT in `brew list --cask` and NOT in `mas list`
- These are "unmanaged" apps (manually downloaded DMGs, etc.)

Compare against `baseline/apps-manual.list` to find untracked manual apps.

### Rate Each Discovery

- **Recommended**: Apps you use daily and would want to reinstall
- **Optional**: Rarely used apps or ones easily re-downloaded
- **Skip**: System-bundled apps, temporary/trial apps

## Step 5: Present Results

For each category, show discoveries in a table:

```
## Dotfiles Not Tracked

| File | Rating | Reason |
|------|--------|--------|
| .tmux.conf | Recommended | Heavily customized terminal multiplexer config |
| .ssh/config | Recommended | SSH host aliases (review for secrets first) |
| .config/nvim/init.lua | Recommended | Neovim configuration |
| .inputrc | Optional | Readline config, minimal customization |

### Copy-paste lines for dotfiles.list:
.tmux.conf
.ssh/config
.config/nvim/init.lua
```

```
## Defaults Domains Not Tracked

| Domain | App | Rating |
|--------|-----|--------|
| com.googlecode.iterm2 | iTerm2 | Recommended |
| com.knollsoft.Rectangle | Rectangle | Recommended |

### Copy-paste lines for defaults-domains.list:
com.googlecode.iterm2
com.knollsoft.Rectangle
```

```
## Unmanaged Applications

| App | Rating | Suggestion |
|-----|--------|------------|
| Figma.app | Recommended | Add to apps-manual.list |
| Zoom.app | Optional | Available via brew: `brew install --cask zoom` |

### Copy-paste lines for apps-manual.list:
Figma.app
```

## Step 6: Summary

- Total discoveries: N dotfiles, N domains, N apps
- Recommended additions: N items
- Suggest running `/mac-status "snapshot"` after updating baseline files to capture the new tracking
