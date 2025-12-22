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

**Step 4: Create tasks/*.md**

For each task identified in tech-spec:

File: `work/{feature-name}/tasks/{N}.md`

**Frontmatter:**
- `status`: planned

**Content (English):**

1. **Description** (1-2 sentences)
   - What this specific task accomplishes
   - How it fits into overall feature

2. **What to do** (specific steps)
   - Concrete implementation steps (NOT pseudocode)
   - What files to create/modify
   - What functions/components to add
   - What to import/configure

3. **Acceptance Criteria** (checklist)
   - How to know task is complete
   - What must work
   - Tests that must pass

4. **Context Files** (which guides to read during implementation)
   ```markdown
   - patterns.md - [relevant section]
   - testing.md - [relevant section]
   - api.md - [relevant section]
   ```

5. **Technical Details**
   - Files affected: `src/auth/middleware.ts`, `src/models/user.ts`
   - Dependencies: express-jwt, bcrypt
   - Edge cases: token expiration, invalid signatures
   - Integration points: existing auth system

**Important:** Do NOT write pseudocode or algorithms. Describe WHAT to implement, not HOW (code is written during implementation by code-developer agent).

**Task atomicity principles:**
- Each task = non-breaking increment (code works after each task)
- ~1-3 hours of work per task (not days)
- Tests separated from implementation (separate tasks for integration/E2E)
- Minimal dependencies between tasks

**Write all task files.**

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
...

Посмотри, пожалуйста. Всё правильно? Нужны изменения?"
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
