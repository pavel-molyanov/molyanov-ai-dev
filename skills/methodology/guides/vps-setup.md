# VPS Setup Guide for Claude Code

> Reference documentation for VPS server in Latvia

## Server Information

### Hardware Specs
- **Provider:** Beget
- **Location:** Latvia 🇱🇻
- **IP Address:** `2.58.98.203`
- **RAM:** 8GB
- **CPU:** 4 cores
- **Storage:** 100GB NVMe SSD
- **OS:** Ubuntu 24.04 LTS

### Access
- **Username:** `molyanov`
- **Authentication:** SSH key only (password auth disabled)
- **SSH Port:** 22 (UFW firewall enabled)

---

## SSH Access Configuration

### SSH Keys

Three SSH keys configured:

1. **Mac key:** `~/.ssh/claude_code_vps`
   - For primary development from Mac

2. **Mobile key:** Generated in Termius
   - For access from iPhone/Android

3. **Original root key** (deprecated)
   - Root login disabled for security

### Mac SSH Config

File: `~/.ssh/config`

```ssh-config
# Claude Code VPS в Латвии
Host claude-vps
    HostName 2.58.98.203
    User molyanov
    IdentityFile ~/.ssh/claude_code_vps
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

### Shell Aliases (Mac)

File: `~/.zshrc`

```bash
# SSH aliases for Claude Code VPS
alias vps='ssh claude-vps'
alias vps-claude='ssh claude-vps -t "bash --login -c \"tmux attach -t claude || tmux new -s claude\""'
```

### Security Configuration

**Enabled:**
- ✅ SSH key authentication only
- ✅ UFW firewall (only port 22 open)
- ✅ Passwordless sudo for molyanov user
- ✅ ~/.bashrc permissions 600 (OAuth token protected)

**Disabled:**
- ❌ Root login
- ❌ Password authentication
- ❌ All ports except SSH

---

## Claude Code on VPS

### Installation Details

- **Version:** 2.0.36
- **Installation method:** npm global
- **Location:** `~/.npm-global/bin/claude`
- **Config:** `~/.claude/` (synced with GitHub)

### Authentication

**Method:** OAuth via Pro subscription

The VPS uses the same Claude Pro subscription as Mac. Authentication persists after initial browser-based login.

**Important:** No `ANTHROPIC_API_KEY` should be set - OAuth handles everything.

### Dependencies

Installed on VPS:
- **Node.js:** 20.19.5 LTS
- **npm:** 10.8.2
- **git:** 2.43.0
- **ripgrep:** 14.1.0 (for code search)
- **tmux:** 3.4 (for persistent sessions)

### Directory Structure

```
/home/molyanov/
├── .claude/              # Meta-project (synced with GitHub)
│   ├── commands/         # Slash commands
│   ├── skills/           # Skills
│   ├── agents/           # Agent configurations
│   └── plugins/          # MCP plugins
└── projects/             # Your projects
    └── (git cloned projects)
```

---

## Access Methods

### 1. Terminal (Mac)

Use aliases from `~/.zshrc`:
- `vps` - Simple SSH connection
- `vps-claude` - SSH + auto-attach to tmux session

### 2. Termius (Mobile)

- **Host:** 2.58.98.203
- **Port:** 22
- **Username:** molyanov
- **Key:** Termius-generated key (already added to VPS authorized_keys)

### 3. Cursor IDE (Remote-SSH)

- Extension: "Remote - SSH"
- Host: `claude-vps` (from ~/.ssh/config)
- Paths: `/home/molyanov/.claude` or `/home/molyanov/projects/`

---

## tmux Configuration

### Configuration File

**Location:** `/home/molyanov/.tmux.conf`

Key features:
- 256 colors support
- Mouse enabled
- 50,000 line history
- Custom key bindings

### Aliases

**On VPS:** `tm` - Attach to 'claude' session or create new

Key bindings:
- `Ctrl+B, D` - Detach (session continues running)
- `Ctrl+B, [` - Scroll mode

---

## Synchronization

### What's synced via GitHub
- `~/.claude/` meta-project (commands, skills, config)
- All project repositories (each project → its own GitHub)

**Auto-sync on session start:**
- SessionStart hook runs `~/.claude/scripts/sync-from-github.sh`
- Automatically syncs **two repositories** when starting Claude Code:
  1. `~/.claude/` meta-project (from github.com/pavel-molyanov/.claude)
  2. Current project (from its own GitHub repository)
- Non-blocking: skips sync if uncommitted changes detected
- Shows clear status messages (✓ up to date, ⚠️ uncommitted changes)
- Configured in `~/.claude/settings.json`

**How it works:**
```bash
# Launch Claude Code in any project
cd ~/projects/my-app
claude

# Script automatically:
# 1. git pull for ~/.claude (if no uncommitted changes)
# 2. git pull for ~/projects/my-app (if no uncommitted changes)
```

### What's NOT synced
- OAuth tokens (device-specific)
- SSH keys (security)
- Local caches

---

## Critical Paths

### On VPS
- `/home/molyanov/.claude/` - Meta-project (backed up to GitHub)
- `/home/molyanov/projects/` - Your projects (each has own git remote)
- `/home/molyanov/.ssh/` - SSH keys
- `/home/molyanov/.bashrc` - OAuth token
- `/home/molyanov/.tmux.conf` - tmux config

### On Mac
- `~/.ssh/claude_code_vps` - VPS SSH key
- `~/.ssh/config` - SSH configuration
- `~/.zshrc` - Shell aliases

---

## Troubleshooting

### SSH Connection Issues

**Problem:** `Permission denied (publickey)`
- Check key permissions: `ls -la ~/.ssh/claude_code_vps` (should be 600)
- Fix: `chmod 600 ~/.ssh/claude_code_vps`

**Problem:** `Connection timeout`
- Check server: `ping 2.58.98.203`
- Check SSH service on VPS: `sudo systemctl status ssh`

### Claude Code Issues

**Problem:** `claude: command not found`
- Check PATH includes `~/.npm-global/bin`
- Fix: Add to ~/.bashrc: `export PATH=~/.npm-global/bin:$PATH`

### tmux Issues

**Problem:** Can't attach to session
- Check sessions: `tmux ls`
- Create new: `tm`

**Problem:** Scrolling doesn't work
- Use tmux copy mode: `Ctrl+B, [`

### GitHub SSH Issues

**Problem:** Can't push/pull from VPS
- Test connection: `ssh -T git@github.com`
- Should see: "Hi pavel-molyanov!"
- Check key added to GitHub: https://github.com/settings/keys

---

## Related Documentation

- [Infrastructure Skill](../SKILL.md) - Overview of infrastructure setup
- [Deployment Platforms](./deployment-platforms.md) - Other deployment options

---

**Last Updated:** 2025-11-10
**VPS Provider:** Beget
**Status:** ✅ Active & Configured
