# Troubleshooting Guide

## Common Issues Across All Workflows

### GitHub Authentication

**Problem:** GitHub authentication fails when running `/init-git` or other GitHub operations.

**Symptoms:**
- Error: "gh: command not found"
- Error: "Not logged in to github.com"
- Error: "Token validation failed"

**Solutions:**
1. Check gh CLI installed:
   ```bash
   gh --version
   ```
   If not installed: `brew install gh` (macOS) or see https://cli.github.com

2. Check authentication status:
   ```bash
   gh auth status
   ```

3. If not authenticated:
   ```bash
   gh auth login
   ```
   - Choose: GitHub.com
   - Protocol: HTTPS or SSH
   - Authenticate: Web browser or token

4. If token expired:
   - Generate new Personal Access Token on GitHub
   - Settings → Developer settings → Personal access tokens
   - Required scopes: `repo`, `workflow`, `admin:public_key`

---

### Context7 Unavailable

**Problem:** Context7 MCP server not available when agent tries to fetch documentation.

**Symptoms:**
- Warning: "Context7 unavailable, using agent knowledge (cutoff January 2025)"
- Error: "MCP server context7 not found"

**Solutions:**
1. Check MCP servers:
   ```bash
   claude mcp list
   ```

2. If Context7 not listed:
   - Open Claude desktop app
   - Settings → MCP Servers
   - Add Context7 server
   - Restart Claude

3. If listed but not working:
   - Restart Claude desktop app
   - Check internet connection

**Fallback:** Agent uses own knowledge and warns about knowledge cutoff

---

### Pre-commit Hooks Not Working

**Problem:** Pre-commit hooks don't run when committing.

**Symptoms:**
- Can commit secrets without warning
- gitleaks doesn't scan
- No hook output during `git commit`

**Solutions:**
1. Check hooks installed:
   ```bash
   ls -la .git/hooks/
   # Should see: pre-commit file
   ```

2. Check executable permissions:
   ```bash
   chmod +x .git/hooks/pre-commit
   ```

3. If hooks missing:
   - Node.js project: `npm install` (installs husky)
   - Python project: `pre-commit install`

4. Test manually:
   ```bash
   .git/hooks/pre-commit
   ```

5. If all else fails:
   ```bash
   rm -rf .git/hooks
   git init  # Reinitialize hooks
   npm install  # or pre-commit install
   ```

---

### CI/CD Pipeline Fails

**Problem:** GitHub Actions pipeline fails after push.

**Symptoms:**
- Red X on GitHub commit
- Build fails in Actions tab
- Tests fail in CI

**Solutions:**
1. Check GitHub Actions secrets configured:
   - Repository → Settings → Secrets and variables → Actions
   - Verify all required secrets exist (from `deployment.md`)

2. Check `.env.example` is up to date:
   - All env vars documented
   - No missing variables

3. Check workflow syntax:
   ```bash
   cat .github/workflows/ci.yml
   # Look for YAML syntax errors
   ```

4. Run tests locally:
   ```bash
   npm test  # or pytest
   # If fails locally, fix tests first
   ```

5. Check logs in GitHub Actions:
   - Click on failed workflow
   - Expand failed step
   - Read error message

---

## New Project Workflow Issues

### Framework Initialization Fails

**Problem:** Framework init command fails (Next.js, Express, etc).

**Symptoms:**
- Error: "command not found"
- Error: "unsupported Node.js version"
- Timeout during installation

**Solutions:**
1. Check Node.js/Python version:
   ```bash
   node -v   # Should be LTS (18+)
   python --version  # Should be 3.9+
   ```

2. Update to LTS version:
   - Node.js: Use nvm: `nvm install --lts`
   - Python: Use pyenv: `pyenv install 3.11`

3. Clear cache:
   ```bash
   npm cache clean --force
   # or
   pip cache purge
   ```

4. Try manual init:
   ```bash
   npx create-next-app@latest .
   # or
   pip install fastapi uvicorn
   ```

---

### Git Repository Already Exists

**Problem:** `/init-git` fails because git repo already exists.

**Solution:**
Skip `/init-git` if you already have a GitHub repository.
- Use existing remote
- Or remove `.git/` and run `/init-git` to start fresh

---

### Context Files Empty

**Problem:** After `/init-context`, some context files are empty or incomplete.

**Solutions:**
1. Fill manually:
   - Open `.claude/skills/project-knowledge/guides/architecture.md`
   - Add missing information
   - Git commit

2. Re-run with more details:
   ```bash
   # Provide more detailed answers in interview
   /init-context
   ```

3. Check if Context7 was available:
   - If unavailable, tech stack might not be validated
   - Manually verify technologies are current

---

## Onboarding Workflow Issues

### Legacy Code Too Large

**Problem:** `/old-project` takes too long or runs out of memory.

**Symptoms:**
- Command hangs
- Out of memory error
- Takes >5 minutes

**Solutions:**
1. Check what's being moved:
   ```bash
   du -sh *
   # Look for huge folders
   ```

2. Clean before `/old-project`:
   ```bash
   # Remove build artifacts
   rm -rf dist/ build/ .next/

   # Remove dependencies (will reinstall)
   rm -rf node_modules/

   # Remove large media (if not needed)
   rm -rf public/uploads/
   ```

3. Update `.gitignore` before `/old-project`:
   - Add patterns for large folders
   - `/old-project` respects .gitignore

---

### Git History Lost

**Problem:** Fear that git history will be lost after `/old-project`.

**Answer:** **Impossible.** `/old-project` only moves files, doesn't touch `.git/` folder.

**Verify:**
```bash
git log  # All commits still there
git status  # See moved files
```

**If you need rollback:**
```bash
git reset --hard HEAD~1  # Undo last commit
```

---

### old-folder-audit Not Running

**Problem:** `/old-folder-audit` fails or doesn't create report.

**Symptoms:**
- Error: "old/ folder not found"
- Error: "No files to analyze"
- Empty audit report

**Solutions:**
1. Check `old/` folder exists:
   ```bash
   ls old/
   # Should contain your legacy code
   ```

2. If empty:
   - Run `/old-project` first
   - `/old-folder-audit` requires `old/` folder

3. If Context7 error:
   - Audit will be created without tech validation
   - Manually verify tech stack is current

4. If audit is shallow:
   - Provide more context in CLAUDE.md
   - Run again with specific focus areas

---

### Can't Delete Migration Branch

**Problem:** Want to delete `feature/migration-ai-first` branch but command fails.

**Why:** It's okay to keep this branch for rollback reference.

**If you must delete:**
1. Merge to main first:
   ```bash
   git checkout main
   git merge feature/migration-ai-first
   git push
   ```

2. Verify everything works

3. Delete branch:
   ```bash
   git branch -D feature/migration-ai-first
   git push origin --delete feature/migration-ai-first
   ```

---

### CI/CD Fails on Legacy Code

**Problem:** After `/setup-infrastructure-old`, CI fails because legacy code doesn't pass tests.

**Answer:** **Expected behavior.**

**Solutions:**
1. Don't block on legacy tests:
   - Edit `.github/workflows/ci.yml`
   - Make tests non-blocking: `continue-on-error: true`

2. Create refactoring tasks:
   - Use `/new-feature` to create refactoring tasks
   - Fix tests gradually

3. Focus on new code:
   - Ensure new features pass tests
   - Legacy code can fail temporarily

---

## Feature Development Issues

### Feature Not Found

**Problem:** Commands can't find feature folder.

**Symptoms:**
- Error: "Feature 'payment-integration' not found"
- Error: "work/ folder empty"

**Solutions:**
1. Check feature name:
   ```bash
   ls work/
   # Should see: feature-name/
   ```

2. Check naming convention:
   - Must be: `lowercase-with-dashes`
   - NOT: `CamelCase`, `snake_case`, `spaces`

3. If spaces in name:
   ```bash
   mv "Payment Integration" payment-integration
   ```

4. If `work/` empty:
   - Run `/new-feature` first

---

### User Spec Not Detailed Enough

**Problem:** `/create-tech-spec` says User Spec lacks details.

**Symptoms:**
- Error: "User Spec doesn't have enough information"
- Agent asks for more details

**Solutions:**
1. Check user-spec.md has:
   - ✅ Problem statement
   - ✅ Expected solution
   - ✅ Acceptance criteria
   - ✅ Constraints (if any)

2. Re-run `/new-feature` with more details

3. Edit user-spec.md manually:
   - Add missing sections
   - Git commit
   - Run `/create-tech-spec` again

---

### Tasks Too Large

**Problem:** Tasks take >4 hours to complete.

**Solutions:**
1. Re-run decomposition:
   ```bash
   /tech-spec-decompose feature-name
   # Ask: "Break tasks into smaller pieces (1-2 hours each)"
   ```

2. Manual split:
   - Edit `tasks/*.md`
   - Split large task into 2-3 smaller tasks
   - Renumber: `1.md`, `2.md`, `3.md`, ...

**Rule of thumb:** One task = one commit = 1-3 hours work

---

### Tests Failing

**Problem:** code-developer writes code but tests fail.

**Symptoms:**
- Unit tests fail
- Integration tests fail
- Agent can't fix automatically

**Solutions:**
1. Check test environment:
   ```bash
   # Node.js
   npm test
   # Python
   pytest
   ```

2. Check env variables:
   ```bash
   cat .env.example
   # Verify all variables set in .env
   ```

3. Check database:
   - Test database accessible?
   - Schema up to date?
   - Test data seeded?

4. If test logic wrong:
   - Update task description with correct expectations
   - Re-run `/start-task`

5. If agent stuck:
   - Manually fix tests
   - Git commit
   - Continue with next task

---

### Code Reviewer Finds Critical Issues

**Problem:** code-reviewer finds critical problems after implementation.

**Scenarios:**

**Single Task Mode:**
1. code-developer automatically fixes
2. code-reviewer re-checks
3. Repeat until pass

**Feature Autopilot Mode:**
1. Rollback to task commit
2. code-developer re-implements
3. Checks repeat

**If disagree with reviewer:**
- Update `.claude/skills/project-knowledge/guides/patterns.md` with your rules
- Re-run review (will use your patterns)

---

### Feature Branch Conflicts with Main

**Problem:** Can't merge feature branch - conflicts with main.

**Solutions:**
1. Before starting feature:
   ```bash
   git pull origin main
   # Resolve conflicts before `/start-feature`
   ```

2. During feature work:
   - Don't merge other features into main
   - Wait until current feature complete

3. After feature complete:
   ```bash
   git checkout feature-branch
   git pull origin main
   git merge main
   # Resolve conflicts
   git push
   ```

---

### E2E Tests Not Running

**Problem:** E2E tests fail to execute.

**Symptoms:**
- Browser doesn't launch
- Timeout errors
- Connection refused

**Solutions:**
1. Check dev server running:
   ```bash
   npm run dev  # or your dev command
   # Server should be accessible
   ```

2. Check env variables:
   - All secrets configured?
   - Database accessible?
   - External services (Stripe sandbox) set up?

3. Check test infrastructure:
   - Playwright/Cypress installed?
   - Browsers installed?

4. If no E2E infrastructure:
   - Skip E2E tests
   - Use manual testing instead
   - Document in tech-spec: "E2E Tests: None (manual testing)"

---

## General Debugging Steps

### When Command Fails

1. **Read the error message**
   - What exactly failed?
   - What file/command mentioned?

2. **Check prerequisites**
   - Did previous commands complete?
   - Are required files present?

3. **Check context**
   - Are context files filled?
   - Is git repository initialized?

4. **Try manual alternative**
   - Can you do it manually?
   - What command would you run?

5. **Check documentation**
   - Read workflow guide
   - Check command sequence

---

### When Agent Stuck

1. **Simplify the ask**
   - Break into smaller steps
   - One task at a time

2. **Provide more context**
   - Update context files
   - Add details to task description

3. **Manual intervention**
   - Fix the issue yourself
   - Git commit
   - Ask agent to continue

4. **Start fresh**
   - Rollback to known good state
   - Try different approach

---

### When Results Unexpected

1. **Check specs**
   - Does implementation match user-spec?
   - Does user-spec match your intent?

2. **Update specs**
   - Fix user-spec if wrong
   - Re-run `/create-tech-spec`
   - Re-run `/tech-spec-decompose`

3. **Manual review**
   - Read generated code
   - Check if it makes sense
   - Test manually

---

## Getting Help

### Before Asking

1. ✅ Read this troubleshooting guide
2. ✅ Check workflow guide for your scenario
3. ✅ Try suggested solutions
4. ✅ Check GitHub Actions logs (if CI issue)
5. ✅ Try manually to understand the issue

### When Asking Agent

Provide:
- What command you ran
- What error you got
- What you expected
- What you already tried
- Relevant file contents

### When Reporting Bug

Include:
- Workflow you're using
- Command that failed
- Full error message
- System info (OS, Node.js version, etc.)
- .claude/skills/project-knowledge/guides/ structure
- Git status

---

## Preventive Measures

### Before Starting Project

- ✅ Check Node.js/Python version (LTS)
- ✅ Authenticate gh CLI
- ✅ Test Context7 available
- ✅ Clean directory (no leftover files)

### Before Each Feature

- ✅ Pull latest from main
- ✅ Check context files up to date
- ✅ Review existing features for patterns
- ✅ Plan task breakdown carefully

### After Each Task

- ✅ Run tests locally
- ✅ Check git status (no untracked secrets)
- ✅ Review code diff before commit
- ✅ Update context if needed

---

## Emergency Procedures

### Rollback Feature
```bash
# Find feature start commit
git log --oneline | grep "feat: start"

# Rollback to before feature
git reset --hard <commit-hash>

# Force push (if already pushed)
git push --force origin feature-branch
```

### Rollback Single Task
```bash
# Find task commit
git log --oneline | grep "feat: task"

# Revert specific commit
git revert <commit-hash>

# Or reset to before task
git reset --hard <commit-hash>
```

### Reset to Main
```bash
# Nuclear option: discard all local work
git checkout main
git pull origin main
git branch -D feature-branch
```

### Recover Lost Changes
```bash
# If you accidentally reset
git reflog  # Find lost commit
git cherry-pick <commit-hash>
```

---

## FAQ

**Q: Can I skip `/init-project-discovery`?**
A: Yes, but you'll need to manually fill `project.md` before `/init-context`.

**Q: Can I use different tech stack than suggested?**
A: Yes, just specify your preferences in `/init-context` interview.

**Q: What if Context7 is unavailable?**
A: Agent uses own knowledge and warns about cutoff. Verify tech choices manually.

**Q: Can I merge multiple features at once?**
A: Better to merge and deploy one by one. Easier to debug issues.

**Q: Should I always use Feature Autopilot?**
A: No. Use Single Task Mode for complex/unclear tasks. Autopilot for clear tasks.

**Q: What if tests take too long?**
A: Move long tests (E2E, integration) to separate tasks. Run after main implementation.

**Q: Can I skip code review?**
A: Not recommended. code-reviewer catches issues before they become bugs.

**Q: What if I disagree with security-auditor?**
A: Review findings carefully. If false positive, document why it's safe.

**Q: How do I handle urgent hotfix?**
A: Use `/new-feature` with type "bug", keep it small (1-2 tasks), deploy fast.

**Q: Can I use workflows in parallel projects?**
A: Yes, methodology works identically across all AI-First projects.
