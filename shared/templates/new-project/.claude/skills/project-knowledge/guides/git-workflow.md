# Git Workflow Strategy

## Purpose
This file defines the git branching strategy and workflow for the project. Helps AI agents understand when to create feature branches vs. commit directly, testing requirements per branch, and merge rules.

---

## Branch Structure

### Main Branches
- **`main`** - Production-ready code (protected)
  - Always stable
  - Only merge from `dev` after full testing
  - Triggers production deployment

- **`dev`** - Active development and integration
  - Integration branch for all work
  - May be temporarily unstable
  - Triggers staging deployment

### Feature Branches (Optional)
- **`feature/XXX-name`** - For complex features
  - Created from `dev`
  - Merged back to `dev` via PR
  - Deleted after merge

---

## Branch Decision Criteria

When creating Tech Spec, analyze User Spec and decide:

### Direct to `dev`:
- Bug fixes
- Single file changes
- Simple improvements
- Documentation updates
- Config changes
- No breaking changes
- No new dependencies

### Feature branch `feature/XXX-name`:
- New features
- Multiple files affected
- Complex functionality from User Spec
- Breaking changes possible
- New dependencies (npm packages)
- External integrations (Stripe, SendGrid, APIs)
- Database schema changes
- Architecture changes

**Rule of thumb:** If unsure → use feature branch (safer)

---

## Testing Strategy

### On commit (any branch):
- Code changed → Unit + Integration tests (automatic)
- Docs only (`.claude/`, `.work/`, `*.md`) → Skip tests

### On merge to `dev`:
- Unit + Integration tests (automatic)
- E2E tests (optional, ask user)

### On merge to `main`:
- Unit + Integration tests (automatic)
- E2E tests (strongly recommended - ask user)

### Smoke Tests

**Status:** Placeholder (`assert True` - always passes)

**TODO:** Update when adding first real functionality:
- Test app imports successfully
- Test config loads
- Test basic initialization

Until updated, smoke tests don't catch startup/import errors.

---

## Security & Quality Gates

**Before every commit:**
- Gitleaks pre-commit hook automatically scans for secrets (API keys, tokens, credentials)
- Commit blocked if secrets detected

**Before every push:**
- Code review agent validates changes
- All checks must pass before code reaches GitHub

---

## Repository Synchronization

**Auto-sync on SessionStart:**
When launching Claude Code in this project, the SessionStart hook automatically:
1. Syncs `~/.claude/` meta-project from GitHub (commands, skills, agents)
2. Syncs current project from its own GitHub repository

**How it works:**
- Script: `~/.claude/scripts/sync-from-github.sh`
- Performs `git pull` on current branch
- Non-blocking: skips sync if uncommitted changes detected
- Shows clear status messages (✓ up to date, ⚠️ uncommitted changes)

**Manual sync:**
If auto-sync was skipped due to uncommitted changes, manually sync:
```bash
git pull origin <branch-name>
```
