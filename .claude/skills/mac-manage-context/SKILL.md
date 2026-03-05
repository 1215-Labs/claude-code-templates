---
name: mac-manage-context
description: "This skill should be used when mac-manage slash commands need shared knowledge about paths, output formats, glossaries, and integration patterns for macOS configuration management."
version: 1.0.0
category: system-management
user-invocable: false
related:
  commands: [mac-manage/mac-health, mac-manage/mac-diff, mac-manage/mac-status, mac-manage/mac-discover, mac-manage/mac-restore]
  workflows: [bug-investigation]
---

# mac-manage Context

Shared context referenced by all `/mac-*` commands. Do NOT invoke directly.

## Paths & Constants

| Variable | Value |
|----------|-------|
| `MAC_MANAGE_DIR` | `/Users/mike/mac-manage` |
| `CLI` | `/Users/mike/mac-manage/mac-manage.sh` |
| `BASELINE_DIR` | `/Users/mike/mac-manage/baseline` |
| `SNAPSHOTS_DIR` | `/Users/mike/mac-manage/snapshots` |
| `SCRIPTS_DIR` | `/Users/mike/mac-manage/scripts` |

## CLI Commands

```
./mac-manage.sh snapshot              # Full snapshot (installs + config)
./mac-manage.sh snapshot-installs     # Software only
./mac-manage.sh snapshot-config       # Dotfiles + defaults only
./mac-manage.sh health                # Security/disk/backup/update checks
./mac-manage.sh diff [old] [new]      # Compare snapshots (defaults to latest two)
./mac-manage.sh restore <dir> [opts]  # Restore dotfiles/defaults
                   --dry-run          #   Preview only
                   --dotfiles         #   Dotfiles only
                   --defaults         #   Defaults only
./mac-manage.sh list                  # List all snapshots
```

## Snapshot Structure

Each snapshot is a timestamped directory (`YYYYMMDD-HHMMSS`) under `snapshots/`:

```
snapshots/20260207-110950/
├── system-info.txt          # hostname, macOS version, disk, uptime
├── Brewfile                 # brew bundle dump
├── brew-formulae.txt        # brew list --formula --versions
├── brew-casks.txt           # brew list --cask --versions
├── brew-taps.txt            # brew tap
├── mas-apps.txt             # mas list (App Store)
├── applications.txt         # ls /Applications
├── security-status.txt      # FileVault, Firewall, SIP, Gatekeeper
├── dotfiles/
│   ├── .zshrc
│   └── .gitconfig
└── defaults/
    ├── NSGlobalDomain.txt       # human-readable
    ├── NSGlobalDomain.plist     # binary (for restore)
    ├── com.apple.dock.txt
    ├── com.apple.dock.plist
    └── ...
```

## Baseline Files

```
baseline/
├── dotfiles.list            # Dotfiles to track (one per line, relative to $HOME)
├── defaults-domains.list    # macOS preference domains to track
├── apps-manual.list         # Manually installed apps (not from brew/mas)
└── Brewfile                 # Desired brew state
```

## Output Format Reference

### Health Check Prefixes
- `  PASS  <message>` — Check passed (green)
- `  WARN  <message>` — Warning, not critical (yellow)
- `  FAIL  <message>` — Failed, action needed (red)
- `[INFO]    <message>` — Informational (blue)
- `[WARN]    <message>` — Warning log (yellow)
- `[ERROR]   <message>` — Error log (red)
- `[OK]      <message>` — Success log (green)
- `=== Header ===` — Section header (bold)

### Health Check Sections
1. **Security** — FileVault, Firewall, SIP, Gatekeeper
2. **Backups** — Time Machine status + last backup time
3. **Disk** — Disk usage percentage (<80% pass, 80-90% warn, >90% fail)
4. **Updates** — macOS software updates, Homebrew outdated + doctor

### Diff Output
- Standard unified diff format per category
- Categories: Brew Formulae, Brew Casks, Mac App Store, Applications, Dotfiles, macOS Defaults
- Summary line: `N category(ies) with changes`

## macOS Defaults Domain Glossary

| Domain | Controls | Common Keys |
|--------|----------|-------------|
| `NSGlobalDomain` | System-wide settings | `AppleShowAllExtensions`, `NSAutomaticSpellingCorrectionEnabled`, `AppleInterfaceStyle` (dark mode) |
| `com.apple.dock` | Dock behavior | `autohide` (0/1), `tilesize` (px), `orientation` (left/bottom/right), `show-recents` (0/1), `minimize-to-application` (0/1) |
| `com.apple.finder` | Finder | `ShowPathbar` (0/1), `ShowStatusBar`, `AppleShowAllFiles`, `FXPreferredViewStyle` (1=icon, 2=list, 3=column, 4=gallery) |
| `com.apple.screencapture` | Screenshots | `location` (path), `type` (png/jpg), `disable-shadow` (0/1) |
| `com.apple.screensaver` | Screen saver | `askForPassword` (0/1), `askForPasswordDelay` (seconds) |
| `com.apple.menuextra.clock` | Menu bar clock | `DateFormat` (format string), `FlashDateSeparators` (0/1) |
| `com.apple.WindowManager` | Stage Manager | `GloballyEnabled` (0/1), `EnableStandardClickToShowDesktop` (0/1) |
| `com.apple.universalaccess` | Accessibility | `reduceMotion` (0/1), `reduceTransparency` (0/1) |
| `com.apple.Safari` | Safari | `ShowFullURLInSmartSearchField`, `IncludeDevelopMenu` |
| `com.apple.Terminal` | Terminal.app | `Default Window Settings`, `Startup Window Settings` |
| `com.apple.LaunchServices` | File associations | `LSQuarantine` (0/1 — Gatekeeper quarantine) |
| `com.apple.SoftwareUpdate` | Auto-updates | `AutomaticCheckEnabled`, `AutomaticDownload`, `CriticalUpdateInstall` |

## Common Dotfile Glossary

| File | Purpose | Key Sections |
|------|---------|-------------|
| `.zshrc` | Zsh config | PATH, aliases, plugins, prompt, completions |
| `.gitconfig` | Git config | user.name/email, aliases, core settings, diff/merge tools |
| `.tmux.conf` | Tmux config | prefix key, pane bindings, status bar |
| `.ssh/config` | SSH hosts | Host aliases, IdentityFile, ProxyJump |
| `.config/nvim/init.lua` | Neovim | plugins, keymaps, LSP, colorscheme |
| `.config/starship.toml` | Starship prompt | format, module config |
| `.npmrc` | npm config | registry, auth tokens (sensitive!) |
| `.pyenv/version` | Python version | global Python version |
| `.nvm/alias/default` | Node version | default Node.js version |
| `.config/gh/config.yml` | GitHub CLI | editor, protocol, aliases |

## Integration Patterns

### With `/rca`
When a health check or diff reveals unexpected changes, suggest:
```
/rca "Unexpected change in [area] — [describe what changed]"
```

### With `debugger` Agent
For investigating why a specific setting changed or a tool stopped working, delegate to the debugger agent.

### Security Regression Detection
Compare `security-status.txt` between snapshots. Any PASS→FAIL transition is a regression that should be flagged as Critical.

### Snapshot Age Warnings
- < 7 days old: Current
- 7-14 days: Slightly stale
- 14-30 days: Stale — suggest new snapshot
- > 30 days: Very stale — strongly recommend new snapshot
