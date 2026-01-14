---
name: tech-spec-planning
description: |
  Create tech-spec.md + tasks/*.md with architecture & task breakdown.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "сделай техспек", "составь техспек", "составь тз и план задач"

  Do NOT use for: business requirements (use user-spec-planning)
---

# Tech Spec Planning

## Overview

Create comprehensive technical specifications and task decomposition through intelligent analysis and adaptive clarification. This skill reads project context, analyzes inputs (user-spec / audit / description), asks clarifying questions only when needed, and produces tech-spec.md + tasks/*.md ready for implementation.

**Input:** user-spec.md OR audit OR user description
**Output:** tech-spec.md + tasks/*.md
**Language:** Technical documentation in English

## When to Use

Activate this skill when:
- Creating technical specification for features/bugs/refactorings
- Need to decompose work into atomic implementation tasks
- Have user-spec and ready to plan technical approach
- Have clear problem description and ready to design solution
- User says "создай техспек", "tech spec", "разбей на задачи", "technical planning"

**Do NOT use for:**
- User-facing planning (that's user-spec-planning skill)
- When requirements are completely unclear (create user-spec first)

## Workflow

### Phase 1: Gather Context

**Step 1: Check for feature folder**

Ask user for feature name if not provided:
```
"Как называется фича? (папка в work/)"
```

Check if folder exists:
```bash
ls work/{feature-name}/ 2>/dev/null
```

If doesn't exist:
```bash
mkdir -p work/{feature-name}
```

**Step 2: Read available inputs**

Try to read user-spec (if exists):
```bash
Read: work/{feature-name}/user-spec.md
```

If user-spec missing, ask user:
```
"Опиши подробно задачу: что нужно сделать и зачем?
Или предоставь аудит/документ с описанием."
```

**Step 3: Read project context**

Read all 7 core context files:
```bash
Read: .claude/skills/project-knowledge/guides/project.md
Read: .claude/skills/project-knowledge/guides/architecture.md
Read: .claude/skills/project-knowledge/guides/patterns.md
Read: .claude/skills/project-knowledge/guides/testing.md
Read: .claude/skills/project-knowledge/guides/deployment.md
Read: .claude/skills/project-knowledge/guides/api.md
Read: .claude/skills/project-knowledge/guides/conventions.md
```

If any files missing, note them and continue (not all projects have all guides).

**Step 4: Research best practices (if applicable)**

For complex technical decisions, use Context7 MCP server to fetch best practices:
- Relevant library documentation
- Framework guidelines
- Security patterns
- Performance optimization techniques

Launch specialized subagents for research if needed (e.g., security patterns, scalability considerations).

### Phase 2: Clarification (Adaptive)

**Analyze information completeness:**

Based on user-spec / description / audit, determine if additional clarification needed.

**Clarification decision rules:**

- **0 questions (skip phase):** If user-spec is comprehensive AND architecture.md has clear patterns
- **1-2 questions:** If minor gaps (e.g., unclear integration point, ambiguous dependency)
- **3-5 questions:** If significant gaps (e.g., missing technical constraints, unclear data model)
- **Suggest user-spec:** If requirements fundamentally unclear (don't guess - ask user to create user-spec first)

**Ask questions conversationally (Russian):**

Focus on technical gaps:
- "Какие технические ограничения есть? (производительность, безопасность, масштабирование)"
- "Где это интегрируется в существующую архитектуру? Какие компоненты затрагиваем?"
- "Какие данные нужны? Откуда берём?"
- "Есть ли зависимости от внешних сервисов/API?"

Do NOT ask about user value, scenarios, or acceptance criteria (that's user-spec territory).

**Wait for answers, move to next phase when ready.**

### Phase 3: Planning

Now create tech-spec.md and tasks/*.md based on all gathered information.

**Step 1: Analyze complexity**

Determine implementation complexity:
- **Simple:** Small change, single component, clear path → use `dev` branch
- **Complex:** Multiple components, architectural changes, high risk → use `feature/{name}` branch

Update decision in tech-spec frontmatter.

**Step 2: Read templates**

```bash
Read: ~/.claude/shared/work-templates/tech-spec.md.template
Read: ~/.claude/shared/work-templates/tasks/task.md.template
```

**Step 3: Create tech-spec.md**

File: `work/{feature-name}/tech-spec.md`

**Frontmatter:**
- `created`: Today's date (YYYY-MM-DD)
- `status`: draft
- `branch`: dev | feature/{name} (based on complexity)

**Content (English):**

1. **Solution** (2-3 paragraphs)
   - High-level technical approach
   - Why this solution (key rationale)
   - Major components involved

2. **Architecture** (components, data flow, diagrams if helpful)
   - What components change/added
   - How they interact (data flow, API calls)
   - Architectural patterns used

3. **Key Decisions** (list with rationale)
   - Major technical choices made
   - WHY chosen (alternatives considered)
   - Trade-offs accepted

4. **Data Models** (if applicable)
   - Database schemas
   - API request/response types
   - State management structures

5. **Dependencies** (external libraries, services, APIs)
   - What we're using
   - Versions if critical
   - Integration points

6. **Testing Strategy** (overall approach)
   - What types of tests needed (unit, integration, E2E)
   - What should be tested
   - Testing challenges

7. **Risks & Mitigation** (what could go wrong)
   - Technical risks
   - How to mitigate each

8. **Implementation Tasks** (brief list with links)
   ```markdown
   - [ ] [Task 1: Setup authentication middleware](tasks/1.md) - planned
   - [ ] [Task 2: Create user model](tasks/2.md) - planned
   - [ ] [Task 3: Integration tests](tasks/3.md) - planned
   ```

   Just list names + links, details go in task files.

**Write tech-spec.md file.**

**Step 3.5: Validate Tech-Spec + Decomposition (Subagent)**

Before creating task files, validate the tech-spec and task decomposition.

Launch validation subagent:

```
Use Task tool with subagent_type="general-purpose":

"Validate the technical specification at work/{feature-name}/tech-spec.md

Read these files:
- work/{feature-name}/tech-spec.md
- work/{feature-name}/user-spec.md (if exists)
- .claude/skills/project-knowledge/guides/architecture.md
- .claude/skills/project-knowledge/guides/patterns.md
- .claude/skills/project-knowledge/guides/database.md (if exists)
- .claude/skills/project-knowledge/guides/api.md (if exists)

Validate against these criteria:

## 1. Solution Optimality
- [ ] Is this the best technical solution for the task?
- [ ] Alternatives considered and choice justified?
- [ ] Solution not overly complex (YAGNI)?
- [ ] Solution matches existing architecture?
- [ ] Uses existing project patterns?

## 2. Scalability
- [ ] Solution handles 10x load growth?
- [ ] No single point of failure?
- [ ] Data can be sharded/partitioned if needed?
- [ ] No blocking operations in critical path?
- [ ] Caching considered where needed?

## 3. Security (OWASP Top 10 + beyond)
- [ ] Injection: parameterized queries, no concatenation
- [ ] Broken Auth: proper session/token verification
- [ ] Sensitive Data: encryption, no secrets in logs
- [ ] XXE: safe XML/JSON parsing
- [ ] Broken Access Control: permission checks at every level
- [ ] Security Misconfiguration: safe defaults
- [ ] XSS: output escaping
- [ ] Insecure Deserialization: input validation
- [ ] Vulnerable Components: up-to-date dependencies
- [ ] Insufficient Logging: audit critical operations

## 4. Reliability
- [ ] Graceful degradation on dependency failures?
- [ ] Retry with exponential backoff where needed?
- [ ] Circuit breaker for external services?
- [ ] Transactions where required?
- [ ] Idempotent operations?

## 5. Project Standards Compliance
- [ ] Architecture matches architecture.md?
- [ ] Patterns match patterns.md?
- [ ] Naming conventions followed?
- [ ] File structure matches project?

## 6. Task Decomposition Quality
- [ ] Each task is atomic, non-breaking increment
- [ ] Tasks cover entire scope from user-spec
- [ ] Task order is logical (dependencies respected)
- [ ] Task sizes are appropriate (not 'do everything')
- [ ] No circular dependencies
- [ ] Tests separated into own tasks where needed

## 7. Risks
- [ ] Risks identified realistically
- [ ] Each risk has mitigation
- [ ] No hidden unmentioned risks

Return JSON:
{
  'valid': true|false,
  'score': {
    'optimality': 1-10,
    'scalability': 1-10,
    'security': 1-10,
    'reliability': 1-10,
    'standards_compliance': 1-10,
    'decomposition': 1-10,
    'risks': 1-10
  },
  'issues': [
    {
      'severity': 'critical|warning|suggestion',
      'category': 'optimality|scalability|security|reliability|standards|decomposition|risks',
      'issue': 'Description',
      'why_matters': 'Why important',
      'fix': 'How to fix'
    }
  ],
  'decomposition_review': {
    'tasks_count': N,
    'estimated_complexity': 'low|medium|high',
    'dependency_graph_valid': true|false,
    'coverage_complete': true|false
  },
  'summary': 'Brief verdict'
}

Be thorough. This is the last check before implementation begins."
```

**Handle validation result:**

```
if valid == true:
    # Proceed to Step 4 (create task files)
    pass

elif has_critical_issues:
    # Auto-fix critical issues in tech-spec.md
    for issue in issues where severity == 'critical':
        # Edit tech-spec.md to fix

    # Re-validate (max 2 retries)
    if retry_count <= 2:
        # Run validation again
    else:
        # Show to user for help

elif only_warnings:
    # Store warnings to show user during review
    validation_warnings = issues
```

**Step 4: Create tasks/*.md (via Subagents)**

For each task from tech-spec's Implementation Tasks section, launch a subagent **in parallel**.

**Step 4.1: Determine relevant docs for each task**

Analyze task description for keywords to determine which additional docs to load:

| Keywords in task | Additional docs |
|------------------|-----------------|
| database, model, schema, migration, query | `database.md` |
| API, endpoint, route, REST, GraphQL | `api.md` |
| UI, component, page, form, style | `ux-guidelines.md` |
| deploy, CI, CD, Docker, env, infrastructure | `deployment.md` |
| git, branch, commit, PR, hook | `git-workflow.md` |
| test, unit, integration, e2e, mock | `testing.md` |
| auth, login, session, token, permission | `api.md` + security sections |

**Step 4.2: Launch subagents for each task (parallel)**

```
Use Task tool with subagent_type="general-purpose":

"Create task file for Task {N}: {task_name}

Read these files for context:
- work/{feature-name}/tech-spec.md
- work/{feature-name}/user-spec.md (if exists)
- .claude/skills/project-knowledge/guides/architecture.md (ALWAYS)
- .claude/skills/project-knowledge/guides/patterns.md (ALWAYS)
- .claude/skills/project-knowledge/guides/project.md (ALWAYS)
- {additional_docs_based_on_keywords}
- ~/.claude/shared/work-templates/tasks/task.md.template

Write task file to: work/{feature-name}/tasks/{N}.md

The task file MUST include:

1. **Frontmatter:**
   - status: planned

2. **Description** (1-2 sentences)
   - What this task accomplishes
   - How it fits into the feature

3. **What to do** (specific steps)
   - Concrete implementation steps (NOT pseudocode!)
   - Which files to create/modify
   - What functions/components to add
   - What to import/configure

4. **Acceptance Criteria** (checklist)
   - How to verify task is complete
   - What must work
   - Tests that must pass

5. **Context Files** (CRITICAL!)
   List ALL guides the implementer should read:
   - ALWAYS include: architecture.md, patterns.md
   - Add relevant guides based on task content:
     - If task touches DB → include database.md
     - If task creates API → include api.md
     - If task has UI → include ux-guidelines.md
     - If task involves deploy → include deployment.md
     - If task involves git → include git-workflow.md
     - If task involves tests → include testing.md
   - Specify WHICH sections are relevant

6. **Technical Details**
   - Files affected: list specific paths
   - Dependencies: packages needed
   - Edge cases: what could go wrong
   - Integration points: what this connects to

IMPORTANT:
- Do NOT write pseudocode or algorithms
- Describe WHAT to implement, not HOW
- Each task must be atomic (non-breaking increment)

Return the file path when done."
```

**Launch all task subagents in parallel** — they are independent.

Wait for all subagents to complete.

**Step 4.3: Validate all task files (Subagent)**

After all task files are created, validate them:

```
Use Task tool with subagent_type="general-purpose":

"Validate all task files in work/{feature-name}/tasks/

Read:
- work/{feature-name}/tech-spec.md
- work/{feature-name}/user-spec.md (if exists)
- All task files: work/{feature-name}/tasks/*.md
- .claude/skills/project-knowledge/guides/architecture.md
- .claude/skills/project-knowledge/guides/patterns.md

For EACH task file, validate:

## 1. Structure Completeness
- [ ] All required sections present
- [ ] No placeholders or TODOs

## 2. Content Quality
- [ ] What to do has concrete steps (not pseudocode)
- [ ] Acceptance Criteria are testable (not 'works correctly')
- [ ] Edge cases considered
- [ ] Files to modify specified

## 3. Context Files Completeness (CRITICAL!)
Analyze task content and verify Context Files includes all necessary guides:

| If task mentions | Context Files MUST include |
|-----------------|---------------------------|
| database, model, schema, query | database.md |
| API, endpoint, route | api.md |
| UI, component, form, style | ux-guidelines.md |
| deploy, CI, Docker | deployment.md |
| git, branch, commit | git-workflow.md |
| test, mock, fixture | testing.md |

If task content references something but Context Files doesn't include relevant guide → CRITICAL issue!

## 4. Security
- [ ] No hardcoded secrets in steps
- [ ] Input validation mentioned where needed
- [ ] Auth/permissions considered if relevant
- [ ] SQL injection prevented (parameterization)
- [ ] XSS prevented (escaping)

## 5. Scalability
- [ ] No N+1 patterns in described operations
- [ ] No blocking operations without reason
- [ ] DB indexes mentioned if needed

## 6. Consistency with tech-spec
- [ ] Task matches its description in tech-spec
- [ ] No scope creep
- [ ] Dependencies match

Return JSON:
{
  'valid': true|false,
  'tasks': {
    '1': {
      'valid': true,
      'issues': []
    },
    '2': {
      'valid': false,
      'issues': [
        {
          'severity': 'critical|warning|suggestion',
          'category': 'structure|content|context_files|security|scalability|consistency',
          'issue': 'Task modifies database schema but database.md not in Context Files',
          'fix': 'Add database.md to Context Files section'
        }
      ]
    }
  },
  'summary': 'X/Y tasks valid, Z need fixes'
}

Be thorough - this is the last validation before user sees the tasks."
```

**Handle task validation result:**

```
if all_tasks_valid:
    # Proceed to Phase 4 (Review)
    pass

elif has_critical_issues:
    # Auto-fix critical issues
    for task_num, task_result in tasks.items():
        for issue in task_result.issues where severity == 'critical':
            # Edit task file to fix the issue

    # Re-validate (max 2 retries)
    if retry_count <= 2:
        # Run validation again
    else:
        # Show remaining issues to user

elif only_warnings:
    # Store warnings to show user during review
    task_validation_warnings = all_warnings
```

### Phase 4: Review & Iterate

**CRITICAL: Get user approval before proceeding.**

**Step 1: Show files to user**

Tell user (in Russian):

```
"Готово! Я создал:

Техспек: [work/{feature-name}/tech-spec.md](work/{feature-name}/tech-spec.md)
Задачи:
- [tasks/1.md](work/{feature-name}/tasks/1.md) - {brief description}
- [tasks/2.md](work/{feature-name}/tasks/2.md) - {brief description}
..."
```

**If validation had warnings, show them:**

```
"Валидация прошла. Есть несколько замечаний:

**Tech-spec:**
⚠️ {category}: {issue}
   → {fix}

**Tasks:**
⚠️ Task {N} - {category}: {issue}
   → {fix}

(это не критично, но стоит учесть)"
```

```
"Посмотри, пожалуйста. Всё правильно? Нужны изменения?"
```

**Step 2: Wait for user response**

User can respond three ways:

**A) Changes requested:**
1. Make requested edits to tech-spec and/or tasks
2. Show updated files with links
3. Return to Step 2 (wait for response again)

**B) Approved:**
1. Update tech-spec.md frontmatter: `status: draft` → `status: approved`
2. Tell user: "Отлично! Техспек и задачи готовы."
3. Proceed to Phase 5 (Commit)

**C) Questions/unclear:**
1. Answer questions, clarify
2. If questions lead to changes: follow path A
3. If just clarification: continue waiting for approval

**Do NOT proceed to commit until user explicitly approves.**

### Phase 5: Commit

After user approval, commit changes to git.

**Commit structure:**

```bash
git add work/{feature-name}/tech-spec.md work/{feature-name}/tasks/*.md
git commit -m "$(cat <<'EOF'
feat: add tech spec and tasks for {feature-name}

Created technical specification with:
- Architecture decisions
- Implementation strategy
- {N} atomic tasks

Files:
- tech-spec.md
- tasks/1.md - {brief}
- tasks/2.md - {brief}
...

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git push
```

**Tell user next steps:**

```
"Закоммитил и запушил.

Следующие шаги:
- `/start-task` - реализовать задачи по одной (с контролем)
- `/start-feature` - автоматическая реализация всех задач
- `/plan-task-waves` - спланировать параллельное выполнение
```

**Skill work is DONE.**

## Quality Guidelines

**Good tech-spec.md:**
- ✅ Clear solution approach (not just "implement X")
- ✅ Architectural rationale (WHY decisions made)
- ✅ Concrete technical details (components, data flow)
- ✅ Realistic risk assessment
- ✅ Testing strategy appropriate to changes

**Good tasks/*.md:**
- ✅ Atomic (non-breaking increment)
- ✅ Specific (files, functions, edge cases)
- ✅ Testable (clear acceptance criteria)
- ✅ Context references (which guides to read)
- ✅ NO pseudocode (describe WHAT, not HOW)

**Bad practices:**
- ❌ Vague tech-spec ("refactor X to be better")
- ❌ Non-atomic tasks (week-long work items)
- ❌ Pseudocode in tasks (code goes in implementation phase)
- ❌ Missing architectural context
- ❌ No testing strategy
- ❌ Skipping user approval

## Resources

This skill uses shared templates:
- `~/.claude/shared/work-templates/tech-spec.md.template` - Technical specification template
- `~/.claude/shared/work-templates/tasks/task.md.template` - Task file template

For best practices research, the skill leverages:
- Context7 MCP server for library documentation
- Specialized subagents for security, scalability, architecture analysis
