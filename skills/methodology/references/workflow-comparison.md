# Workflow Comparison

## Quick Decision Matrix

| Ситуация | Workflow | Команды |
|----------|----------|---------|
| Создаю новый проект с нуля | [New Project](#new-project-workflow) | `/init-project` → `/init-git` → `/init-project-discovery` → `/init-context` → `/setup-infrastructure` |
| Есть legacy код без документации | [Onboarding](#onboarding-workflow) | `/old-project` → `/old-folder-audit` → `/init-project-discovery` → `/init-context-old` → `/setup-infrastructure-old` |
| Разрабатываю фичу/баг/рефакторинг | [Feature Development](#feature-development-workflow) | `/new-feature` → `/create-tech-spec` → `/tech-spec-decompose` → `/start-task` или `/start-feature` |

---

## Detailed Comparison

### New Project Workflow

**Когда:** Создание нового проекта с нуля.

**Фазы:**
1. **Project Initialization** - `/init-project`, `/init-git`
2. **Product Discovery** - `/init-project-discovery`
3. **Technical Planning** - `/init-context`
4. **Framework & DevOps Setup** - `/setup-infrastructure`

**Результат:**
- ✅ GitHub репозиторий создан
- ✅ Структура `.claude/` и `work/` готова
- ✅ Все 7 context файлов заполнены
- ✅ Framework инициализирован
- ✅ CI/CD настроен
- ✅ Pre-commit hooks активны
- ✅ Готов к разработке первой фичи

**Время:** 30-60 минут

**Детали:** [guides/workflow-new-project.md](../guides/workflow-new-project.md)

---

### Onboarding Workflow

**Когда:** Есть работающий проект, но нет документации и структуры.

**Фазы:**
1. **Legacy Code Preservation** - `/old-project`
2. **Product Discovery** - `/init-project-discovery`
3. **Code Analysis & Audit** - `/old-folder-audit`
4. **Context Creation** - `/init-context-old`
5. **Final Documentation** - CLAUDE.md update
6. **Infrastructure & DevOps** - `/setup-infrastructure-old`

**Результат:**
- ✅ Legacy код сохранен в `old/`
- ✅ Структура `.claude/` и `work/` развернута
- ✅ Context создан на основе audit
- ✅ Infrastructure настроена (tests, CI/CD)
- ✅ Готов к созданию задач рефакторинга

**Время:** 60-90 минут

**Особенность:** Работает в отдельной ветке `feature/migration-ai-first`, production не затрагивается.

**Детали:** [guides/workflow-onboarding.md](../guides/workflow-onboarding.md)

---

### Feature Development Workflow

**Когда:** Ежедневная работа - фичи, баги, рефакторинг.

**Фазы:**
1. **User Spec Creation** - `/new-feature`
2. **Tech Spec Creation** - `/create-tech-spec`
3. **Task Decomposition** - `/tech-spec-decompose`
4. **Implementation** - `/start-task` или `/start-feature`
5. **Testing & Deploy** - integration tests, E2E, manual testing

**Результат:**
- ✅ Фича реализована с specs
- ✅ Unit tests написаны
- ✅ Code reviewed
- ✅ Security audited
- ✅ Готова к deploy

**Время:** Зависит от размера фичи (часы до дней)

**Два режима:**
- **Single Task Mode** (`/start-task`) - ручной контроль, задача за задачей
- **Feature Autopilot** (`/start-feature`) - автоматическая реализация всех задач

**Детали:** [guides/workflow-feature-dev.md](../guides/workflow-feature-dev.md)

---

## Side-by-Side Comparison

| Параметр | New Project | Onboarding | Feature Development |
|----------|-------------|------------|---------------------|
| **Starting point** | Пустая папка | Legacy код | Существующий AI-First проект |
| **Creates structure** | ✅ Да | ✅ Да | ❌ Нет (уже есть) |
| **Product discovery** | ✅ С нуля | ✅ На основе existing | ❌ Нет (проект уже описан) |
| **Context files** | ✅ Все 7 | ✅ 5-7 (зависит от проекта) | ❌ Нет (читает existing) |
| **Framework init** | ✅ Инициализирует | ❌ Использует existing | ❌ Не трогает |
| **CI/CD setup** | ✅ Полный setup | ✅ Добавляет к existing | ❌ Не трогает |
| **Legacy code** | ❌ Нет | ✅ Сохраняет в `old/` | ❌ Не актуально |
| **Git repository** | ✅ Создает | ✅ Использует existing | ✅ Использует existing |
| **Работает в ветке** | main | feature/migration-ai-first | feature/* или dev |
| **Output** | Готовый проект | Мигрированный проект | Реализованная фича |
| **Next step** | Feature Development | Feature Development | Deploy → Next feature |

---

## Command Sequences

### New Project (Full)
```bash
# 1. Create structure
/init-project

# 2. Create GitHub repo
/init-git

# 3. Product discovery interview
/init-project-discovery

# 4. Fill context files
/init-context

# 5. Setup framework & DevOps
/setup-infrastructure

# Result: Ready for first feature
```

**Time:** 30-60 min

---

### Onboarding (Full)
```bash
# 1. Archive old code, create structure
/old-project

# 2. Product discovery interview
/init-project-discovery

# 3. Analyze legacy code
/old-folder-audit

# 4. Create context from audit
/init-context-old

# 5. Setup tests & CI/CD (no framework init)
/setup-infrastructure-old

# Result: Ready for refactoring tasks
```

**Time:** 60-90 min

---

### Feature Development (Full)

**Single Task Mode:**
```bash
# 1. Create User Spec
/new-feature

# 2. Create Tech Spec
/create-tech-spec feature-name

# 3. Decompose into tasks
/tech-spec-decompose feature-name

# 4. Implement tasks one by one
/start-task feature-name 1
/start-task feature-name 2
/start-task feature-name 3

# Result: Feature implemented task by task
```

**Feature Autopilot Mode:**
```bash
# 1. Create User Spec
/new-feature

# 2. Create Tech Spec
/create-tech-spec feature-name

# 3. Decompose into tasks
/tech-spec-decompose feature-name

# 4. Implement all tasks automatically
/start-feature feature-name

# Result: Entire feature implemented automatically
```

**Time:** Hours to days (depends on feature size)

---

## When to Use Each Workflow

### Use New Project When:
- ✅ Starting from scratch
- ✅ No existing codebase
- ✅ Fresh GitHub repository needed
- ✅ Full control over tech stack
- ✅ Clean slate approach

### Use Onboarding When:
- ✅ Existing project with code
- ✅ No (or poor) documentation
- ✅ Want to apply AI-First methodology
- ✅ Need to preserve legacy code
- ✅ Incremental migration preferred

### Use Feature Development When:
- ✅ Project already initialized (via New Project or Onboarding)
- ✅ Context files exist
- ✅ Infrastructure set up
- ✅ Daily development work
- ✅ Features, bugs, refactoring

---

## Common Mistakes

### Wrong Workflow Selection

**Mistake:** Running `/setup-infrastructure` on existing project with framework.
**Fix:** Use `/setup-infrastructure-old` instead (adds tests/CI/CD, doesn't init framework).

**Mistake:** Running `/new-feature` before project initialization.
**Fix:** Run `/init-project` or `/old-project` first.

**Mistake:** Running `/init-context` after `/init-context-old`.
**Fix:** Use `/init-context` for new projects only. For onboarding, use `/init-context-old`.

### Skipping Steps

**Mistake:** Running `/start-feature` without `/tech-spec-decompose`.
**Fix:** Always follow sequence: User Spec → Tech Spec → Tasks → Implementation.

**Mistake:** Skipping `/old-folder-audit` in onboarding.
**Fix:** Audit is critical for understanding legacy code. Don't skip.

### Incorrect Assumptions

**Mistake:** Assuming `/init-project` creates GitHub repo.
**Fix:** `/init-project` only creates local structure. Run `/init-git` separately.

**Mistake:** Assuming `/setup-infrastructure-old` will initialize framework.
**Fix:** It won't. It only adds tests and CI/CD to existing project.

---

## Workflow Transitions

### From New Project to Feature Development
```bash
# Complete New Project workflow
/init-project → /init-git → /init-project-discovery → /init-context → /setup-infrastructure

# ✅ Ready for Feature Development
/new-feature
```

### From Onboarding to Feature Development
```bash
# Complete Onboarding workflow
/old-project → /old-folder-audit → /init-project-discovery → /init-context-old → /setup-infrastructure-old

# ✅ Ready for Feature Development
/new-feature
```

### Multiple Features (Daily Work)
```bash
# Feature 1
/new-feature → /create-tech-spec feature-1 → /tech-spec-decompose feature-1 → /start-feature feature-1

# Feature 2
/new-feature → /create-tech-spec feature-2 → /tech-spec-decompose feature-2 → /start-feature feature-2

# Feature 3...
```

---

## Checklist: Which Workflow?

**Answer these questions:**

1. ☐ Do I have existing code?
   - **No** → New Project
   - **Yes** → Go to question 2

2. ☐ Does the project have `.claude/skills/project-knowledge/guides/` with 7 files?
   - **No** → Onboarding
   - **Yes** → Go to question 3

3. ☐ Am I working on a specific feature/bug?
   - **Yes** → Feature Development
   - **No** → What are you trying to do?

**Result:**
- No existing code → **New Project Workflow**
- Existing code, no AI-First structure → **Onboarding Workflow**
- AI-First structure exists, working on feature → **Feature Development Workflow**

---

## Summary

| | New Project | Onboarding | Feature Development |
|-|-------------|------------|---------------------|
| **Purpose** | Initialize from scratch | Migrate existing project | Daily development |
| **Duration** | 30-60 min | 60-90 min | Hours to days |
| **Commands** | 5 commands | 5 commands | 4-5 commands |
| **Frequency** | Once per project | Once per project | Daily/weekly |
| **Risk** | Low (fresh start) | Medium (migration) | Low (incremental) |
| **Reversible** | N/A (fresh) | Yes (separate branch) | Yes (git revert) |

**Rule of thumb:**
- New project → New Project Workflow
- Existing project → Onboarding Workflow
- Working on features → Feature Development Workflow
