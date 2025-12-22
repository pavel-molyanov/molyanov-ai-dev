# Key Concepts: Deep Dive

## Overview

AI-First методология построена на 6 ключевых концепциях. Этот документ содержит детальное объяснение каждой концепции с примерами и обоснованием.

---

## 1. Just-In-Time Context

### Концепция
Агент читает только необходимую информацию для текущей задачи, не загружая весь контекст проекта.

### Проблема
Традиционный подход: монолитный CLAUDE.md с 10,000+ строк. При каждом запросе весь файл попадает в context window. Это:
- Расходует tokens
- Замедляет обработку
- Достигает context limits
- Включает нерелевантную информацию

### Решение
Распределенная Knowledge Base с модульными файлами:
- project-knowledge skill с 9 guides (каждый 50-500 строк)
- Work items в отдельных папках
- Specs и tasks в структурированном виде

Агент читает только нужное:
```
Task development → architecture.md + patterns.md + task.md (300 строк)
vs
Monolithic CLAUDE.md (10,000 строк)
```

**Экономия:** 97% context window освобождается для кода и анализа.

### Как работает
1. Команда `/start-task feature-name 1` запускается
2. code-developer читает:
   - `work/feature-name/tasks/1.md` (task description)
   - `work/feature-name/tech-spec.md` (technical approach)
   - `.claude/skills/project-knowledge/guides/architecture.md` (tech stack)
   - `.claude/skills/project-knowledge/guides/patterns.md` (code conventions)
3. НЕ читает:
   - project.md (не нужен для конкретной задачи)
   - database.md (если задача не про БД)
   - ux-guidelines.md (если задача не про UI)
   - Другие tasks (не релевантны)

### Примеры

**Пример 1: Backend API задача**
```
Читает:
- architecture.md (tech stack, API framework)
- patterns.md (error handling, logging)
- database.md (schema, если нужны query)
- tech-spec.md (technical approach)
- task.md (конкретная задача)

НЕ читает:
- ux-guidelines.md (нет UI)
- deployment.md (не про deploy)
- git-workflow.md (не про git)
```

**Пример 2: UI компонент**
```
Читает:
- architecture.md (frontend framework)
- ux-guidelines.md (design system, tone of voice)
- patterns.md (component structure)
- tech-spec.md
- task.md

НЕ читает:
- database.md (нет DB queries)
- deployment.md (не про deploy)
```

### Бенефиты
- **Меньше tokens** - экономия на API costs
- **Быстрее** - меньше обработки
- **Фокус** - только релевантная информация
- **Масштабируемость** - проект может расти без проблем с context

---

## 2. Single Source of Truth

### Концепция
Каждая информация хранится в одном месте, остальные ссылаются на нее.

### Проблема
Традиционный подход: дублирование информации в разных файлах:
- Tech stack описан в CLAUDE.md, README.md, package.json comments
- Database schema в migrations, docs, комментариях
- Deployment instructions в README, DEPLOY.md, CI config comments

**Последствия:**
- Outdated information (обновили в одном месте, забыли в другом)
- Conflicts (разные версии truth в разных файлах)
- Confusion (какой файл актуальный?)

### Решение
Четкая иерархия: каждая информация в одном designated файле.

**Mapping (project-knowledge skill guides):**
- Tech stack → `architecture.md`
- Database schema → `database.md`
- Deployment → `deployment.md`
- Git workflow → `git-workflow.md`
- Code patterns → `patterns.md`
- UX guidelines → `ux-guidelines.md`
- Project description → `project.md`

All guides live in `.claude/skills/project-knowledge/guides/` and are accessed through the project-knowledge skill.

### Как работает
1. Агент нужна информация о tech stack
2. Читает `.claude/skills/project-knowledge/guides/architecture.md` (и только его)
3. Не ищет в README, package.json, comments
4. Single Source of Truth гарантирует актуальность

### Примеры

**Плохо:**
```
README.md: "Using React 18"
package.json: "react": "^17.0.0"
CLAUDE.md: "Frontend: React 19"
```
**Кто прав?** Непонятно.

**Хорошо:**
```
.claude/skills/project-knowledge/guides/architecture.md:
## Frontend
- Framework: React 18.2.0
- State Management: Zustand
- Routing: React Router v6

Все остальные файлы: НЕ описывают tech stack или ссылаются на architecture.md
```

### Cross-references
Если информация нужна в нескольких местах, используй ссылки:

```markdown
# README.md
For complete tech stack, see [.claude/skills/project-knowledge/guides/architecture.md](.claude/skills/project-knowledge/guides/architecture.md)

# deployment.md
Database configuration: see [database.md](database.md)
```

### Бенефиты
- **Актуальность** - обновил в одном месте, везде актуально
- **Нет конфликтов** - одна версия truth
- **Легко найти** - знаешь где искать
- **Легко обновить** - одно место вместо 5

---

## 3. Spec-Driven Development

### Концепция
Сначала спецификация, потом код. Всегда.

### Проблема
Традиционный подход: код без спецификации:
- Пользователь: "Добавь платежи"
- Агент: "Ок" → начинает писать код
- Через час: "Я добавил Stripe"
- Пользователь: "Мне нужен был PayPal!"

**Последствия:**
- Переделка кода
- Missed requirements
- Scope creep
- No approval before implementation

### Решение
Строгая иерархия спецификаций перед кодом:

```
1. Context (project description) ← Создается один раз
2. User Spec (what + why) ← На русском, для человека
3. Tech Spec (how) ← На английском, для агента
4. Tasks (atomic work items) ← Инкрементальные задачи
5. Code ← Реализация
```

Каждый уровень утверждается перед следующим.

### Workflow

**Шаг 1: User Spec**
```bash
/new-feature
```
- Интервью с пользователем
- Agent создает user-spec.md (русский)
- **Пользователь ревьювит и утверждает**
- Git commit

**Шаг 2: Tech Spec**
```bash
/create-tech-spec feature-name
```
- Agent читает user-spec + все project knowledge guides
- Создает tech-spec.md (English) с technical approach
- **Пользователь ревьювит и утверждает**
- Git commit

**Шаг 3: Tasks**
```bash
/tech-spec-decompose feature-name
```
- Agent разбивает tech-spec на atomic tasks
- **Пользователь ревьювит и утверждает**
- Git commit

**Шаг 4: Implementation**
```bash
/start-task feature-name 1
```
- code-developer реализует задачу
- Пишет unit tests
- Commit

### Примеры

**Плохо:**
```
User: "Добавь аутентификацию"
Agent: *пишет код*
30 минут спустя...
Agent: "Готово, добавил JWT auth"
User: "Мне нужен был OAuth через Google"
```

**Хорошо:**
```
User: "Добавь аутентификацию"
Agent: *запускает /new-feature*
Agent: "Какой тип auth? JWT/OAuth/Magic Link?"
User: "OAuth через Google"
Agent: *создает user-spec.md*
Agent: "Проверь User Spec"
User: *читает, утверждает*
Agent: *создает tech-spec.md*
Agent: "Проверь Tech Spec"
User: *читает, утверждает*
Agent: *создает tasks*
Agent: "Проверь задачи"
User: *утверждает*
Agent: *начинает реализацию*
```

### Бенефиты
- **No surprises** - пользователь видит план до кода
- **Approval points** - можно остановить до wasted работы
- **Clear scope** - все понимают что реализуется
- **Documentation** - specs остаются в git как документация
- **Parallel work** - можно обсуждать specs пока агент работает над другим

---

## 4. Progressive Disclosure

### Концепция
Информация раскрывается постепенно: от общего к частному.

### Проблема
Традиционный подход: вся информация в одном файле на одном уровне:
```markdown
# CLAUDE.md

Project: E-commerce platform
Tech Stack: Next.js, PostgreSQL
Database Schema: users table (id, email, password_hash, ...)
API: POST /api/auth/login accepts {email, password}
Frontend: Login form at /login, uses FormInput component
...
(10,000 строк всего подряд)
```

**Последствия:**
- Cognitive overload
- Трудно найти нужное
- Непонятно что важнее

### Решение
Иерархическая структура с уровнями детализации:

```
Level 1: project.md
  "E-commerce platform for handmade goods"

Level 2: architecture.md
  "Next.js + PostgreSQL + Stripe"

Level 3: user-spec.md
  "Add user authentication"

Level 4: tech-spec.md
  "Implement JWT-based auth with refresh tokens"

Level 5: tasks/1.md
  "Create User model with password hashing"
```

Агент читает столько уровней, сколько нужно для задачи.

### Как работает

**Scenario 1: New feature**
1. Agent читает `project.md` (level 1) - понять scope проекта
2. Читает `architecture.md` (level 2) - понять tech stack
3. Создает `user-spec.md` (level 3) - детализирует фичу
4. Создает `tech-spec.md` (level 4) - технический план
5. Создает tasks (level 5) - atomic работа

**Scenario 2: Existing task**
1. Agent сразу читает `task.md` (level 5) - что делать
2. Читает `tech-spec.md` (level 4) - контекст фичи
3. Читает `architecture.md` (level 2) - tech stack
4. НЕ читает `project.md` (level 1) - не нужен

### Примеры

**Project structure reflects levels:**
```
.claude/skills/project-knowledge/    # Project knowledge skill
├── SKILL.md                         # Skill manifest
└── guides/
    ├── project.md                   # Level 1: High-level vision
    ├── architecture.md              # Level 2: Tech decisions
    ├── database.md                  # Level 2: Data model
    ├── deployment.md                # Level 2: Infrastructure
    ├── ux-guidelines.md             # Level 2: Design system
    ├── patterns.md                  # Level 2: Code conventions
    └── git-workflow.md              # Level 2: Process

work/payment-integration/
├── user-spec.md                     # Level 3: Feature description
├── tech-spec.md                     # Level 4: Technical plan
└── tasks/
    ├── 1.md                         # Level 5: Atomic work
    ├── 2.md                         # Level 5: Atomic work
    └── 3.md                         # Level 5: Atomic work
```

### Бенефиты
- **Reduced cognitive load** - читаешь только нужный уровень
- **Easy navigation** - от общего к частному
- **Better understanding** - контекст перед деталями
- **Scalability** - можно добавлять уровни без переделки

---

## 5. Agent Orchestration

### Концепция
Главный агент координирует специализированных субагентов для разных задач.

### Проблема
Традиционный подход: один агент делает все:
- Пишет код
- Ревьювит код
- Находит security issues
- Создает specs
- Настраивает инфраструктуру

**Последствия:**
- Перегрузка контекста
- Нет специализации
- Пропущенные проблемы (security, code quality)

### Решение
Orchestration: главный агент координирует специализированных субагентов.

**Роли:**

**Main Agent:**
- Координирует workflow
- Принимает решения
- Общается с пользователем
- Запускает субагенты

**Subagents:**
- **code-developer** - Пишет код, unit tests, запускает тесты
- **code-reviewer** - Ревьювит качество кода, архитектуру
- **security-auditor** - Проверяет OWASP Top 10, security issues

**Skills:**
- **infrastructure** - Setup CI/CD, Docker, tests
- **testing** - Testing strategy guidance
- **methodology** - Workflow guidance

### Workflow Example

```
User: /start-task payment-integration 1

Main Agent:
1. Читает task, tech-spec, context
2. Создает plan через TodoWrite
3. Запускает code-developer

code-developer:
4. Пишет код
5. Пишет unit tests
6. Запускает tests
7. Возвращает результат Main Agent

Main Agent:
8. Запускает code-reviewer (parallel)
9. Запускает security-auditor (parallel)
10. Если issues → отправляет обратно code-developer
11. Если ок → git commit (gitleaks pre-commit hook сканирует секреты)
12. Обновляет task status → done
```

### Бенефиты
- **Специализация** - каждый агент expert в своей области
- **Parallel execution** - code-reviewer + security-auditor одновременно
- **Quality assurance** - systematic checks
- **Clear responsibilities** - кто за что отвечает

---

## 6. Git-Friendly Documentation

### Концепция
Документация живет в Git вместе с кодом. Reasoning в описаниях компонентов, история в Git.

### Проблема
Традиционный подход:
- Документация в Notion/Google Docs (отдельно от кода)
- Устаревает (код меняется, docs нет)
- Нет версионирования (не понятно что когда изменилось)
- Нет истории решений

### Решение
Все документы в Git:
- Project knowledge skill guides в `.claude/skills/project-knowledge/guides/`
- Work items в `work/`
- Templates в `shared/templates/`
- История через `git log`
- Reasoning в комментариях и описаниях

### Что версионируется

**Версионируется:**
```
.claude/skills/project-knowledge/    # Project knowledge skill & guides
work/                                # All specs and tasks
guides/                              # Methodology guides
.gitignore                           # Security rules
CLAUDE.md                            # Project instructions
README.md                            # User-facing docs
```

**НЕ версионируется:**
```
.env                       # Secrets
*.key                      # Private keys
credentials.json           # Credentials
node_modules/              # Dependencies
dist/                      # Build artifacts
```

### Git Operations

**Review changes:**
```bash
git diff .claude/skills/project-knowledge/guides/architecture.md
```

**See history:**
```bash
git log --follow .claude/skills/project-knowledge/guides/architecture.md
```

**Rollback:**
```bash
git revert <commit-hash>
```

**Branch experiments:**
```bash
git checkout -b experiment/new-architecture
# Edit architecture.md
# Test
# Merge or discard
```

### Бенефиты
- **Versioning** - полная история изменений
- **Review** - git diff для review документации
- **Rollback** - можно откатить документы как код
- **Sync** - документация всегда соответствует коду в ветке
- **Collaboration** - PRs для документации как для кода

---

## Как концепции работают вместе

**Пример: Разработка фичи "Payment Integration"**

1. **Spec-Driven Development** → Сначала User Spec, потом Tech Spec, потом Tasks
2. **Progressive Disclosure** → От project.md к tasks/1.md постепенно
3. **Just-In-Time Context** → code-developer читает только task.md + tech-spec.md + architecture.md
4. **Single Source of Truth** → Tech stack только в architecture.md, не дублируется
5. **Agent Orchestration** → Main agent → code-developer → code-reviewer → security-auditor
6. **Git-Friendly Documentation** → Все specs в git, история решений сохранена

**Результат:** Эффективная, документированная, качественная разработка с минимальным context window usage.
