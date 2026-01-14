---
name: task-execution
description: |
  Execute tasks from tasks/*.md with quality gates: pre-checks, TDD, reviews.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "выполни задачу", "начни задачу", "сделай задачу", "запусти задачу",
  "реализуй задачу", "сделай таск", "do task"

  Do NOT use for: planning (use tech-spec-planning), creating tasks, writing specs
---

# Task Execution

Execute individual tasks from `tasks/*.md` with quality gates at each phase.

## When to Use

- Implementing a specific task from `work/{feature}/tasks/*.md`
- User says "выполни задачу" or similar
- Command `/do-task` is invoked

## Prerequisites

Before starting:
- Task file exists in `work/{feature}/tasks/`
- Tech-spec is approved
- User-spec is approved

## Workflow

### Phase 1: PRE-TASK

Before writing any code:

1. **Validate Task**
   - Read task file, verify status = `planned`
   - Parse acceptance criteria

2. **Read Context Files**
   See [references/context-files-list.md](references/context-files-list.md) for full list.

   Always read:
   - `.claude/skills/project-knowledge/guides/architecture.md`
   - `.claude/skills/project-knowledge/guides/patterns.md`
   - `.claude/skills/project-knowledge/guides/project.md`
   - `work/{feature}/user-spec.md`
   - `work/{feature}/tech-spec.md`

   Read from task file's "Context Files" section any additional files.

3. **Review Approach**
   Quick sanity check before coding:
   - Does planned solution follow patterns.md?
   - Can existing code be reused?
   - Any obvious issues with the approach?

   If concerns arise, discuss with user before proceeding.

4. **Baseline Tests** (optional)
   Run existing tests for the area being modified to establish baseline.
   If tests fail, note it but proceed (not our fault).

### Phase 2: IMPLEMENTATION

TDD approach - tests first, then code:

1. **Pre-implementation Analysis**
   - Grep for usages of code to be modified
   - Read all files that will be changed
   - Understand existing patterns

2. **Write Tests First**
   - Write tests for acceptance criteria
   - Write tests for edge cases from task file
   - Tests should fail initially (no implementation yet)

3. **Write Code**
   - Implement to pass tests
   - Follow patterns.md strictly
   - Handle edge cases

4. **Run Tests**
   - All new tests must pass
   - Fix any failures

5. **Verify Acceptance Criteria**
   - Check each criterion from task file
   - Document how each is satisfied

**Quality Reminders During Implementation:**
- Follow patterns.md
- No hardcoded secrets (use env vars)
- Validate all inputs
- Handle edge cases explicitly
- Comment WHY, not WHAT

### Phase 3: POST-TASK

After implementation complete:

1. **Run Relevant Tests**
   - Tests for files changed
   - Tests mentioned in task
   - NOT all tests (save that for end of feature)

2. **Ask User About Reviews**
   Use AskUserQuestion:
   ```
   Задача выполнена. Прогнать через ревью?
   - code-reviewer (качество кода, архитектура)
   - security-auditor (безопасность, OWASP)
   ```

3. **Run Selected Reviews**
   Launch subagents in parallel based on user choice:
   - `code-reviewer` - quality, architecture, patterns
   - `security-auditor` - OWASP Top 10, vulnerabilities

   `secret-scanner` runs automatically via pre-commit hook.

4. **Fix Issues**
   - Address critical/high severity issues
   - Note minor suggestions for future

5. **Git Commit**
   - Pre-commit hooks run (gitleaks, secret-scanner)
   - Use standard commit message format
   - Reference task file in commit

6. **Update Status**
   - Update task file: `status: planned` → `status: done`
   - Update tech-spec: mark task checkbox as complete

## Guides

- [Pre-task checklist](guides/pre-task-checklist.md) - detailed pre-task steps
- [Post-task checklist](guides/post-task-checklist.md) - detailed post-task steps

## References

- [Context files list](references/context-files-list.md) - all possible context files and when to use them
