# Infrastructure Troubleshooting Guide

## Common Problems and Solutions

### 1. Secrets Leaked to Git

**Problem:** Accidentally committed `.env` or API keys to git.

**Solution:**
```bash
# 1. Remove from git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# 2. Force push (⚠️ coordinate with team)
git push origin --force --all

# 3. Rotate compromised secrets immediately
# - Regenerate API keys
# - Update in deployment platform
# - Update locally

# 4. Add to .gitignore
echo ".env" >> .gitignore
git add .gitignore
git commit -m "chore: add .env to .gitignore"
```

**Prevention:**
- Always verify: `git check-ignore .env` returns `.env`
- Use pre-commit hooks (gitleaks)
- Never disable pre-commit hooks

---

### 2. Pre-commit Hooks Too Slow

**Problem:** Pre-commit hook takes >30 seconds, slowing development.

**Symptoms:**
```bash
git commit -m "fix: ..."
# ... waiting ... waiting ... 45 seconds later ...
```

**Solution:**

**Identify slow hooks:**
```bash
time git commit -m "test"  # See what takes time
```

**Remove slow checks:**
- ❌ Don't run full test suite in pre-commit
- ❌ Don't run full build in pre-commit
- ❌ Don't run integration tests

**Keep only fast checks (<10 seconds total):**
- ✅ gitleaks (~2-5 seconds)
- ✅ Lint on staged files only (~3-5 seconds)
- ✅ Type check if fast (<5 seconds)

**For Node.js (Husky):**
```bash
# .husky/pre-commit
#!/bin/sh
gitleaks detect --staged --verbose --no-banner
npx lint-staged  # Only lints staged files
```

**For Python:**
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff  # Fast linter
        args: [--fix]
```

---

### 3. CI Fails But Tests Pass Locally

**Problem:** Tests pass on your machine but fail in CI.

**Common causes:**

**A. Environment differences:**
```bash
# Local: Uses .env file
# CI: Doesn't have .env

# Solution: Add env vars to CI secrets
```

**B. Missing dependencies:**
```bash
# Local: npm install (might install extra deps)
# CI: npm ci (strict install)

# Solution: Ensure package-lock.json is committed
git add package-lock.json
git commit -m "chore: update lockfile"
```

**C. Different Node/Python versions:**
```bash
# Check versions
node --version  # Local
# vs GitHub Actions: uses actions/setup-node@v4 with version: '20'

# Solution: Match versions in workflow
```

**D. Timezone/locale differences:**
```javascript
// Test uses local timezone
expect(date.toString()).toBe('Mon Jan 01 2024 ...')

// Solution: Use UTC or mock time in tests
```

**Debug in CI:**
```yaml
- name: Debug environment
  run: |
    node --version
    npm --version
    env | sort
```

---

### 4. .env Not Being Ignored

**Problem:** Git wants to commit `.env` file.

**Check current status:**
```bash
git status
# Shows: .env (should not appear if properly ignored)

git check-ignore .env
# Should return: .env
# If returns nothing: .env is NOT ignored
```

**Solution:**
```bash
# 1. Add to .gitignore
echo ".env" >> .gitignore

# 2. Remove from git tracking (if already tracked)
git rm --cached .env

# 3. Commit .gitignore update
git add .gitignore
git commit -m "chore: add .env to .gitignore"

# 4. Verify
git check-ignore .env  # Should return: .env
```

**Pattern to ignore all .env variants:**
```gitignore
.env
.env.*
!.env.example
```

---

### 5. Docker Build Fails

**Problem A: Dependencies not found**
```
ERROR: Cannot find module 'express'
```

**Solution:**
```dockerfile
# Ensure package files copied BEFORE npm install
COPY package*.json ./
RUN npm install

# Then copy source
COPY . .
```

**Problem B: .env files in image**
```dockerfile
# Bad: Copies .env into image
COPY . .

# Solution: Use .dockerignore
echo ".env" >> .dockerignore
```

**Problem C: Build context too large**
```
Sending build context to Docker daemon: 2.5GB
```

**Solution:** `.dockerignore`
```
node_modules/
.git/
.next/
dist/
coverage/
*.log
```

**Test locally:**
```bash
docker build -t test-image .
docker run -p 3000:3000 test-image
```

---

### 6. GitHub Actions Secrets Not Working

**Problem:** Workflow fails with "secret not found" or null values.

**Common mistakes:**

**A. Wrong secret name:**
```yaml
# Wrong (typo)
${{ secrets.VERCEL_TOKN }}

# Correct
${{ secrets.VERCEL_TOKEN }}
```

**B. Secret added to wrong scope:**
- Organization secrets: Check repository access
- Repository secrets: Verify you're in correct repo

**C. Secret contains newlines/spaces:**
```bash
# Bad (trailing newline)
echo "my-secret-key
" | gh secret set MY_SECRET

# Good (no newline)
echo -n "my-secret-key" | gh secret set MY_SECRET
```

**Debug:**
```yaml
- name: Check secrets exist
  run: |
    if [ -z "${{ secrets.VERCEL_TOKEN }}" ]; then
      echo "VERCEL_TOKEN is not set"
      exit 1
    fi
```

---

### 7. Smoke Test Doesn't Run

**Problem:** Test framework can't find test file.

**Node.js (Jest/Vitest):**
```bash
# Check test file naming
tests/smoke.test.ts  ✅
tests/smoke.spec.ts  ✅
tests/smokeTest.ts   ❌ (missing .test)

# Verify jest config
# package.json
{
  "jest": {
    "testMatch": ["**/*.test.ts"]
  }
}
```

**Python (pytest):**
```bash
# Check test file naming
tests/test_smoke.py  ✅
tests/smoke_test.py  ❌ (must start with test_)

# Verify pytest config
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
```

**Verify manually:**
```bash
npm test
# or
pytest -v
```

---

### 8. Deployment Fails After Tests Pass

**Platform-specific solutions:**

**Vercel:**
```bash
# Check build command
npm run build  # Must succeed locally

# Verify vercel.json if exists
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next"
}
```

**Railway:**
```bash
# Check start command in package.json
{
  "scripts": {
    "start": "node dist/index.js"
  }
}

# Or set in Railway dashboard
```

**Fly.io:**
```bash
# Check fly.toml
[http_service]
  internal_port = 3000  # Must match app port

# Test Docker image locally
docker build -t test .
docker run -p 3000:3000 test
```

**AWS ECS:**
```bash
# Check task definition port mapping
# Check security group allows inbound traffic
# Check target group health checks
```

---

### 9. Framework Not Starting

**Next.js:**
```bash
# Check port
PORT=3000 npm run dev

# Check dependencies
rm -rf node_modules package-lock.json
npm install
```

**FastAPI:**
```bash
# Check Python version
python --version  # Must be 3.7+

# Check uvicorn installed
pip install uvicorn
uvicorn src.main:app --reload
```

**Express:**
```bash
# Check port not in use
lsof -i :3000
kill -9 <PID>

# Start
npm run dev
```

---

### 10. CI Runs on Documentation Changes

**Problem:** GitHub Actions runs tests when only `.md` files changed.

**Solution:** Check skip-docs logic in workflow.

**Correct pattern:**
```yaml
- id: check
  run: |
    FILES=$(git diff --name-only HEAD^ HEAD)
    if echo "$FILES" | grep -qvE '\.(md|txt)$|^\.claude/|^docs/'; then
      echo "skip=false" >> $GITHUB_OUTPUT
    else
      echo "skip=true" >> $GITHUB_OUTPUT
    fi
```

**Test manually:**
```bash
# Make doc-only change
echo "test" >> README.md
git add README.md
git commit -m "docs: update readme"
git push

# Check Actions tab - should skip tests
```

---

## Debug Checklist

When infrastructure fails, check in this order:

1. **Secrets & Environment Variables**
   - [ ] All required secrets configured
   - [ ] No typos in secret names
   - [ ] Values are correct (no trailing newlines)

2. **Dependencies**
   - [ ] Lockfile committed (package-lock.json, requirements.txt)
   - [ ] Dependencies installed (`npm ci` not `npm install`)
   - [ ] Versions match between local and CI

3. **Configuration Files**
   - [ ] .gitignore properly configured
   - [ ] .env not committed
   - [ ] Framework config files present (next.config.js, etc.)

4. **Tests**
   - [ ] Test files named correctly
   - [ ] Test framework configured
   - [ ] Tests pass locally
   - [ ] No environment-specific test code

5. **Build & Deployment**
   - [ ] Build succeeds locally
   - [ ] Docker image builds (if using Docker)
   - [ ] Deployment platform configured
   - [ ] Health checks passing

6. **Permissions**
   - [ ] Git pre-commit hook executable (`chmod +x .husky/pre-commit`)
   - [ ] Docker user has correct permissions
   - [ ] IAM roles configured (AWS)
