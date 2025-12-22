# Backlog Management Guide

## Where Backlogs Live

### Global Level (~/.claude/)
- **backlog.md** - methodology improvements (skills, commands, infrastructure)
- **project-ideas.md** - ideas for new projects (before they start)

### Project Level (my-project/)
- **backlog.md** - feature ideas and bugs for the project

## Format

Simple list. No checkboxes. When done - delete the line.

```markdown
# Project Backlog

## Features
- CSV export for clients
- Telegram integration
- Analytics dashboard

## Bugs
- Slow loading with 100+ clients
- Email validation issues
```

## Workflow

1. **New project idea** → add to `~/.claude/project-ideas.md`
2. **Ready to start** → `/init-project` → creates project with `backlog.md`
3. **New feature idea** → add to `project/backlog.md`
4. **Ready to implement** → move to `work/` via `/new-feature`
5. **Done** → delete from backlog

## Key Principles

- **No formalization** - write freely, no templates
- **No commands** - just create files and write
- **Simple text** - easy to read and edit
- **Git-friendly** - version controlled with code
