---
name: documentation
description: |
  Manage .claude/skills/project-knowledge/ docs: create, check, update, fill knowledge base.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "заполни документацию", "создай документацию", "проверь документацию", "обнови документацию", "заполни базу знаний проекта", "обнови базу знаний проекта"

  Do NOT use for: reading docs, explaining concepts
---

# Documentation Management

## Overview

This skill manages project documentation in `.claude/skills/project-knowledge/guides/`. It helps create concise, project-specific documentation through interviews and codebase analysis, audit existing docs for bloat and anti-patterns, edit documentation files, verify consistency across files, and track documentation status.

## When to Use

Activate this skill when:
- **"Create documentation"** or **"Document this project"** - Initialize docs for new or legacy projects
- **"Audit my documentation"** or **"Check docs for bloat"** - Find and fix quality issues
- **"Edit [filename]"** or **"Update architecture docs"** - Modify specific documentation
- **"Check consistency"** - Verify terminology and tech stack across files
- **"Show doc status"** or **"What docs are filled?"** - Review documentation completeness

## Documentation Structure

Every project uses **11 core documentation files** in `.claude/skills/project-knowledge/guides/`:

1. **project.md** - High-level overview, target audience, core features, out of scope
2. **features.md** - Complete feature inventory with priorities, dependencies, status
3. **roadmap.md** - Development phases, milestones, timeline, migration plan (if applicable)
4. **architecture.md** - Tech stack, project structure, dependencies, integrations
5. **patterns.md** - Coding standards, conventions, error handling, testing
   - Contains **Universal Patterns** (from template, shared across all projects) + **Project-Specific Patterns** (custom for this project)
   - Universal Patterns section should NOT be removed - it ensures consistent code quality
6. **database.md** - Schema, tables/collections, migrations, sensitive data
7. **deployment.md** - Platform, environment variables, CI/CD, rollback
8. **git-workflow.md** - Branching strategy, testing requirements, security gates
9. **ux-guidelines.md** - Interface language, tone, domain glossary, design system
10. **monitoring.md** - Logging, error tracking, metrics, health checks, alerts
11. **business-rules.md** - Domain workflows, validation rules, calculations, state machines (optional)

For detailed information about each file's sections and purpose, see [references/structure.md](references/structure.md).

## Core Workflows

### 1. Create Documentation

**Trigger:** User asks to create or initialize project documentation.

**Process:**

1. **Verify setup:**
   - Check if `.claude/skills/project-knowledge/guides/` exists
   - If missing, create structure or suggest using `/init-project` command

2. **Fill project.md via interview:**
   - Ask about project purpose, goals, target audience
   - Identify core features and what's out of scope
   - Define success criteria
   - Write concise responses to `guides/project.md`

3. **Fill documentation files:**

   **Files typically created by project-planning skill:**
   - **project.md** - via interview (this skill can also fill for legacy projects)
   - **features.md** - via feature decomposition interview
   - **roadmap.md** - via roadmap planning interview

   **Files created via codebase analysis + interview:**
   - **architecture.md** - Tech stack, structure, dependencies (analyze package.json, configs)
   - **database.md** - Schema, migrations (analyze models, migrations folder)
   - **deployment.md** - Platform, env vars, CI/CD (analyze deploy configs, .env.example)
   - **git-workflow.md** - Branching, testing requirements (analyze existing workflow or interview)
   - **monitoring.md** - Logging, metrics, alerts (analyze existing monitoring or interview)
   - **ux-guidelines.md** - UI language, tone, glossary (interview about user-facing aspects)

   **Special handling:**
   - **patterns.md** - Keep Universal Patterns from template (`~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/patterns.md`), add Project-Specific Patterns only if custom conventions exist. For simple projects, empty Project-Specific section is acceptable.
   - **business-rules.md** - OPTIONAL, create only if project has complex domain logic (workflows, calculations, state machines)

   **Process for each file:**
   - **Analyze codebase:** Scan package files, directory structure, configs
   - **Check existing docs:** Extract project-specific info from old README/docs
   - **Use Context7:** Verify library versions and get official documentation URLs
   - **Draft documentation:** Create drafts following quality principles
   - **Review with user:** Show drafts, get corrections/additions, confirm accuracy
   - **Write final files:** Save agreed-upon documentation

4. **Confirm completion:**
   - Show documentation status
   - Verify all 11 files are present
   - Note: CLAUDE.md and README.md are usually filled by `/init-project` command, but for legacy projects may need manual verification (see "Root Project Files" section)

**Key principles:**
   - Follow documentation principles from [references/principles.md](references/principles.md) - avoid code examples, obvious content, and generic framework explanations
   - **Exception:** patterns.md contains Universal Patterns from template - this is intentional and should be preserved

### 2. Audit Documentation

**Trigger:** User asks to audit, check quality, or find bloat in documentation.

**Process:**

1. **Read all documentation files:**
   - Load all 11 core guide files from `.claude/skills/project-knowledge/guides/`
   - Also check CLAUDE.md and README.md for quality issues

2. **Identify quality issues:**
   - ❌ Code examples (should be file references)
   - ❌ Obvious information ("npm install installs dependencies")
   - ❌ Generic framework/library explanations
   - ❌ Duplication between files
   - ❌ Placeholder/template text
   - ❌ Outdated information
   - ❌ Function-specific details (should be code comments)
   - ❌ Detailed info in CLAUDE.md/README.md (should be in project-knowledge guides)
   - 📏 Bloated sections (too long, too detailed)

   **IMPORTANT - patterns.md exception:**
   - ✅ **Universal Patterns section is intentional** - This section comes from the global template (`~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/patterns.md`) and contains common best practices
   - ✅ **DO NOT flag Universal Patterns as "generic" or "to be removed"** - This content ensures consistent code quality across all projects
   - ✅ **Only audit Project-Specific Patterns section** - This is where project-specific content should be added if needed
   - ✅ **Simple projects can have empty Project-Specific section** - If project is straightforward, only Universal Patterns are sufficient

3. **Create audit report:**
   - List issues by file and line number
   - Categorize: code examples, obvious content, bloat, duplication, outdated info
   - Provide specific recommendations
   - Suggest moving function-specific details to code comments

4. **Apply fixes:**
   - Ask user which issues to address
   - Edit files with approved changes
   - Replace code examples with file references (e.g., "See [auth.ts:45-67](src/auth.ts#L45-L67)")
   - Move function-specific details to code comment suggestions
   - Verify consistency after changes

For audit criteria and examples, see [references/principles.md](references/principles.md).

### 3. Edit Documentation

**Trigger:** User asks to edit, update, or modify specific documentation.

**Process:**

1. **Identify target:**
   - If user specifies file/section, use that
   - Otherwise, show list of 11 files and ask which to edit

2. **Read current content:**
   - Load the target file
   - Show relevant sections for context

3. **Apply changes:**
   - Implement user-requested changes
   - Follow documentation principles (no bloat, no code examples)
   - Use file references instead of code duplication

4. **Verify consistency:**
   - Check if changes affect other files (e.g., tech stack mentioned elsewhere)
   - Update related files if needed

### 4. Check Consistency

**Trigger:** User asks to verify consistency or check for terminology mismatches.

**Process:**

1. **Read all files:**
   - Load all 7 core guide files

2. **Extract key information:**
   - Tech stack names and versions
   - Service/component names
   - Database names
   - Environment variable names
   - Deployment platforms and URLs

3. **Compare across files:**
   - Check if same items have different names (e.g., "PostgreSQL" vs "Postgres" vs "postgres")
   - Verify version numbers match
   - Identify terminology inconsistencies

4. **Report and fix:**
   - Show inconsistencies found
   - Ask user for correct terminology
   - Apply standardization across all files
   - Re-verify consistency

### 5. Show Documentation Status

**Trigger:** User asks about documentation status, what's filled, or what needs work.

**Process:**

1. **Check each file:**
   - Verify file exists
   - Determine if filled or template (check for placeholders like `[Project Name]`)
   - Get file size and last modified date

2. **Analyze completeness:**
   - ✅ Filled: No placeholders, all sections complete
   - ⚠️ Partially filled: Some sections complete, some placeholders
   - ❌ Template: All placeholders, not customized

3. **Show status report:**
   - List all 11 files with status icons
   - Show file sizes and last update dates
   - Summarize: X files filled, Y files partial, Z files need work
   - Provide recommendations for next steps

4. **Offer actions:**
   - Ask if user wants to fill missing sections
   - Suggest audit if files are large (potential bloat)

## Root Project Files (CLAUDE.md & README.md)

Projects have two root-level documentation files that serve as entry points to the main documentation in `.claude/skills/project-knowledge/guides/`:

### CLAUDE.md - For AI Agents

**Purpose:** Minimal file that directs AI agents to the project-knowledge skill.

**Template location:** `~/.claude/shared/templates/new-project/CLAUDE.md`

**Content:**
- Project name and one-line description
- Reference to `.claude/skills/project-knowledge/` as the documentation source
- Methodology overview (spec-driven development workflow)
- Active work directory reference (`work/`)
- Default branch strategy
- Library documentation approach (Context7)

**When to update:**
- ✅ Project initialization (via `/init-project` command)
- ✅ Fundamental methodology changes
- ✅ Default branch strategy changes
- ❌ **DO NOT** add detailed workflows, commands, or information that belongs in project-knowledge guides
- ❌ **DO NOT** duplicate information from guides

**Key principle:** Keep it minimal. This file should only point to the real documentation, not contain it.

### README.md - For Humans

**Purpose:** Brief project overview for human developers (in Russian).

**Template location:** `~/.claude/shared/templates/new-project/README.md`

**Content:**
- Project title and purpose (concise)
- Project structure overview (folder tree)
- Brief methodology reference
- Link to `guides/` folder for detailed documentation

**When to update:**
- ✅ Project initialization (via `/init-project` command)
- ✅ Project name or core purpose changes
- ✅ Major folder structure changes
- ❌ **DO NOT** add commands, detailed workflows, or step-by-step instructions
- ❌ **DO NOT** duplicate content from project-knowledge guides
- ❌ **DO NOT** add obvious information or generic explanations

**Key principle:** Keep it concise and human-friendly. This is an overview, not a manual.

### Relationship to Project-Knowledge Guides

Both CLAUDE.md and README.md are **meta-documentation** that points to the real documentation in `.claude/skills/project-knowledge/guides/`. They should:

- Be stable and rarely change
- Avoid duplication of information from the 11 core guides
- Serve as navigation/entry points only
- Keep focus on "what and where" rather than "how"

When auditing or updating documentation, check that these files don't contain information that should live in the project-knowledge guides instead.

## Adding New Guides (Rare)

⚠️ **Warning:** The 11 core files cover 99% of projects. Adding a 12th+ file should be rare and well-justified.

**Before adding:**
1. Confirm information doesn't fit in existing 11 files
2. Verify information is critical and frequently referenced
3. Get user approval

**If justified:**
1. Create new guide file in `guides/` directory
2. Update `.claude/skills/project-knowledge/skill.md` to list new guide
3. Check and update `.claude/CLAUDE.md` if it lists guide files
4. Check and update project `README.md` if it lists documentation
5. **Do NOT** update `~/.claude/shared/templates/` (project-specific only)

## Integration with Commands

This skill works alongside existing documentation commands:

- **`/init-project-discovery`** - Creates initial `project.md` via interview
- **`/init-context`** - Fills technical docs for new projects (uses Context7)
- **`/init-context-old`** - Fills technical docs for legacy projects (from code analysis)
- **`/migrate-context-to-skill`** - Migrates old `context/` folder to `project-knowledge` skill

**Relationship:** Use commands for initial project setup, use this skill for ongoing maintenance, auditing, editing, and quality control.

## Resources

This skill includes reference documentation with detailed information:

### references/structure.md
Complete description of all 11 core documentation files, their purpose, sections, and what information belongs in each.

### references/principles.md
Documentation quality principles covering:
- What NOT to write (obvious info, code examples, generic explanations)
- What TO write (project-specific info, architectural decisions, references)
- When to use code comments vs documentation
- Quality indicators (good vs bad documentation)

### references/examples.md
Real examples of good vs bad documentation:
- How to reference code instead of copying it
- Concise vs bloated content
- Project-specific vs generic information
- Proper code comment examples
