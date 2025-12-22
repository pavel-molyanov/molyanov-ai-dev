# Workflow: Copy Project to VPS

## Когда использовать

Копирование проекта с Mac на VPS для разработки в dual-environment режиме (Mac + VPS).

**Это НЕ deployment!** Это копирование кода для разработки с VPS (например, работа с мобильного через Termius или запуск долгих операций).

---

## ⚠️ IMPORTANT: Clarification Required

When user says "перенести проект на VPS" or "скопировать на VPS", **ALWAYS ask first:**

**Question to user:**
> Уточни, пожалуйста:
> 1. **Deploy to production** (настроить CI/CD, Docker, автодеплой) → используй `/setup-infrastructure` + deployment guides
> 2. **Copy code for development** (просто скопировать код на VPS для работы с мобильного) → используй этот workflow

**Only proceed with this workflow if user confirms option 2 (copy for development).**

---

## Command Sequence

```bash
# On Mac
git push  # Ensure latest code is on GitHub

# On VPS
ssh claude-vps
cd ~/projects/
git clone <repo-url>
cd <project-name>
npm install  # or pip install, etc.

# Update registry
cd ~/.claude
nano projects-registry.json  # Add new project entry
git add projects-registry.json
git commit -m "Add <project-name> to VPS registry"
git push
```

---

## Detailed Steps

### Фаза 1: Prepare on Mac

Убедись, что последние изменения запушены на GitHub:

```bash
cd /path/to/project
git status
git add .
git commit -m "Latest changes before VPS copy"
git push
```

**Result:** Latest code is on GitHub remote.

---

### Фаза 2: SSH to VPS

```bash
ssh claude-vps
```

Or use alias:
```bash
vps-claude  # Auto-attaches to tmux session
```

**Result:** Connected to VPS in tmux session.

---

### Фаза 3: Clone Project

Navigate to projects directory and clone:

```bash
cd /home/molyanov/projects/
git clone git@github.com:pavel-molyanov/<project-name>.git
cd <project-name>
```

**Verify clone:**
```bash
ls -la
git remote -v
```

**Result:** Project copied to VPS.

---

### Фаза 4: Install Dependencies

Depending on project type:

**Node.js:**
```bash
npm install
# or
npm ci
```

**Python:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Go:**
```bash
go mod download
```

**Result:** Dependencies installed, project ready for development.

---

### Фаза 5: Update Projects Registry

Update VPS projects registry to track the new project:

```bash
cd ~/.claude
nano projects-registry.json
```

Add new entry:
```json
{
  "name": "project-name",
  "path": "/home/molyanov/projects/project-name",
  "added": "2025-11-11",
  "description": "Brief description"
}
```

Commit and push:
```bash
git add projects-registry.json
git commit -m "Add project-name to VPS registry"
git push
```

**Result:** Registry updated and synced to GitHub.

---

## Result

✅ Project copied to VPS
✅ Dependencies installed
✅ Registry updated
✅ Ready for dual-environment development (Mac + VPS)

---

## Daily Sync Workflow

### Auto-sync with SessionStart Hook

**When launching Claude Code** (on Mac or VPS):
- `~/.claude/` syncs automatically from GitHub
- Current project syncs automatically from its own GitHub

**After working on Mac:**
```bash
git push  # Push changes to GitHub
```

**On VPS:**
```bash
vps-claude  # Auto-syncs on SessionStart
# OR manually:
cd ~/projects/<project-name>
git pull
```

**After working on VPS:**
```bash
git push  # Push changes to GitHub
```

**On Mac:**
```bash
claude  # Auto-syncs on SessionStart
# OR manually:
git pull
```

**Note:** Auto-sync skips if uncommitted changes detected (shows warning instead).

---

## Troubleshooting

### SSH Connection Issues

See [vps-setup.md](vps-setup.md#ssh-connection-issues) for detailed SSH troubleshooting.

**Quick fixes:**
- Check SSH key: `ls -la ~/.ssh/claude_code_vps`
- Test connection: `ssh -T git@github.com`
- Use alias: `vps` or `vps-claude`

### Git Clone Fails

**Problem:** `Permission denied (publickey)` when cloning

**Solution:**
1. Check GitHub SSH key is added to VPS:
   ```bash
   ssh claude-vps
   ssh -T git@github.com
   ```
2. Should see: "Hi pavel-molyanov!"
3. If not, add VPS SSH key to GitHub: https://github.com/settings/keys

### npm install Fails

**Problem:** `npm: command not found`

**Solution:**
```bash
echo $PATH  # Check if ~/.npm-global/bin is in PATH
source ~/.bashrc  # Reload environment
node -v  # Verify Node.js installed (should be 20.19.5)
```

### tmux Session Lost

**Problem:** Lost connection, can't find work

**Solution:**
```bash
ssh claude-vps
tmux ls  # List all sessions
tmux attach -t claude  # Attach to claude session
# Or use alias:
tm
```

---

## Related Documentation

- [vps-setup.md](vps-setup.md) - VPS reference guide (server info, SSH config, troubleshooting)
- [workflow-feature-dev.md](workflow-feature-dev.md) - Daily feature development workflow
- [folder-structure.md](folder-structure.md) - Project structure and organization

---

**Last Updated:** 2025-11-11
**Use Case:** Dual-environment development (Mac + VPS)
**NOT for:** Production deployment (use `/setup-infrastructure` instead)
