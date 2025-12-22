---
description: Start feature development in parallel waves autopilot mode
allowed-tools:
  - Bash(git *)
  - Bash(find:*)
  - Bash(grep:*)
  - Bash(tree:*)
  - Read
  - Edit
  - Glob
  - TodoWrite
  - AskUserQuestion
  - Task
  - WebFetch
  - WebSearch
---

# Instructions

## 0. Create task tracking

**Use TodoWrite to create plan:**

```json
[
  {"content": "Проверить git статус", "status": "pending", "activeForm": "Проверка git статуса"},
  {"content": "Найти или валидировать фичу", "status": "pending", "activeForm": "Поиск/валидация фичи"},
  {"content": "Переключиться на ветку фичи", "status": "pending", "activeForm": "Переключение на ветку"},
  {"content": "Проверить наличие waves.md", "status": "pending", "activeForm": "Проверка waves.md"},
  {"content": "Выполнить все волны задач", "status": "pending", "activeForm": "Выполнение волн"},
  {"content": "Запустить integration тесты", "status": "pending", "activeForm": "Запуск integration тестов"},
  {"content": "Параллельные проверки (code review + security audit)", "status": "pending", "activeForm": "Code review и security audit"},
  {"content": "Исправить найденные проблемы", "status": "pending", "activeForm": "Исправление проблем"},
  {"content": "Обновить context документацию", "status": "pending", "activeForm": "Обновление context"},
  {"content": "Финализировать tech-spec", "status": "pending", "activeForm": "Финализация tech-spec"},
  {"content": "Git push", "status": "pending", "activeForm": "Git push"},
  {"content": "Отчёт о завершении", "status": "pending", "activeForm": "Отчёт"}
]
```

Mark each step as `in_progress` when starting, `completed` when done.

---

## 1. Check git status

**Mark todo as in_progress.**

**EXECUTE this command:**

```bash
git status
```

**If there are uncommitted changes:** Ask user: "Есть uncommitted changes. Закоммитить и продолжить / Продолжить без коммита / Остановиться?"

**Mark todo as completed.**

---

## 2. Find or validate feature

**Mark todo as in_progress.**

### If NO argument provided

**Find all active tech-specs:**

```bash
find work -name "tech-spec.md" -type f 2>/dev/null
```

**For each found tech-spec file:**
- Read the file
- Check frontmatter `status` field
- Include if `status: draft` OR `status: approved`

**If NO active features found:**

Tell user: "Активные фичи не найдены. Создай новую фичу: `/new-feature`"

STOP execution.

**If active features found:**

Show list to user:

```
Найдены активные фичи:
1. feature-1
2. feature-2
3. feature-3

Выбери фичу для работы. Запусти: /start-feature-waves <feature-name>
```

STOP execution.

### If argument provided

Argument can be in any format:
- `stripe-payments` (feature name)
- `work/stripe-payments` (path to feature folder)
- `work/stripe-payments/tech-spec.md` (path to tech-spec file)

**Extract feature name from argument** (the folder name inside `work/`).

**Check if tech-spec exists:**

```bash
test -f work/{feature-name}/tech-spec.md && echo "exists" || echo "not-found"
```

**If output contains "not-found":**

Find all active features (same logic as above) and show list:

```
Фича '{argument}' не найдена.

Доступные активные фичи:
1. feature-1
2. feature-2

Выбери существующую фичу.
```

STOP execution.

**Mark todo as completed.**

---

## 2.5. Switch to feature branch

**Mark todo as in_progress.**

**Read tech-spec frontmatter:**

Read `work/{feature-name}/tech-spec.md` and extract `branch` field from frontmatter (if exists).

**If branch field exists and specifies feature branch:**

Check if branch exists locally:

```bash
git show-ref --quiet refs/heads/{branch-name} && echo "exists" || echo "not-exists"
```

**If output contains "exists":**

```bash
git checkout {branch-name}
```

**If output contains "not-exists" (need to create):**

Create feature branch from dev:

```bash
git checkout dev && git checkout -b feature/{feature-name}
```

**If branch field does NOT exist:**

Work in current branch (typically `dev`).

**Mark todo as completed.**

---

## 3. Check for waves.md

**Mark todo as in_progress.**

**Check if waves.md exists:**

```bash
test -f work/{feature-name}/waves.md && echo "waves-exist" || echo "no-waves"
```

**If output contains "no-waves":**

Tell user:

```
❌ Файл waves.md не найден!

Сначала создай план выполнения задач:
/plan-task-waves {feature-name}

Или используй последовательное выполнение:
/start-feature {feature-name}
```

STOP execution.

**If waves.md exists:**

Read `work/{feature-name}/waves.md`.

**Extract from frontmatter:**
- `total_waves` - total number of waves
- `completed_waves` - how many waves are already done

**Extract wave information:**

Parse each wave section and extract:
- Wave number
- Status (pending/completed)
- List of task files in this wave

**Store wave execution plan.**

**Validate waves.md is not stale (staleness check):**

Extract all task numbers mentioned in waves.md from all waves.

Find actual task files:

```bash
find work/{feature-name}/tasks -name "*.md" -type f 2>/dev/null
```

Extract task numbers from actual files.

Compare lists:
- If waves.md mentions tasks that don't exist → stale
- If actual tasks exist that aren't in waves.md → stale

**If waves.md is stale:**

Tell user:

```
⚠️ План waves.md устарел!

Задачи изменились с момента создания плана.
Пересоздай план: /plan-task-waves {feature-name}
```

STOP execution.

**If waves.md is valid:**

**Show user:**

```
📊 Найден план выполнения волнами

Всего волн: {total_waves}
Завершено: {completed_waves}

Начинаю выполнение...
```

**Mark todo as completed.**

---

## 4. Execute all waves

**Mark todo as in_progress.**

**For each wave (starting from first incomplete wave):**

### Step 4.1: Prepare wave execution

**Update TodoWrite** - create detailed plan for current wave:

```json
[
  {"content": "Волна {N}: задача 1", "status": "pending", "activeForm": "Выполнение задачи 1"},
  {"content": "Волна {N}: задача 2", "status": "pending", "activeForm": "Выполнение задачи 2"},
  ...
]
```

Tell user:

```
🌊 Wave {N}/{total_waves}
Задач в волне: {count}
Запускаю параллельное выполнение...
```

### Step 4.2: Execute all tasks in wave in parallel

**Check status of each task in wave:**

For each task in current wave, read task file frontmatter and check `status` field.

**Filter tasks:**
- If status: done → skip this task (already completed)
- If status: planned OR in_progress → include in execution

**If ALL tasks in wave are done:**

Skip to Step 4.9 (update waves.md for completed wave).

**For tasks to execute:**

**IMPORTANT:** Launch ALL incomplete tasks in the wave in parallel using single message with multiple Task tool calls.

**For EACH incomplete task, use Task tool with subagent_type="code-developer":**

**Provide this prompt for each:**

```
Implement task: work/{feature-name}/tasks/{N}.md

Read the task file - it contains what to do.
Read all Context Files referenced in the task.
Tech-spec file: work/{feature-name}/tech-spec.md

Workflow:
1. Update task status in frontmatter from "planned" to "in_progress"
2. Implement functionality according to task description
3. Write comprehensive unit tests
4. Run tests, ensure all pass
5. Update task status to "done"
6. Update tech-spec.md - find this task's line in "## Implementation Tasks" section and replace ☐ with ✅

Return JSON in your specification format.
```

**Send ALL code-developer calls in parallel.**

**Wait for ALL responses.**

### Step 4.3: Validate all task results

**For EACH task response:**

**Extract from JSON:**
- `status` (must be "success")
- `modifiedFiles` (must be non-empty array)
- `createdTests` (must be non-empty array)
- `testsPassed` (must be true)
- `summary`

**Collect tasks by status:**
- `successTasks` - validation passed (status=success AND all checks passed)
- `failedTasks` - any other status OR validation failed

### Step 4.4: Retry failed or incomplete tasks

**If failedTasks is NOT empty:**

Tell user:

```
⚠️ Некоторые задачи требуют исправления (ошибки, невалидация, неполное выполнение):
{list failed task numbers}

Перезапускаю...
```

**Launch code-developer again for EACH failed task in PARALLEL:**

```
Task: work/{feature-name}/tasks/{N}.md

PROBLEMS FROM PREVIOUS RUN:
{copy entire previous response or problem description}

Fix all issues and complete the task correctly.
Tech-spec file: work/{feature-name}/tech-spec.md

Workflow:
1. Update task status → in_progress (if not done yet)
2. Fix identified problems
3. Implement missing functionality
4. Write/fix tests
5. Run tests - all must pass
6. Update status → done
7. Update tech-spec.md - find this task's line in "## Implementation Tasks" section and replace ☐ with ✅

Return correct JSON.
```

**Wait for all retry responses.**

**Validate again.**

**If still failing after retry:** Ask user for guidance on these specific tasks.

### Step 4.5: Collect all modified files from wave

**Combine modifiedFiles from ALL successful tasks in this wave.**

**Create unique list of all files changed in this wave.**

### Step 4.6: Update tech-spec for all tasks in wave

**Read tech-spec:**

Read `work/{feature-name}/tech-spec.md`.

**For each task in wave:**

Find the task line in "## Implementation Tasks" section.

Use Edit tool to change:
```markdown
- [Task {N}: description](tasks/{N}.md) ☐
```
to:
```markdown
- [Task {N}: description](tasks/{N}.md) ✅
```

### Step 4.9: Update waves.md for completed wave

**Use Edit tool** to update waves.md:

Change wave section status from pending to completed:
```markdown
**Status:** pending
```
to:
```markdown
**Status:** completed
```

Change task checkboxes from unchecked to checked:
```markdown
- [ ] Task ...
```
to:
```markdown
- [x] Task ...
```

**Update frontmatter** `completed_waves`:

```yaml
completed_waves: {N}
```

### Step 4.10: Git commit entire wave

**Commit only, NO push.**

**EXECUTE this command:**

```bash
git add work/{feature-name}/tasks/*.md work/{feature-name}/tech-spec.md work/{feature-name}/waves.md {список ВСЕХ modifiedFiles через пробел} && git commit -m "$(cat <<'EOF'
feat({feature-name}): complete wave {N} - {count} tasks

Wave {N}/{total_waves} completed:
{list task numbers and brief titles}

Modified files: {count}

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Verify commit:**

```bash
git log -1 --oneline
```

### Step 4.11: Update TodoWrite

**Mark all task todos for this wave as completed.**

### Step 4.12: Report wave completion

Tell user:

```
✅ Wave {N}/{total_waves} завершена!

Выполнено задач: {count}
Commit создан

{if more waves}
Переход к следующей волне...
{endif}
```

### Step 4.13: Next wave

**If more waves remaining:** Go to step 4.1 for next wave.

**If all waves completed:**

Tell user:

```
🎉 Все волны выполнены!

Всего волн: {total_waves}
Всего задач: {total_tasks}

Переход к финальным проверкам...
```

**Mark "Выполнить все волны задач" todo as completed.**

---

## 5. Run integration tests

**Mark todo as in_progress.**

**Read tech-spec to check if integration tests are mentioned:**

Read `work/{feature-name}/tech-spec.md` and find section "## Testing".

**If integration tests are NOT mentioned:**

Skip this step. Mark todo as completed.

**If integration tests are mentioned:**

**Check if integration test task exists:**

```bash
grep -l "integration test" work/{feature-name}/tasks/*.md 2>/dev/null
```

**If integration test task file exists:**

Read that task file and run integration tests.

**If tests FAIL:**

Launch code-developer:

```
Fix failing integration tests for feature: {feature-name}

PROBLEM:
{output of failed tests}

Your task:
1. Find and fix the cause of test failures
2. Run tests again
3. Ensure all pass

Return JSON with results.
```

Repeat until tests pass.

**Commit only, NO push.**

**Git commit:**

```bash
git add . && git commit -m "test: fix integration tests for {feature-name}"
```

**Mark todo as completed.**

---

## 6. Code review and security audit of entire feature

**Mark todo as in_progress.**

**Collect all modified files from all commits in this feature:**

```bash
git log --name-only --pretty=format: work/{feature-name}/ | sort -u | grep -v "^$"
```

Store list of files.

**Use Task tool TWO times in PARALLEL (single message with 2 tool calls):**

### Check 1: Code reviewer

**subagent_type="code-reviewer"**

**Prompt:**

```
Code review for feature: {feature-name}

Files to review:
{list of all modified files}

User spec: work/{feature-name}/user-spec.md
Tech spec: work/{feature-name}/tech-spec.md

Context files:
- .claude/skills/project-knowledge/guides/project.md
- .claude/skills/project-knowledge/guides/architecture.md
- .claude/skills/project-knowledge/guides/patterns.md
- .claude/skills/project-knowledge/guides/database.md
- .claude/skills/project-knowledge/guides/deployment.md
- .claude/skills/project-knowledge/guides/ux-guidelines.md
- .claude/skills/project-knowledge/guides/monitoring.md
- .claude/skills/project-knowledge/guides/business-rules.md

Read all specified files and conduct comprehensive code review.

Return JSON in your specification format.
```

### Check 2: Security auditor

**subagent_type="security-auditor"**

**Prompt:**

```
Security audit for feature: {feature-name}

Files to audit:
{list of all modified files}

User spec: work/{feature-name}/user-spec.md
Tech spec: work/{feature-name}/tech-spec.md

Conduct comprehensive security audit based on OWASP Top 10.
Run npm audit (or equivalent for the project).

Return JSON in your specification format.
```

**Wait for both responses.**

**Mark todo as completed.**

---

## 7. Fix issues if found

**Mark todo as in_progress.**

**Analyze code-reviewer and security-auditor responses.**

**Extract critical and high severity issues:**
- From code-reviewer: `criticalIssues` where `severity: "critical"`
- From security-auditor: `findings` where `severity: "critical" OR "high"`

**If NO critical/high issues found:**

Tell user: "Code review и security audit пройдены успешно! Критических проблем не найдено."

Skip to step 8.

**If critical/high issues found:**

Show user the issues:

```
Найдены критические проблемы:

CODE REVIEW:
{список criticalIssues}

SECURITY AUDIT:
{список critical/high findings}

Запускаю исправление...
```

**Launch code-developer to fix issues:**

```
Fix critical issues in feature: {feature-name}

CODE REVIEW ISSUES:
{list of criticalIssues with file, line, issue, recommendation}

SECURITY AUDIT ISSUES:
{list of findings with file, line, description, recommendation}

Your task:
1. Fix all listed issues
2. Run tests, ensure nothing broke
3. Return list of fixed files

Return JSON.
```

**Wait for response.**

**Commit only, NO push.**

**Git commit:**

```bash
git add {список исправленных файлов} && git commit -m "fix: address code review and security audit feedback for {feature-name}"
```

**Mark todo as completed.**

---

## 8. Update context documentation

**Mark todo as in_progress.**

**Read current context files:**

Read these files:
- `.claude/skills/project-knowledge/guides/architecture.md`
- `.claude/skills/project-knowledge/guides/patterns.md`
- `.claude/skills/project-knowledge/guides/database.md` (if exists)
- `.claude/skills/project-knowledge/guides/deployment.md` (if exists)
- `.claude/skills/project-knowledge/guides/ux-guidelines.md` (if exists)

**Analyze what was changed in the feature:**

Review user-spec and tech-spec to understand scope:
- `work/{feature-name}/user-spec.md`
- `work/{feature-name}/tech-spec.md`

**Create context update plan:**

Based on the feature changes, create a plan for which context files need updates.

**IMPORTANT:** Context files should be:
- Concise - only essential information
- No code examples - principles and patterns only
- No obvious things - only important project-specific info
- Links and references where relevant
- Architecture decisions and rationale

**Show plan to user:**

```
План обновления context документации:

Файл: .claude/skills/project-knowledge/guides/architecture.md
Изменения:
- [что добавить/изменить]
- [почему это важно]

Файл: .claude/skills/project-knowledge/guides/patterns.md
Изменения:
- [что добавить/изменить]
- [почему это важно]

...

Применить эти изменения?
```

**If user says no:**

Ask: "Какие изменения внести?"

Apply user corrections.

**If user says yes:**

Apply updates using Edit tool for each file.

**Mark todo as completed.**

---

## 9. Finalize tech-spec

**Mark todo as in_progress.**

**Read tech-spec:**

Read `work/{feature-name}/tech-spec.md`.

**Verify all tasks are marked completed:**

Check section "## Implementation Tasks".

All tasks should already be marked ✅.

**If any task is still marked ☐:**

This indicates an error. Check task file status and update tech-spec manually if needed.

**Update tech-spec frontmatter status:**

Change `status` to `implemented`.

**Commit only, NO push.**

**Git commit:**

```bash
git add work/{feature-name}/tech-spec.md && git commit -m "docs: mark feature {feature-name} as implemented"
```

**Mark todo as completed.**

---

## 10. Git push

**Mark todo as in_progress.**

**Show summary to user:**

```
✅ Фича {feature-name} завершена!

Выполнено волн: {waves_count}
Выполнено задач: {tasks_count}
Commits: {count commits}
Code review: пройден
Security audit: пройден
Context: обновлён
Tech-spec: обновлён

Готов к push на GitHub. Push?
```

**If user says no:**

STOP execution. Tell user: "Команда завершена. Push вручную когда будешь готов."

**If user says yes:**

**EXECUTE this command:**

```bash
git push
```

**Mark todo as completed.**

---

## 11. Report completion

**Mark todo as in_progress.**

Tell user:

```
🎉 Фича {feature-name} полностью реализована и отправлена в репозиторий!

Итого:
- ✅ Выполнено волн: {waves_count}
- ✅ Выполнено задач: {tasks_count}
- ✅ Все тесты прошли
- ✅ Code review пройден
- ✅ Security audit пройден
- ✅ Context обновлён
- ✅ Изменения запушены

⚡️ Использовано параллельное выполнение - экономия времени ~{speedup}x

Следующий шаг - ручное тестирование на dev окружении:
1. Deploy на dev
2. Протестируй все сценарии из user-spec
3. Если найдены баги - создай новые задачи: /new-feature

Фича готова к merge в main после тестирования!
```

**Mark todo as completed.**
