# Command Sequences: Quick Reference

## Command Categories

### Project Initialization Commands
- `/init-project` - Copy project template
- `/init-git` - Create GitHub repository
- `/init-project-discovery` - Product discovery interview
- `/init-context` - Fill context files (new project)
- `/init-context-old` - Fill context files (from audit)
- `/setup-infrastructure` - Setup framework + CI/CD
- `/setup-infrastructure-old` - Setup tests + CI/CD only

### Onboarding Commands
- `/old-project` - Archive old code, create structure
- `/old-folder-audit` - Analyze legacy code

### Feature Development Commands

**Planning Commands (New):**
- `/new-user-spec` - Create User Spec (uses user-spec-planning skill)
- `/new-tech-spec` - Create Tech Spec + Tasks (uses tech-spec-planning skill)

**Legacy Planning Commands:**
- `/new-feature` - Create User Spec (old)
- `/create-tech-spec` - Create Tech Spec from User Spec (old)
- `/tech-spec-decompose` - Decompose into tasks (old)

**Implementation Commands:**
- `/plan-task-waves` - Decompose into parallel waves
- `/start-task` - Start single task (manual mode)
- `/start-feature` - Start feature autopilot (sequential)
- `/start-feature-waves` - Start feature autopilot (parallel waves)

### Utility Commands
- `/project-context` - Load project context files
- `/meta-context` - Load meta-project context

---

## Complete Workflows

### 1. New Project Workflow

**Goal:** Create new project from scratch.

```bash
# Step 1: Create project structure locally
/init-project

# Step 2: Create GitHub repository
/init-git
# Input: repo name, description, public/private

# Step 3: Product discovery interview
/init-project-discovery
# Input: 3-15 questions, creates project.md

# Step 4: Technical planning
/init-context
# Input: tech stack preferences, creates 4 context files

# Step 5: Framework & DevOps setup
/setup-infrastructure
# Result: Framework initialized, CI/CD configured, tests ready
```

**Total time:** 30-60 minutes
**Output:** Fully initialized project ready for first feature

---

### 2. Onboarding Workflow

**Goal:** Migrate existing project to AI-First methodology.

```bash
# Step 1: Preserve legacy code
/old-project
# Result: All code moved to old/, new structure created

# Step 2: Product discovery interview
/init-project-discovery
# Input: 3-15 questions, creates project.md

# Step 3: Analyze legacy code
/old-folder-audit
# Result: Detailed audit report in old-folder-audit.md

# Step 4: Create context from audit
/init-context-old
# Result: 5 context files filled based on audit

# Step 5: Setup tests & CI/CD
/setup-infrastructure-old
# Result: Tests and CI/CD added (no framework init)
```

**Total time:** 60-90 minutes
**Output:** Migrated project ready for refactoring tasks
**Safety:** Works in separate branch `feature/migration-ai-first`

---

### 3. Feature Development Workflow (New Commands)

**Goal:** Implement feature using new simplified commands.

```bash
# Option A: Complex feature (user-spec needed)
# Step 1: Create User Spec through interview
/new-user-spec
# Input: Interview (adaptive 2-10 questions)
# Output: work/feature-name/user-spec.md

# Step 2: Create Tech Spec + Tasks
/new-tech-spec
# Input: Reads user-spec, asks clarifying questions (0-5) if needed
# Output: tech-spec.md + tasks/*.md

# Option B: Simple feature (skip user-spec)
# Step 1: Create Tech Spec + Tasks directly
/new-tech-spec
# Input: Your description of the task
# Output: tech-spec.md + tasks/*.md

# Step 3: Implement
/start-task feature-name 1
# OR
/start-feature feature-name
```

**Key improvements:**
- Simple command interface (/new-user-spec, /new-tech-spec)
- User-spec optional (skip for simple features)
- Tech-spec + tasks created together (not separate commands)
- Adaptive clarification (0-5 questions only if needed)
- One approval for tech-spec + tasks

---

### 5. Feature Development Workflow (Legacy - Single Task Mode)

**Goal:** Implement feature with manual control over each task using old commands.

**Note:** Consider using new skills workflow (section 3) instead.

```bash
# Step 1: Create User Spec
/new-feature
# Step 2: Create Tech Spec
/create-tech-spec feature-name
# Step 3: Decompose into tasks
/tech-spec-decompose feature-name
# Step 4: Implement tasks one by one
/start-task feature-name 1
/start-task feature-name 2
/start-task feature-name 3
# Step 5: Testing & Deploy
```

---

### 6. Feature Development Workflow (Legacy - Feature Autopilot)

**Goal:** Implement entire feature automatically using old commands.

**Note:** Consider using new skills workflow (section 3) instead.

```bash
# Steps 1-3: Same as above
/new-feature
/create-tech-spec feature-name
/tech-spec-decompose feature-name
# Step 4: Implement all tasks automatically
/start-feature feature-name
# Step 5: Testing & Deploy
```

---

### 7. Feature Development Workflow (Legacy - Parallel Waves)

**Goal:** Implement feature with parallel task execution using old commands.

**Note:** Consider using new skills workflow (section 3) instead.

```bash
# Steps 1-2: Same as above
/new-feature
/create-tech-spec feature-name
# Step 3: Decompose into parallel waves
/plan-task-waves feature-name
# Step 4: Implement all waves automatically
/start-feature-waves feature-name
# Step 5: Testing & Deploy
```

---

## Command Details

### /init-project

**Purpose:** Copy project template to current directory.

**Checks:**
- Git status (handles uncommitted changes)
- Directory not empty (warns)

**Creates:**
- `.claude/skills/project-knowledge/guides/` - 7 context file templates
- `work/` - work items folder
- `work/templates/` - spec templates
- `.gitignore` - security-focused
- `CLAUDE.md` - project instructions template
- `README.md` - project README template

**Does NOT:**
- Create git repository (use `/init-git`)
- Fill context files (use `/init-context`)
- Create GitHub remote (use `/init-git`)

**Next step:** `/init-git`

---

### /init-git

**Purpose:** Initialize git repo, create GitHub remote.

**Asks:**
- Repository name
- Description
- Public or private

**Does:**
- `git init` (if needed)
- Creates GitHub repository via `gh`
- Adds remote `origin`
- Initial commit
- Push to GitHub

**Requires:** `gh` CLI authenticated (`gh auth status`)

**Next step:** `/init-project-discovery`

---

### /init-project-discovery

**Purpose:** Product discovery interview, create project.md.

**Process:**
1. Adaptive interview (3-15 questions)
2. Creates `.claude/skills/project-knowledge/guides/project.md`
3. User reviews and approves
4. Agent iterates if needed
5. Git commit

**Questions cover:**
- Problem statement
- Target audience
- Core functionality
- MVP scope
- Constraints
- Success metrics

**Next step:** `/init-context` or `/init-context-old`

---

### /init-context

**Purpose:** Fill context files for NEW project.

**Asks:**
- Tech stack preferences
- Database choice
- Deployment target
- UI requirements

**Creates/updates:**
- `architecture.md` - tech stack with rationale
- `database.md` - database config (if applicable)
- `deployment.md` - deployment strategy
- `ux-guidelines.md` - UI guidelines (if applicable)

**Does NOT touch:**
- `patterns.md` (already well-filled in template)
- `git-workflow.md` (already well-filled in template)

**Uses Context7:** Validates tech stack is current

**Next step:** `/setup-infrastructure`

---

### /init-context-old

**Purpose:** Fill context files from legacy code audit.

**Requires:** `old-folder-audit.md` exists

**Creates/updates:**
- `architecture.md` - from audit (as-is)
- `database.md` - if DB found in audit
- `deployment.md` - current deployment from audit
- `ux-guidelines.md` - if UI found in audit

**Does NOT touch:**
- `patterns.md` (remains template)
- `git-workflow.md` (remains template)

**Next step:** `/setup-infrastructure-old`

---

### /setup-infrastructure

**Purpose:** Initialize framework, setup CI/CD, tests, Docker.

**Does:**
1. Initializes framework (Next.js/Express/FastAPI/etc)
2. Creates folder structure (separation of concerns)
3. Configures pre-commit hooks (gitleaks)
4. Sets up Docker (if needed)
5. Configures GitHub Actions CI/CD
6. Creates smoke test
7. Updates `deployment.md` and `git-workflow.md`
8. Git commit

**Autonomous decisions:** Based on `architecture.md`

**Asks only when:** Docker unclear, deployment target unclear

**Next step:** Start developing first feature (`/new-feature`)

---

### /setup-infrastructure-old

**Purpose:** Add tests and CI/CD to EXISTING project.

**Does:**
1. **Does NOT** initialize framework (already exists in `old/`)
2. Adds/updates Docker (if needed)
3. Configures GitHub Actions CI/CD
4. Configures pre-commit hooks (gitleaks)
5. Updates `.gitignore` (security)
6. Creates `.env.example`
7. Updates `deployment.md`
8. Git commit

**Key difference:** No framework init (unlike `/setup-infrastructure`)

**Next step:** Start refactoring tasks (`/new-feature`)

---

### /old-project

**Purpose:** Archive old code, initialize new AI-First structure.

**Does:**
1. Creates migration branch `feature/migration-ai-first`
2. Moves all files to `old/` (except .git, node_modules, build)
3. Runs `/init-project` (creates new structure)
4. Merges old .gitignore rules with `old/` prefix
5. Creates `old-folder-audit.md` template
6. Git commit (before and after)
7. Optionally pushes

**Safety:** Works in separate branch, doesn't touch main/production

**Next step:** `/old-folder-audit` or `/init-project-discovery`

---

### /old-folder-audit

**Purpose:** Analyze legacy code, create audit report.

**Requires:** `old/` folder exists

**Creates:** `old-folder-audit.md` with:
- Current tech stack
- Code quality assessment
- Security issues found
- Outdated dependencies
- Recommendations for migration

**Uses Context7:** Checks if technologies are current

**Next step:** `/init-context-old`

---

### /new-feature

**Purpose:** Create User Spec through interview.

**Process:**
1. Adaptive interview (2-10 questions)
2. Auto-detects type (feature/bug/refactoring)
3. Suggests feature name (lowercase-with-dashes)
4. Reads context (project.md, architecture.md)
5. Creates `work/feature-name/user-spec.md` (Russian)
6. User reviews and approves
7. Git commit and push

**Questions depend on type:**
- Feature: How should it work? For whom? MVP scope?
- Bug: How to reproduce? Expected vs actual? Severity?
- Refactoring: What's the problem? Expected result? Tests exist?

**Next step:** `/create-tech-spec feature-name`

---

### /create-tech-spec

**Purpose:** Create Tech Spec from User Spec.

**Usage:** `/create-tech-spec feature-name`

**Does:**
1. Validates user-spec exists and is detailed
2. Handles existing tech-spec (backup/overwrite/cancel)
3. Reads ALL 7 context files
4. Analyzes complexity (simple → dev branch, complex → feature branch)
5. Uses Context7 for best practices
6. Creates `tech-spec.md` (English) with:
   - Technical approach
   - Components to change
   - Database changes
   - API changes
   - Testing requirements
   - Edge cases
   - Task breakdown preview
7. User reviews and approves
8. Git commit and push

**Next step:** `/tech-spec-decompose feature-name`

---

### /tech-spec-decompose

**Purpose:** Break Tech Spec into atomic tasks.

**Usage:** `/tech-spec-decompose feature-name`

**Does:**
1. Reads tech-spec.md
2. Creates task files: `tasks/1.md`, `2.md`, ...
3. Tasks are:
   - Atomic (one commit each)
   - Incremental (non-breaking)
   - Testable
4. Integration/E2E tests = separate tasks
5. User reviews task breakdown
6. Git commit

**Next step:** `/start-task feature-name 1` or `/start-feature feature-name`

---

### /start-task

**Purpose:** Execute single task (manual mode).

**Usage:** `/start-task feature-name task-number`

**Does:**
1. Finds and validates task
2. Switches to feature branch (if exists)
3. Updates task status: `planned → in_progress`
4. Launches **code-developer** (code + unit tests)
5. Updates task status: `in_progress → done`
6. Updates tech-spec (☐ → ✅)
7. Runs parallel checks:
   - **code-reviewer** (quality)
   - **security-auditor** (OWASP)
8. If issues → code-developer fixes, repeat checks
9. Git commit locally
10. Asks about push

**Use when:** Want control over each task

**Next step:** `/start-task feature-name 2` or manual testing

---

### /start-feature

**Purpose:** Execute ALL tasks automatically (Feature Autopilot).

**Usage:** `/start-feature feature-name`

**Does:**
1. Finds feature, switches to feature branch
2. Checks task statuses
3. Creates plan via TodoWrite
4. **For each task** (sequential):
   - Launches code-developer
   - Git commit (gitleaks pre-commit hook scans secrets)
   - Updates task status → done
5. **After all tasks:**
   - Runs integration tests (if any)
   - Parallel final checks:
     - code-reviewer (entire feature)
     - security-auditor (entire feature)
   - If critical issues → rollback, fix, repeat
   - Updates context documentation
   - Finalizes tech-spec (status → implemented)
   - Git push

**Use when:** All tasks clear, trust agent execution

**Next step:** Manual testing, deploy

---

### /start-feature-waves

**Purpose:** Execute tasks in parallel waves (max speed).

**Usage:** `/start-feature-waves feature-name`

**Requires:** Tasks organized in waves via `/plan-task-waves`

**Does:**
1. Executes tasks in wave-1/ in parallel
2. Waits for wave-1 completion
3. Executes tasks in wave-2/ in parallel
4. Continues for all waves
5. Final checks and push

**Use when:** Large feature, independent tasks, need speed

---

### /plan-task-waves

**Purpose:** Decompose Tech Spec into parallel task waves.

**Usage:** `/plan-task-waves feature-name`

**Does:**
1. Reads tech-spec
2. Analyzes task dependencies
3. Groups independent tasks into waves
4. Creates wave folders: `wave-1/`, `wave-2/`, ...
5. User reviews wave structure

**Next step:** `/start-feature-waves feature-name`

---

## Command Cheat Sheet

| Command | Use Case | Input Required | Output |
|---------|----------|----------------|--------|
| `/init-project` | Start new project structure | None | Project template copied |
| `/init-git` | Create GitHub repo | Repo name, visibility | GitHub repo created |
| `/init-project-discovery` | Define project | Interview answers | project.md |
| `/init-context` | Fill context (new) | Tech preferences | 4 context files |
| `/init-context-old` | Fill context (from audit) | old-folder-audit.md | 5 context files |
| `/setup-infrastructure` | Setup framework + CI/CD | Tech stack from context | Framework + CI/CD ready |
| `/setup-infrastructure-old` | Add tests + CI/CD only | Existing code | Tests + CI/CD added |
| `/old-project` | Archive legacy code | Confirmation | old/ folder + new structure |
| `/old-folder-audit` | Analyze legacy code | old/ folder exists | old-folder-audit.md |
| `/new-feature` | Create User Spec | Interview answers | user-spec.md |
| `/create-tech-spec` | Create Tech Spec | feature-name, user-spec | tech-spec.md |
| `/tech-spec-decompose` | Create tasks | feature-name, tech-spec | tasks/*.md |
| `/plan-task-waves` | Create task waves | feature-name, tech-spec | wave-*/*.md |
| `/start-task` | Execute one task | feature-name, task-number | Task completed |
| `/start-feature` | Execute all tasks | feature-name, tasks exist | Feature completed |
| `/start-feature-waves` | Execute in parallel | feature-name, waves exist | Feature completed (fast) |

---

## Common Command Combinations

### Quick project start (no interview):
```bash
/init-project && /init-git
# Then manually edit .claude/skills/project-knowledge/guides/ files
```

### Skip framework init (API projects):
```bash
# Edit architecture.md to specify "no framework init needed"
/setup-infrastructure  # Will skip framework init
```

### Create feature and start immediately:
```bash
/new-feature && /create-tech-spec feature-name && /tech-spec-decompose feature-name && /start-feature feature-name
```

### Create multiple features in batch:
```bash
/new-feature  # feature-1
/new-feature  # feature-2
/new-feature  # feature-3
# Then implement them one by one
```

---

## Error Messages and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| "User Spec not found" | Missing user-spec.md | Run `/new-feature` first |
| "Tech Spec not found" | Missing tech-spec.md | Run `/create-tech-spec` first |
| "Tasks not found" | Missing tasks/ folder | Run `/tech-spec-decompose` first |
| "old/ folder not found" | `/old-project` not run | Run `/old-project` first |
| "GitHub auth failed" | Not logged in to gh CLI | Run `gh auth login` |
| "Context files missing" | `/init-context` not run | Run `/init-context` or `/init-context-old` |

---

## Next Steps

After completing any workflow:
- **New Project** → `/new-feature` (start first feature)
- **Onboarding** → `/new-feature` (start refactoring)
- **Feature Development** → Deploy → `/new-feature` (next feature)
