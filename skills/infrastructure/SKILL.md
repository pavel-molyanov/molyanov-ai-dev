---
name: infrastructure
description: |
  Setup dev infrastructure: CI/CD, testing, Docker, pre-commit hooks, auto-deploy.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "настрой инфраструктуру", "подготовь деплой", "настрой автодеплой", "настрой тесты", "настрой проверки при коммите", "настрой проверки при пуше"

  Do NOT use for: methodology (use methodology skill), running tests (answer directly)
---

# Infrastructure Setup Skill

## Overview

This skill provides comprehensive guidance for setting up development infrastructure for new projects. It covers framework initialization, folder structure, CI/CD pipelines, pre-commit hooks, testing infrastructure, and deployment configuration.

**Use this skill when:**
- Setting up a new project from scratch
- Adding CI/CD to an existing project
- Configuring testing infrastructure
- Setting up Docker containers
- Implementing security best practices (secret detection, .gitignore)

**For detailed examples and code snippets**, see `guides/` directory.

---

## Prerequisites

Before starting infrastructure setup, ensure these context files exist:
- `.claude/skills/project-knowledge/guides/architecture.md` - tech stack and framework choice
- `.claude/skills/project-knowledge/guides/patterns.md` - code patterns and conventions
- `.claude/skills/project-knowledge/guides/deployment.md` - deployment strategy
- `.claude/skills/project-knowledge/guides/git-workflow.md` - git branching strategy
- GitHub repository exists with remote configured

---

## Decision Framework

**Autonomous decisions** (no user input needed):
- Framework initialization commands (based on `architecture.md`)
- Folder structure (based on project type)
- Testing framework (based on project type)
- .gitignore patterns (based on framework)

**Ask user only when**:
- Docker setup not specified in context files
- Deployment target unclear in `deployment.md`
- Pre-commit hook strictness preference not documented

**Example questions:**
- "Do you need Docker for this project? (local dev, deployment, or both)"
- "Where will you deploy? (Vercel/Railway/AWS/Fly.io/other)"
- "Should pre-commit hooks block commits on any findings or just warn?"

---

## Step-by-Step Process

### 1. Framework Initialization

**Goal:** Get the framework running with standard configuration.

**Procedure:**
1. Read `architecture.md` to identify framework (Next.js, Express, FastAPI, etc.)
2. Run framework initialization command
3. Verify framework starts successfully (brief dev server test)
4. Check basic project structure is created

**Agent knows standard commands** - no need to specify exact flags unless documented in `architecture.md`.

---

### 2. Folder Structure (Separation of Concerns)

**Goal:** Organize code for maintainability and testability.

**Key principle:** Separate config, prompts, messages, and business logic.

**Standard structures:**
- **Web Apps:** `src/{components, services, lib, config, prompts, messages}` + `tests/{unit, integration, e2e}`
- **APIs:** `src/{routes, services, models, middleware, config, prompts}` + `tests/{unit, integration}`
- **CLI tools:** `src/{commands, services, config, prompts, messages}` + `tests/{unit, integration}`

**Why this matters:**
- Config in separate files → easy to change without code changes
- Prompts separated → iterate on prompts without touching code
- Messages extracted → easy translation and A/B testing
- Services layer → testable business logic independent of framework

**Action:** Create appropriate structure based on project type from `architecture.md`.

**For detailed examples**, see [guides/architecture-rationale.md](guides/architecture-rationale.md).

---

### 3. Docker Setup (Conditional)

**When:** Only if specified in context files or user confirms need.

**What to create:**
- Dockerfile (development and/or production)
- docker-compose.yml (if needed)
- .dockerignore

**Key decisions:**
- Local development vs production vs both
- Multi-stage builds for production (smaller images)
- Base image selection (alpine for minimal, slim for compatibility)

**For Dockerfile examples**, see [guides/docker-setup.md](guides/docker-setup.md).

---

### 4. GitHub Actions CI/CD

**Goal:** Automated testing and deployment on every push.

**What to create:** `.github/workflows/ci.yml`

**Key features:**
- Run lint, type-check, tests, build on every push
- Skip CI for documentation-only commits (`.md`, `.claude/`, `docs/`)
- Deploy based on target platform (read from `deployment.md`)

**Deployment platforms:**
- Vercel → use `vercel/actions`
- Railway → use `railway/deploy`
- AWS → use `aws-actions/configure-aws-credentials`
- Fly.io → use `superfly/flyctl-actions`
- Chrome Extension → create GitHub Release
- NPM package → publish to registry
- Other → tests only, manual deploy

**Important:** Document required secrets in `deployment.md`.

**For complete CI/CD workflow examples**, see [guides/github-actions.md](guides/github-actions.md).

**For deployment-specific guides**, see [guides/deployment-platforms.md](guides/deployment-platforms.md).

---

### 5. Pre-commit Hooks (gitleaks)

**Goal:** Prevent secrets from entering git history.

**Why gitleaks:**
- Fast (~2-5 seconds)
- Git enforces it (cannot bypass)
- Detects 95% of common secrets (API keys, tokens, credentials)
- Free (no LLM tokens)
- Replaces manual secret scanning before commits

**What gitleaks detects:**
- API keys (OpenAI `sk-...`, AWS `AKIA...`, Stripe `sk_live_...`)
- OAuth tokens (GitHub `ghp_...`)
- Private keys (`-----BEGIN PRIVATE KEY-----`)
- Database connection strings
- High-entropy strings (passwords)

**Implementation:**
- **Node.js projects:** Use husky + gitleaks
- **Python projects:** Use pre-commit + gitleaks

**Speed target:** Keep total pre-commit time under 10 seconds.

**Do NOT add to pre-commit:**
- ❌ Unit tests (too slow, agent runs in workflow)
- ❌ Integration tests (way too slow)
- ❌ Build (too slow, CI handles this)

**Can add (keep fast):**
- ✅ Linter on staged files only
- ✅ Type check if fast
- ✅ Format check

**For setup commands and examples**, see `templates/` directory.

---

### 6. .gitignore Updates (Security Critical)

**Goal:** Prevent committing sensitive files and build artifacts.

**ALWAYS add (security):**
```
.env
.env.*
!.env.example
*.key
*.pem
credentials.json
secrets/
*api-key*
*secret*
```

**Framework-specific patterns:**
- Read `architecture.md` to identify framework
- Add appropriate ignores (node_modules/, __pycache__/, dist/, etc.)

**Create .env.example:**
- Template showing required environment variables
- Commit this file (not .env itself)

**Validation:**
```bash
git check-ignore .env  # Should return: .env
```

---

### 7. Testing Infrastructure

**Goal:** Set up test framework with smoke test.

**Test framework selection:**
- Node.js → Jest or Vitest (read `architecture.md` for preference)
- Python → pytest
- Other → Framework-appropriate test runner

**Create smoke test:**
- Purpose: Verify project setup works, CI has something to run
- Minimal: 1-2 tests checking basic functionality
- Fast: Must run in milliseconds

**For smoke test templates**, see `templates/` directory.

**Configure test scripts:**
- package.json: `"test": "jest"` or `"test": "vitest"`
- pyproject.toml: Configure pytest testpaths

**Verify:** Run `npm test` or `pytest` - should pass.

---

### 8. Documentation Updates

**Update `deployment.md`:**
- Deployment commands
- Required environment variables list
- CI/CD pipeline details
- Secrets configuration instructions

**Update `git-workflow.md`:**
- CI/CD triggers (branches, pull requests)
- Pipeline jobs description
- Documentation-only commit skip logic
- Pre-commit hooks list

---

### 9. Commit Infrastructure

**Goal:** Commit all infrastructure setup to git.

**Commit message format:**
```
chore: setup project infrastructure

- Initialize [framework] project
- Configure CI/CD pipeline (GitHub Actions)
- Setup pre-commit hooks (gitleaks)
- Create folder structure (separation of concerns)
- Add testing infrastructure (smoke test)
- Configure .gitignore and .env.example
[- Setup Docker (if applicable)]

Infrastructure is ready for feature development.
```

**Verify before commit:**
```bash
git status  # Review what will be committed
git status | grep .env  # Should only show .env.example
```

**Push and verify:** Check GitHub Actions tab - CI should pass.

---

## Validation Checklist

After setup, verify:
- [ ] Framework runs locally
- [ ] Folder structure created with separation of concerns
- [ ] `.github/workflows/ci.yml` exists
- [ ] Pre-commit hook works (test with fake API key)
- [ ] `.gitignore` includes `.env`, `*.key`, secrets folders
- [ ] `.env.example` exists (if project uses env vars)
- [ ] Smoke test passes
- [ ] `deployment.md` updated with CI/CD and env vars
- [ ] `git-workflow.md` updated
- [ ] All infrastructure committed
- [ ] GitHub Actions CI passes
- [ ] Docker works (if applicable)

---

## Common Pitfalls

**For complete troubleshooting guide**, see [guides/troubleshooting.md](guides/troubleshooting.md).

**Quick tips:**
1. **Always verify** `.env` is in .gitignore: `git check-ignore .env`
2. **Keep pre-commit fast** - under 10 seconds total
3. **Document secrets** in deployment.md before configuring CI
4. **Test Docker locally** before pushing: `docker build -t test .`
5. **Verify smoke test** runs: `npm test` or `pytest`

---

## Bundled Resources

**Guides (detailed examples and procedures):**
- [docker-setup.md](guides/docker-setup.md) - Dockerfile and docker-compose examples
- [github-actions.md](guides/github-actions.md) - Complete CI/CD workflow YAML
- [deployment-platforms.md](guides/deployment-platforms.md) - Platform-specific deployment guides
- [troubleshooting.md](guides/troubleshooting.md) - Common problems and solutions
- [architecture-rationale.md](guides/architecture-rationale.md) - Why separation of concerns matters

**Templates (ready-to-use files):**
- [husky-pre-commit-gitleaks.sh](templates/husky-pre-commit-gitleaks.sh) - Pre-commit hook for Node.js
- [smoke.test.ts](templates/smoke.test.ts) - Smoke test template for TypeScript
- [test_smoke.py](templates/test_smoke.py) - Smoke test template for Python

---

## Related Skills

- **testing** - For detailed testing strategies (unit, integration, e2e)
- **command-manager** - For creating infrastructure-related slash commands

---

## Summary

This skill provides infrastructure setup for:
- ✅ Working framework with proper structure
- ✅ Automated CI/CD pipeline
- ✅ Secret detection (gitleaks)
- ✅ Testing infrastructure
- ✅ Deployment configuration
- ✅ Security best practices

After setup, project is ready for feature development.
