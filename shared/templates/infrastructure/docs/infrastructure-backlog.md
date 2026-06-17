# Infrastructure Migration Plan

<!-- LLM: Insert current date in format: YYYY-MM-DD -->
**Created:** [DATE]
**Status:** Infrastructure ready in dev, deployment pending

---

## Current State

<!-- LLM: Describe what's configured in dev branch based on what was actually created.
List items like:
- ✅ CI/CD for testing (specify which jobs: lint, type-check, tests, build)
- ✅ Docker for local development (specify: dev only or dev+prod)
- ✅ Pre-commit hooks (gitleaks or others)
- ✅ Testing infrastructure (specify framework: Vitest/pytest/etc)
- ✅ Folder structure for new code (src/, tests/, etc)
-->

**dev branch:**
[LLM: List configured infrastructure items here]

**main branch:**
- ⚠️ **UNTOUCHED** (production keeps running)
- Existing workflows NOT changed

---

## Migration Steps

### Step 1: Refactoring in dev

**Current stage:** Developing and refactoring legacy code from `old/` into the new `src/` structure

**TODO:**
- [ ] Refactor code (use `/new-feature` for each feature)
- [ ] Test coverage
- [ ] Code review
- [ ] All tests pass

---

### Step 2: Deploy Setup (dev → staging)

**After refactoring is complete:**

1. **Set up deployment for dev→staging:**

<!-- LLM: Read .claude/skills/project-knowledge/references/deployment.md and fill deployment info:
- Platform (VPS/Railway/Vercel/Fly.io/etc)
- If VPS: SSH access details, server IP for staging
- If cloud platform: specify which one
- Environment name for staging
-->
   **Platform:** [LLM: Insert platform from deployment.md]

   **Staging environment:** [LLM: Insert staging env details from deployment.md]

2. **Update CI/CD for dev:**
   - Add a deployment job for dev branch → staging
   - Add GitHub secrets (see below)

3. **Create production Docker config (if not already present):**
   - `docker-compose.prod.yml` (multi-stage build, optimized)

4. **Test on staging:**
   - Push to dev → auto-deploy to staging
   - Smoke tests, integration tests
   - User acceptance testing

<!-- LLM: Read .claude/skills/project-knowledge/references/deployment.md and list required GitHub Secrets.
Format as markdown list with secret names and descriptions.
Example:
- SSH_PRIVATE_KEY - for deploying to the VPS
- SERVER_IP_STAGING - staging server IP address
- DATABASE_URL - connection string for the staging DB
-->
**GitHub Secrets to add (Settings → Secrets → Actions):**

[LLM: List required secrets from deployment.md here]

---

### Step 3: Merge dev → main (Production)

**⚠️ ONLY after full testing on staging!**

1. **Make sure staging is stable:**
   - [ ] No critical bugs
   - [ ] Performance acceptable
   - [ ] User acceptance testing passed

2. **Merge dev → main:**
   ```bash
   git checkout main
   git merge dev
   git push origin main
   ```

3. **Set up deployment main→production:**
   - Update `.github/workflows/ci.yml`
   - Add a deployment job for main branch → production
   - Add production secrets to GitHub

<!-- LLM: Read .claude/skills/project-knowledge/references/deployment.md and suggest appropriate deployment strategy.
Consider project size, traffic, downtime tolerance.
Default for small projects: simple deployment
For larger projects: suggest blue-green or canary
-->
4. **Deployment strategy:**

   [LLM: Recommend deployment strategy based on project from deployment.md]

   - [ ] Blue-green deployment (zero downtime, requires 2x resources)
   - [ ] Canary release (gradual rollout, more complex)
   - [ ] Rolling deployment (update one instance at a time)
   - [ ] Simple deployment (small projects, short downtime ok)

<!-- LLM: Read .claude/skills/project-knowledge/references/deployment.md and suggest monitoring setup.
Include what monitoring tools/services are mentioned or recommend appropriate ones.
-->
5. **Monitoring after deploy:**

   [LLM: List monitoring setup from deployment.md or suggest appropriate tools]

   - [ ] Health checks
   - [ ] Error tracking
   - [ ] Performance monitoring
   - [ ] Logs

---

## Rollback Plan

<!-- LLM: Read .claude/skills/project-knowledge/references/deployment.md for rollback procedures.
If not specified there, provide standard git-based rollback for the platform.
-->

**IF something goes wrong on staging:**
- `git revert` the problematic commit in dev
- Push to dev → auto-deploy the fix

**IF something goes wrong on production:**

[LLM: Insert rollback procedure from deployment.md, or provide platform-specific default]

---

## Notes

- 📝 This document is updated as the migration progresses
- ✅ All work happens in dev, then merge to main for production
