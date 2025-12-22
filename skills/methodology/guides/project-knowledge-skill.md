# Project Knowledge Skill: 9 Guides for Project Context

## Обзор

project-knowledge skill в `.claude/skills/project-knowledge/` хранит всю необходимую информацию о проекте для AI-агентов. Это Single Source of Truth для технических решений.

**Структура:**
```
.claude/skills/project-knowledge/
├── SKILL.md          # Skill manifest with activation description
└── guides/           # 9 documentation guides
    ├── project.md
    ├── architecture.md
    ├── patterns.md
    ├── database.md
    ├── deployment.md
    ├── git-workflow.md
    ├── ux-guidelines.md
    ├── monitoring.md
    └── business-rules.md
```

**Принцип:** Каждая информация в одном месте, остальные ссылаются на нее.

**Язык:** Все guides на английском (tech docs).

**Активация:** Skill активируется когда агент нужна информация об архитектуре, tech stack, паттернах кода, database, deployment, git workflow или UX guidelines.

---

## 1. project.md

### Назначение
Описание проекта: проблема, аудитория, функциональность, MVP scope, метрики успеха.

### Когда создается
- **Новый проект:** `/init-project-discovery` (интервью с пользователем)
- **Онбординг:** `/init-project-discovery` (интервью на основе existing кода)

### Для кого
Человек и агент - оба читают и понимают что мы строим.

### Содержит
- **Problem Statement** - Какую проблему решаем
- **Target Audience** - Для кого
- **Core Functionality** - Основные возможности
- **MVP Scope** - Что входит в минимальный продукт
- **Constraints** - Ограничения (бюджет, сроки, технологии)
- **Success Metrics** - Метрики успеха
- **Out of Scope** - Что НЕ входит (важно!)

### Когда обновляется
При изменении vision, scope, или pivot.

### Пример использования
- Агент читает при создании Tech Spec для фичи
- Проверяет что фича соответствует project scope
- Предупреждает если выходит за рамки MVP

---

## 2. architecture.md

### Назначение
Tech stack, архитектурные решения, обоснование выбора технологий.

### Когда создается
- **Новый проект:** `/init-context` (после product discovery)
- **Онбординг:** `/init-context-old` (извлекается из audit)

### Обновляется
При добавлении новых технологий или изменении архитектуры.

### Содержит
- **Tech Stack** - Фреймворки, языки, библиотеки с версиями
- **Architecture Type** - Monolith / Microservices / Serverless
- **Frontend** - React/Vue/Svelte, state management
- **Backend** - Express/FastAPI/Django, API type (REST/GraphQL)
- **Database** - См. database.md (ссылка)
- **Authentication** - JWT/OAuth/Sessions
- **File Storage** - S3/Cloudinary/local
- **External Services** - Payments, email, analytics
- **Context7 Availability** - Упоминание что Context7 доступен
- **Decision Rationale** - Почему выбраны эти технологии

### Пример использования
- code-developer читает перед началом задачи
- Проверяет существующий stack перед добавлением новой зависимости
- Context7 фетчит актуальную документацию для указанных технологий

---

## 3. database.md

### Назначение
Database schema, migrations strategy, query patterns, indexing.

### Когда создается
- **Новый проект:** `/init-context` (если есть БД в tech stack)
- **Онбординг:** `/init-context-old` (если есть БД в audit)

### Обновляется
При изменении schema, добавлении таблиц/коллекций.

### Содержит
- **Database Type** - PostgreSQL / MySQL / MongoDB / SQLite
- **Schema** - Таблицы/коллекции с полями и типами
- **Relationships** - Foreign keys, references
- **Indexes** - Какие поля индексированы
- **Migration Strategy** - Как применяются изменения schema
- **Query Patterns** - Типичные запросы и оптимизации
- **Seeding** - Test data strategy

### Когда НЕ создается
Если проект без БД (например, статический сайт, CLI tool).

### Пример использования
- code-developer проверяет schema перед написанием query
- Обновляет файл при добавлении новой таблицы
- Документирует migration после изменения schema

---

## 4. deployment.md

### Назначение
Deployment setup, environment variables, CI/CD pipeline, commands.

### Когда создается
**Всегда** - в `/init-context` для новых проектов, `/init-context-old` для онбординга.

### Обновляется
- `/setup-infrastructure` - добавляет CI/CD детали
- При изменении deployment target
- При добавлении новых env variables

### Содержит
- **Deployment Target** - Vercel / Railway / AWS / Fly.io / Docker
- **Environment Variables** - Список всех env vars с описанием
- **CI/CD Pipeline** - GitHub Actions / GitLab CI config
- **Build Commands** - Как собрать проект
- **Deploy Commands** - Как задеплоить вручную
- **Secrets Configuration** - Где настроить secrets (GitHub, Vercel, etc.)
- **Rollback Strategy** - Как откатить deploy

### Пример использования
- code-developer читает перед добавлением нового env var
- infrastructure skill обновляет при setup CI/CD
- Документирует где пользователь должен настроить secrets

---

## 5. ux-guidelines.md

### Назначение
UI text, tone of voice, design system, component library.

### Когда создается
- **Новый проект:** `/init-context` (если есть UI)
- **Онбординг:** `/init-context-old` (если есть UI в audit)

### Обновляется
При изменении design system или UI guidelines.

### Содержит
- **Tone of Voice** - Formal / Friendly / Professional
- **UI Text Guidelines** - Как писать тексты в интерфейсе
- **Design System** - Цвета, шрифты, spacing
- **Component Library** - Используемые компоненты (Shadcn, MUI, custom)
- **Accessibility** - ARIA labels, keyboard navigation
- **Responsive Design** - Mobile-first / Desktop-first
- **Localization** - Языки, i18n strategy

### Когда НЕ создается
Если проект без UI (например, API, CLI tool, backend service).

### Пример использования
- code-developer читает перед созданием UI компонентов
- Проверяет tone of voice перед написанием error messages
- Использует указанную component library

---

## 6. patterns.md

### Назначение
Code patterns, best practices, architectural decisions, code conventions.

### Когда создается
Из шаблона - уже хорошо заполнен базовыми паттернами.

### Обновляется
При появлении новых паттернов в процессе разработки.

### Содержит (из шаблона)
- **Code Style** - ESLint/Prettier config, naming conventions
- **Folder Structure** - Separation of concerns (services, models, controllers)
- **Error Handling** - Try/catch patterns, custom errors
- **Testing Patterns** - Mocking, test structure
- **Logging** - Logging strategy
- **Performance** - Caching, optimization patterns
- **Security** - Input validation, sanitization

### Пример использования
- code-developer читает перед написанием нового кода
- code-reviewer проверяет соответствие паттернам
- Обновляется если команда решает изменить подход

---

## 7. git-workflow.md

### Назначение
Git branching strategy, commit conventions, PR process, code review rules.

### Когда создается
Из шаблона - уже хорошо заполнен стандартным git workflow.

### Обновляется
- `/setup-infrastructure` - добавляет CI/CD детали
- При изменении git strategy

### Содержит (из шаблона)
- **Branching Strategy** - main/dev branches, feature branches
- **Commit Conventions** - Conventional Commits (feat/fix/chore)
- **PR Process** - Review requirements, merge strategy
- **Code Review Rules** - What to check, approval requirements
- **CI/CD Integration** - Which checks must pass before merge
- **Pre-commit Hooks** - gitleaks, linting

### Пример использования
- Агент следует commit conventions при коммите
- Проверяет git status перед началом фичи
- Создает feature branch по правилам

---

## 8. monitoring.md

### Назначение
Observability infrastructure: логирование, error tracking, метрики, health checks, alerting.

### Когда создается
Из минималистичного шаблона при `/init-project` или `/old-project`.

### Обновляется
- При настройке production мониторинга
- При добавлении error tracking (Sentry, Rollbar)
- При настройке метрик и алертов

### Содержит
- **Logging** - Где хранятся логи (stdout, CloudWatch, файлы), формат, retention
- **Error Tracking** - Инструмент (Sentry/None), конфигурация, что отслеживается
- **Metrics** - Analytics (GA, Vercel Analytics), performance tracking
- **Health Checks** - Endpoints для проверки состояния
- **Alerts** - Инструменты алертинга, правила, получатели

### Когда НЕ заполняется
Для маленьких проектов может остаться минимальным: "No monitoring - logs to stdout only"

### Пример использования
- Агент знает где искать логи при debugging
- При ошибке знает как создать Sentry issue
- Понимает какие метрики отслеживаются

---

## 9. business-rules.md

### Назначение
Domain-specific бизнес-логика: workflows, validation rules, calculations, state machines.

### Когда создается
Из минималистичного шаблона (в комментариях) при `/init-project` или `/old-project`.

### Обновляется
- При добавлении сложной domain логики
- При появлении multi-step workflows
- При добавлении расчетных формул

### Содержит
- **Multi-step Workflows** - Переходы состояний (order: pending → paid → shipped)
- **Validation Rules** - Бизнес-ограничения (booking: cancel 24h before)
- **Calculations** - Формулы (pricing: (subtotal - discount) * tax + shipping)
- **State Machines** - Lifecycle entities (subscription states)
- **Access Control** - Доступ к фичам по тарифам

### Когда НЕ заполняется
Для simple CRUD или utility проектов файл можно удалить или написать "N/A - no complex business logic"

### Пример использования
- Агент понимает допустимые переходы состояний
- Знает формулы для расчетов
- Следует бизнес-правилам при валидации

---

## Принципы работы с Project Knowledge Skill

### Just-In-Time Loading через Skill Activation
Skill активируется когда агенту нужна информация о проекте. SKILL.md загружается с описанием доступных guides, агент читает только нужные:

- **Task development** → architecture.md, patterns.md, database.md (если нужен)
- **UI task** → architecture.md, patterns.md, ux-guidelines.md
- **Deployment task** → deployment.md, git-workflow.md
- **New feature** → project.md, architecture.md (scope check)

### Single Source of Truth
Каждая информация в одном месте:
- Tech stack → architecture.md (НЕ в CLAUDE.md)
- Database schema → database.md (НЕ в architecture.md)
- Env vars → deployment.md (НЕ в README)
- Git strategy → git-workflow.md (НЕ в CLAUDE.md)

### Version Control
Весь skill (включая guides) в git:
- История изменений через `git log`
- Review через `git diff`
- Rollback через `git revert`

### Updates
Guides обновляются:
- **Manual** - пользователь может редактировать напрямую
- **Through specs** - при создании фич агент предлагает обновить guides
- **After infrastructure** - `/setup-infrastructure` обновляет deployment.md и git-workflow.md

---

## Troubleshooting

### Guide файл пустой или неполный
- Заполни вручную или используй соответствующую команду
- `/init-context` для новых проектов
- `/init-context-old` для онбординга

### Информация устарела
- Обнови guide напрямую
- Git commit с описанием изменения
- Агент увидит актуальное состояние

### Дублирование информации
- Выбери один guide как Single Source of Truth
- Удали дубликаты из других мест
- Добавь ссылки где нужно

### Guides слишком большие
- Нормально! Это лучше чем монолитный CLAUDE.md
- Skill active загружает SKILL.md, guides читаются по требованию
- Progressive Disclosure работает

### Skill не активируется
- Проверь что SKILL.md существует
- Проверь что description в SKILL.md соответствует use case
- Можно явно прочитать guide: `Read .claude/skills/project-knowledge/guides/architecture.md`
