---
name: methodology
description: |
  AI-First methodology: workflows, ~/.claude structure, command sequences.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "изучи методологию", "изучи глобальную папку"

  Do NOT use for: project-specific tech (answer directly), infrastructure (use infrastructure skill)
---

# AI-First Development Methodology

## Overview

AI-First methodology is a structured development approach designed for entrepreneurs and small teams working with AI agents. It solves the core problem of **context loss between sessions** by implementing a distributed knowledge base and spec-driven workflow.

**Problems solved:**
1. **Context loss** - Agent forgets previous work
2. **Chaotic documentation** - Monolithic CLAUDE.md files overwhelm context window
3. **Outdated knowledge** - Agent's knowledge cutoff (January 2025)
4. **Lack of structure** - Every project organized differently
5. **Quality issues** - No systematic review
6. **Complex onboarding** - New developers get lost

**Solution:**
- **Distributed Knowledge Base** - Modular structure instead of monolith
- **Proper hierarchy** - Context → User Spec → Tech Spec → Tasks → Code
- **MCP Context7** - Real-time up-to-date documentation
- **Agent Orchestration** - Specialized subagents for different tasks
- **Quality automation** - Code review, tests, security scanning
- **Git-friendly documentation** - Versioned with code

---

## When to Use This Skill

Invoke this skill when:
- User asks about "методология" or "workflow"
- Starting new project - need workflow guidance
- Onboarding existing project - confused about approach
- Daily development - which commands to use
- Understanding system concepts and structure
- Choosing between different workflows
- Setting up project documentation

**Do NOT use when:**
- User needs infrastructure setup (use `infrastructure` skill)
- User needs testing strategy (use `testing` skill)
- User wants to create/manage commands (use `command-manager` skill)
- User asks about specific technical implementation (answer directly)

---

## Key Concepts

### Just-In-Time Context
Agent reads only necessary information for current task, not entire context.

**How it works:**
- Task development → read task.md, tech-spec.md, relevant context files
- Feature development → read all tasks, tech-spec, user-spec
- Context update → read only modified files

**Benefits:**
- Reduced context window usage
- Faster processing
- More focused responses

### Single Source of Truth
Each piece of information stored in one place, others reference it.

**Examples:**
- Project description → `.claude/skills/project-knowledge/guides/project.md`
- Tech stack → `.claude/skills/project-knowledge/guides/architecture.md`
- Database schema → `.claude/skills/project-knowledge/guides/database.md`
- Deployment config → `.claude/skills/project-knowledge/guides/deployment.md`

**Benefits:**
- No duplication
- No conflicts
- Easy updates

### Spec-Driven Development
Write specifications before code, always.

**Flow:**
1. **Context** - Project description (created once, updated) [English]
2. **User Spec** - What we want and why (for human) [Russian]
3. **Tech Spec** - How to implement technically (for agent) [English]
4. **Tasks** - Concrete tasks from Tech Spec [English]
5. **Code** - Implementation

**Benefits:**
- Clear requirements
- Approved scope
- Prevents scope creep
- Enables parallel work

### Progressive Disclosure
Information revealed gradually from general to specific.

**Levels:**
1. `project.md` - What we're building
2. `architecture.md` - What we're building with
3. `user-spec.md` - What we want in feature
4. `tech-spec.md` - How we implement feature
5. `tasks/*.md` - Concrete work items

**Benefits:**
- Cognitive load management
- Better understanding
- Easier navigation

### Agent Orchestration
Main agent coordinates specialized subagents for different tasks.

**Roles:**
- **Main agent** - Coordinates, makes decisions, plans
- **code-developer** - Implements tasks, writes code and tests
- **code-reviewer** - Reviews code quality, finds issues
- **security-auditor** - Audits against OWASP Top 10

**Skills:**
- **infrastructure** - Sets up CI/CD, Docker, testing
- **testing** - Provides testing strategy guidance
- **methodology** - This skill, provides workflow guidance

**Benefits:**
- Specialized expertise
- Parallel execution
- Quality assurance

### Git-Friendly Documentation
Documentation lives in Git with code. Reasoning in descriptions, history in Git.

**What's versioned:**
- All context files
- All specs and tasks
- All guides
- All rules

**Benefits:**
- History through `git log`
- Review through `git diff`
- Rollback through `git revert`
- Branching for experiments

---

## Workflow Decision Framework

### Decision Tree

**Starting new project from scratch?**
→ Use **New Project Workflow** ([guides/workflow-new-project.md](guides/workflow-new-project.md))
- Command sequence: `/init-project` → `/init-git` → `/init-project-discovery` → `/init-context` → `/setup-infrastructure`
- Result: Fully initialized project with context, git, and infrastructure

**Have existing project without documentation?**
→ Use **Onboarding Workflow** ([guides/workflow-onboarding.md](guides/workflow-onboarding.md))
- Command sequence: `/old-project` → `/old-folder-audit` → `/init-project-discovery` → `/init-context-old` → `/setup-infrastructure-old`
- Result: Legacy code preserved, new AI-First structure created

**Working on feature/bug/refactor?**
→ Use **Feature Development Workflow** ([guides/workflow-feature-dev.md](guides/workflow-feature-dev.md))
- Command sequence: `/new-feature` → `/create-tech-spec` → `/tech-spec-decompose` → `/start-task` or `/start-feature`
- Result: Feature implemented with specs, tasks, tests, and review

### Command Quick Reference

**Project Initialization:**
- `/init-project` - Copy project template to current directory
- `/init-git` - Initialize git repo and create GitHub remote
- `/init-project-discovery` - Product discovery interview → create project.md
- `/init-context` - Fill 7 context files for new project
- `/init-context-old` - Fill 7 context files from legacy code audit
- `/setup-infrastructure` - Setup framework, CI/CD, Docker, tests
- `/setup-infrastructure-old` - Setup tests only (feature branch)

**Onboarding Existing Project:**
- `/old-project` - Archive old files, initialize new structure
- `/old-folder-audit` - Analyze legacy code, create audit report

**Feature Development:**
- `/new-feature` - Interview → create User Spec
- `/create-tech-spec` - Create Tech Spec from User Spec
- `/tech-spec-decompose` - Decompose Tech Spec into atomic tasks
- `/plan-task-waves` - Decompose into parallel waves
- `/start-task` - Start single task (manual mode)
- `/start-feature` - Start feature autopilot (sequential tasks)
- `/start-feature-waves` - Start feature autopilot (parallel waves)

**Utilities:**
- `/project-context` - Load key project context files
- `/meta-context` - Load context for ~/.claude/ meta-project

---

## Folder Structure Overview

### Global Folder `~/.claude/`

Meta-project for AI-First methodology. Changes affect ALL projects.

```
~/.claude/
├── shared/
│   └── templates/
│       ├── new-project/          # Complete project template
│       ├── infrastructure/       # Infrastructure templates
│       └── old-folder-audit.md   # Legacy audit template
├── skills/
│   ├── methodology/              # This skill
│   ├── infrastructure/           # Infrastructure setup
│   ├── testing/                  # Testing strategy
│   ├── skill-creator/            # Skill creation guide
│   └── command-manager/          # Command management
├── agents/                       # Global subagents
│   ├── code-developer/
│   ├── code-reviewer/
│   └── security-auditor/
├── commands/                     # 19 slash commands
├── hooks/                        # Automation hooks
├── CLAUDE.md                     # GLOBAL instructions
├── projects-registry.json        # All AI-First projects
└── backlog.md                    # Meta-project backlog
```

**Details:** [guides/folder-structure.md](guides/folder-structure.md)

### Local Project Folder

Created via `/init-project` or `/old-project`.

```
my-project/
├── .claude/skills/project-knowledge/guides/              # 7 context files
│   ├── project.md                # Project description
│   ├── architecture.md           # Tech stack
│   ├── database.md               # Database config
│   ├── deployment.md             # Deployment setup
│   ├── ux-guidelines.md          # UI/UX guidelines
│   ├── patterns.md               # Code patterns
│   └── git-workflow.md           # Git strategy
├── work/                         # Work items
│   ├── feature-name/
│   │   ├── user-spec.md          # What we want (Russian)
│   │   ├── tech-spec.md          # How to implement (English)
│   │   └── tasks/                # Atomic tasks
│   │       ├── 1.md
│   │       ├── 2.md
│   │       └── 3.md
│   ├── completed/                # Completed features (archive)
│   └── templates/                # Templates for specs/tasks
├── src/                          # Source code
├── tests/                        # Tests
├── CLAUDE.md                     # Project instructions
└── README.md                     # Project README
```

**Completed features:** After feature is done, tested, and deployed, move `work/feature-name/` to `work/completed/feature-name/` to keep work folder clean.

**Details:** [guides/folder-structure.md](guides/folder-structure.md)

### Context Files (9 Files)

1. **project.md** - Project description, audience, functionality, MVP scope
2. **architecture.md** - Tech stack, architectural decisions, Context7 mention
3. **database.md** - Database schema, migrations, query patterns
4. **deployment.md** - Deployment setup, env vars, CI/CD pipeline
5. **ux-guidelines.md** - UI text, tone of voice, design system
6. **patterns.md** - Code patterns, best practices, conventions
7. **git-workflow.md** - Git branching strategy, commit conventions, PR process
8. **monitoring.md** - Logging, error tracking, metrics, health checks, alerts
9. **business-rules.md** - Domain workflows, validation rules, calculations (optional)

**Details:** [guides/project-knowledge-skill.md](guides/project-knowledge-skill.md)

### Work Items Structure

```
work/feature-name/
├── user-spec.md              # What we want (Russian)
├── tech-spec.md              # How to implement (English)
└── tasks/                    # Atomic tasks
    ├── 1.md                  # Task 1
    ├── 2.md                  # Task 2
    └── 3.md                  # Task 3
```

**Task numbering:** Local to each feature (starts from 1).

**Task frontmatter:**
```yaml
---
status: planned | in_progress | done
type: implementation | test | documentation
---
```

**Details:** [guides/work-items.md](guides/work-items.md)

---

## Templates System

### New Project Template

Location: `~/.claude/shared/templates/new-project/`

**Contents:**
- 7 context file templates with examples
- `.gitignore` (security-focused)
- `CLAUDE.md` template
- `README.md` template
- `work/` folder with templates

**Used by:** `/init-project` command

### Infrastructure Templates

Location: `~/.claude/shared/templates/infrastructure/`

**Contents:**
- `husky-pre-commit-gitleaks.sh` - Pre-commit hook
- `smoke.test.ts` - TypeScript smoke test
- `test_smoke.py` - Python smoke test

**Used by:** `/setup-infrastructure` command

### Old Folder Audit Template

Location: `~/.claude/shared/templates/old-folder-audit.md`

**Purpose:** Template for analyzing legacy code during onboarding.

**Used by:** `/old-folder-audit` command

---

## Context7 Integration

**Problem:** Agent knowledge cutoff → outdated APIs and patterns.

**Solution:** Context7 MCP server fetches up-to-date documentation.

**How it works:**
1. Agent encounters unfamiliar/recent API
2. Agent uses Context7 to fetch latest docs
3. Agent implements using current best practices

**Setup:** Mention Context7 availability in `.claude/skills/project-knowledge/guides/architecture.md`:
```markdown
## Documentation Access
- Context7 MCP server available for real-time documentation
```

**Benefits:**
- Always current documentation
- Recent framework versions supported
- New API patterns learned

---

## Bundled Resources

### Guides (Detailed Procedures)

**Core Methodology:**
- [overview.md](guides/overview.md) - Methodology overview and key concepts
- [folder-structure.md](guides/folder-structure.md) - Complete folder structure guide
- [project-knowledge-skill.md](guides/project-knowledge-skill.md) - Project knowledge skill detailed guide
- [work-items.md](guides/work-items.md) - Work items structure and management

**Workflows:**
- [workflow-new-project.md](guides/workflow-new-project.md) - New project from scratch
- [workflow-onboarding.md](guides/workflow-onboarding.md) - Onboarding existing project
- [workflow-feature-dev.md](guides/workflow-feature-dev.md) - Daily feature development

**Development Environment:**
- [vps-setup.md](guides/vps-setup.md) - VPS reference guide (server info, SSH config, tmux, troubleshooting)
- [workflow-copy-to-vps.md](guides/workflow-copy-to-vps.md) - Copy project to VPS for dual-environment development

### References (Quick Lookup)

- [key-concepts.md](references/key-concepts.md) - Deep dive into methodology concepts
- [workflow-comparison.md](references/workflow-comparison.md) - Side-by-side workflow comparison
- [command-sequences.md](references/command-sequences.md) - Quick command reference
- [troubleshooting.md](references/troubleshooting.md) - Common issues and solutions

---

## Related Skills

- **infrastructure** - For setting up CI/CD, Docker, testing infrastructure
- **testing** - For comprehensive testing strategy (smoke, unit, integration, E2E)
- **command-manager** - For creating and managing slash commands
- **skill-creator** - For creating new skills

---

## Summary

This skill ensures:
- ✅ Clear workflow selection based on project stage
- ✅ Consistent project structure across all projects
- ✅ Proper context organization (7 files + work items)
- ✅ Spec-driven development (User Spec → Tech Spec → Tasks)
- ✅ Just-In-Time context loading
- ✅ Git-friendly documentation
- ✅ Agent orchestration for quality

**Remember:** Methodology provides the "when" and "why". Infrastructure and testing skills provide the "how".
