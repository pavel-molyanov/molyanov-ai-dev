---
description: Decompose tech-spec into atomic tasks
allowed-tools:
  - Bash(git *)
  - Bash(find:*)
  - Bash(grep:*)
  - Read
  - Write
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
  {"content": "Проверить существующий waves.md", "status": "pending", "activeForm": "Проверка waves.md"},
  {"content": "Прочитать все незавершённые задачи", "status": "pending", "activeForm": "Чтение задач"},
  {"content": "Проанализировать зависимости и сгруппировать в волны", "status": "pending", "activeForm": "Анализ и группировка"},
  {"content": "Создать waves.md", "status": "pending", "activeForm": "Создание waves.md"},
  {"content": "Согласовать план с пользователем", "status": "pending", "activeForm": "Согласование плана"},
  {"content": "Git commit", "status": "pending", "activeForm": "Git commit"},
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

Выбери фичу для планирования. Запусти: /plan-task-waves <feature-name>
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

## 3. Check for existing waves.md

**Mark todo as in_progress.**

**Check if waves.md already exists:**

```bash
test -f work/{feature-name}/waves.md && echo "waves-exist" || echo "no-waves"
```

**If output contains "waves-exist":**

Tell user:

```
⚠️ Файл waves.md уже существует!

Если продолжить, он будет перезаписан. Продолжить / Отменить?
```

**If user says "Отменить":**

STOP execution.

**If user says "Продолжить":**

Continue to next step.

**Mark todo as completed.**

---

## 4. Read all incomplete tasks

**Mark todo as in_progress.**

**Find all task files:**

```bash
find work/{feature-name}/tasks -name "*.md" -type f 2>/dev/null | sort
```

**If NO tasks found:**

Tell user: "Задачи не найдены. Сначала декомпозируй tech-spec: `/tech-spec-decompose {feature-name}`"

STOP execution.

**For each task file, read frontmatter and extract:**
- Task number (from filename)
- Status
- Title (from frontmatter)

**Filter only incomplete tasks** (status: planned OR in_progress).

**If all tasks are done:**

Tell user: "Все задачи уже выполнены! Нечего планировать."

STOP execution.

**Store list of incomplete tasks with their file paths.**

**Mark todo as completed.**

---

## 5. Analyze dependencies and group into waves

**Mark todo as in_progress.**

**IMPORTANT:** This is the most critical step. We need to be VERY conservative in determining independence.

**Use Task tool with subagent_type="general-purpose".**

**Provide this prompt:**

```
ultrathink

Analyze task dependencies and group into execution waves for feature: {feature-name}

**Context files to read:**
- .claude/skills/project-knowledge/guides/project.md
- .claude/skills/project-knowledge/guides/architecture.md
- .claude/skills/project-knowledge/guides/patterns.md
- .claude/skills/project-knowledge/guides/database.md (if exists)
- work/{feature-name}/tech-spec.md
- work/{feature-name}/user-spec.md

**Tasks to analyze:**
{list all incomplete task files with paths}

**For EACH task, analyze:**
1. Files to modify/create
2. Code dependencies (functions/modules/APIs it uses)
3. What it creates (new functions/APIs)
4. Database changes (schemas, migrations, FKs)
5. Test files
6. Environment variables (.env, config)
7. Package dependencies (package.json, requirements.txt, go.mod)
8. API contracts (breaking changes to endpoints/types)
9. Middleware dependencies (order-dependent)
10. Import/export dependencies

**Independence criteria (ALL must be true for tasks in same wave):**
1. ✅ NO shared files
2. ✅ NO code dependencies (Task B doesn't use what Task A creates)
3. ✅ NO database dependencies
4. ✅ NO test conflicts
5. ✅ NO shared modules
6. ✅ NO environment variable conflicts
7. ✅ NO package dependency conflicts
8. ✅ NO API contract changes affecting other tasks
9. ✅ NO middleware order dependencies

**Conservative approach:**
- If ANY doubt → tasks are dependent
- Prefer more waves over conflicts

**Wave size limit: max 3 tasks per wave**

**Grouping algorithm:**
1. Find tasks with NO dependencies → Wave 1 (max 3 tasks)
2. If >3 independent tasks → put first 3 in Wave 1, rest in Wave 2
3. Find tasks where ALL dependencies in Wave 1 → add to next available wave (max 3 tasks)
4. Continue until all assigned

**Output JSON:**

```json
{
  "waves": [
    {
      "waveNumber": 1,
      "tasks": [
        {
          "taskFile": "tasks/1.md",
          "taskNumber": "1",
          "title": "Task title",
          "dependsOnTasks": []
        }
      ]
    },
    {
      "waveNumber": 2,
      "tasks": [
        {
          "taskFile": "tasks/2.md",
          "taskNumber": "2",
          "title": "Another task",
          "dependsOnTasks": ["1"]
        }
      ]
    }
  ],
  "reasoning": "Detailed explanation of grouping decisions",
  "conflictsAvoided": [
    "Task 1 and 3: both modify src/api/users.ts",
    "Task 2 depends on Task 1 output"
  ]
}
```

Be thorough and conservative.

**Wait for agent response.**

**Extract waves data from JSON.**

**Mark todo as completed.**

---

## 6. Create and validate waves.md

**Mark todo as in_progress.**

**Read template from:** `~/.claude/shared/work-templates/waves.md`

**Fill template with data from step 5 JSON response.**

**Use Write tool to create file:** `work/{feature-name}/waves.md`

**Validate created waves.md:**

Read created file and verify:
1. Each wave has ≤3 tasks
2. Tasks in same wave have no dependencies on each other
3. All dependsOnTasks are in previous waves
4. No file conflicts within waves (check against JSON from step 5)
5. Wave numbering is sequential (1, 2, 3...)

**If validation fails:**

Fix the issues:
- If wave has >3 tasks → split into multiple waves
- If tasks in same wave depend on each other → move to different waves
- If wave numbering is wrong → renumber
- **If ANY doubt about independence** → move to next wave (conservative approach)

**Conservative principle:**
If not 100% certain tasks are independent → assume dependencies exist → separate waves.

Re-write waves.md with fixes.

**Mark todo as completed.**

---

## 7. Get user approval

**Mark todo as in_progress.**

**Show user the created plan:**

Tell user:

```
📊 План волн создан: work/{feature-name}/waves.md

Всего задач: {N}
Волн: {M}

Проверь план перед коммитом:
```

**Show markdown link:** [work/{feature-name}/waves.md](work/{feature-name}/waves.md)

**Ask user:** "План корректный? Внести изменения / Одобрить / Отменить?"

**If user wants changes:**
- Ask what to change
- Use Edit tool to modify waves.md
- Ask again for approval

**If user cancels:**
- STOP execution

**If user approves:**
- Continue to step 8

**Mark todo as completed.**

---

## 8. Git commit

**Mark todo as in_progress.**

**EXECUTE this command:**

```bash
git add work/{feature-name}/waves.md && git commit -m "$(cat <<'EOF'
docs: create task execution waves plan for {feature-name}

Generated {M} waves for {N} tasks

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

**Verify commit:**

```bash
git log -1 --oneline
```

**Mark todo as completed.**

---

## 9. Report completion

**Mark todo as in_progress.**

Tell user:

```
✅ План волн создан и сохранён!

Файл: work/{feature-name}/waves.md
Волн: {M}
Задач: {N}

Следующий шаг: запусти выполнение
/start-feature-waves {feature-name}
```

**Mark todo as completed.**
