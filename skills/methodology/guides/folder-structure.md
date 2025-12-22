# Структура проекта

AI-First методология использует две ключевые структуры:
1. **Глобальная папка** `~/.claude/` - единый репозиторий для всех проектов
2. **Локальная папка проекта** - структура конкретного проекта

---

## Глобальная папка `~/.claude/`

Мета-проект для разработки и хранения AI-First методологии. Изменения здесь влияют на ВСЕ проекты.

```
~/.claude/
├── shared/                          # Общие ресурсы для всех проектов
│   ├── templates/                   # Шаблоны проектов
│   │   ├── new-project/             # Шаблон нового проекта
│   │   │   ├── .claude/
│   │   │   │   └── skills/project-knowledge/  # Project knowledge skill with 9 guides
│   │   │   ├── .gitignore           # Security-focused gitignore
│   │   │   ├── CLAUDE.md            # Project instructions template
│   │   │   ├── README.md            # Project README template
│   │   │   └── work/                # Work items folder
│   │   ├── infrastructure/          # Infrastructure templates
│   │   │   ├── husky-pre-commit-gitleaks.sh
│   │   │   ├── smoke.test.ts
│   │   │   └── test_smoke.py
│   │   └── old-folder-audit.md      # Legacy code audit template
│   ├── guides/                      # Документация методологии (русский)
│   │   ├── README.md                # Главный хаб
│   │   ├── folder-structure.md      # Этот файл
│   │   └── workflows/               # 3 основных workflow
│   │       ├── new-project.md
│   │       ├── onboarding.md
│   │       └── feature-dev.md
│   └── rules/                       # Legacy правила для агентов (English)
├── skills/                          # Skills для агентов (новая система)
│   ├── testing/                     # Testing strategy skill
│   │   ├── skill.md
│   │   └── guides/                  # Bundled guides
│   ├── infrastructure/              # Infrastructure setup skill
│   │   ├── skill.md
│   │   └── guides/
│   └── command-manager/             # Command management skill
├── agents/                          # Глобальные субагенты
│   ├── code-developer/
│   ├── code-reviewer/
│   └── security-auditor/
├── commands/                        # Slash-команды
│   ├── init-project.md
│   ├── new-feature.md
│   ├── start-feature.md
│   └── ... (всего 19 команд)
├── hooks/                           # Automation hooks
├── CLAUDE.md                        # ГЛОБАЛЬНЫЕ инструкции для Claude
├── projects-registry.json           # Реестр всех AI-First проектов
└── backlog.md                       # Backlog мета-проекта
```

### Что версионируется в git

```bash
# Версионируется
shared/templates/
skills/
agents/
commands/
hooks/
CLAUDE.md
projects-registry.json

# НЕ версионируется (.gitignore)
*.log
.DS_Store
node_modules/
```

---

## Локальная папка проекта

Структура создается автоматически через `/init-project` или `/old-project`.

```
my-project/
├── .claude/                         # Claude configuration
│   ├── skills/                      # Project-specific skills
│   │   └── project-knowledge/       # Project knowledge base
│   │       ├── guides/              # 7 documentation guides
│   │       │   ├── project.md       # Project overview and goals
│   │       │   ├── architecture.md  # Tech stack and architecture
│   │       │   ├── database.md      # Database schema and queries
│   │       │   ├── deployment.md    # Deployment setup and env vars
│   │       │   ├── ux-guidelines.md # UI/UX guidelines and tone
│   │       │   ├── patterns.md      # Code patterns and conventions
│   │       │   └── git-workflow.md  # Git branching strategy
│   │       └── SKILL.md             # Skill manifest
│   └── settings.json                # Claude workspace settings
├── work/                            # Work items (features/bugs)
│   ├── payment-integration/         # Active feature
│   │   ├── user-spec.md             # User specification (русский)
│   │   ├── tech-spec.md             # Technical specification (English)
│   │   └── tasks/                   # Task breakdown
│   │       ├── 1.md                 # Task 1
│   │       ├── 2.md                 # Task 2
│   │       └── 3.md                 # Task 3
│   ├── completed/                   # Completed features (archive)
│   │   └── auth-system/             # Example completed feature
│   └── templates/                   # Templates for work items
├── agents/                          # Project-specific agents (optional)
├── commands/                        # Project-specific commands (optional)
├── hooks/                           # Project-specific hooks (optional)
├── src/                             # Source code
├── tests/                           # Tests
├── .env                             # Environment variables (NOT in git)
├── .env.example                     # Env template (in git)
├── .gitignore                       # Git ignore rules
├── CLAUDE.md                        # Project-specific Claude instructions
├── README.md                        # Project README
├── package.json                     # Dependencies (Node.js example)
└── old/                             # Legacy code (only for migrated projects)
    └── old-folder-audit.md          # Legacy code audit report
```

### Что версионируется в git

```bash
# Версионируется
.claude/skills/project-knowledge/
.claude/rules/project/
.claude/settings.json
guides/project/
work/
src/
tests/
.gitignore
.env.example
CLAUDE.md
README.md
package.json
old/                                 # Если миграция старого проекта

# НЕ версионируется (.gitignore)
.env                                 # Секреты!
*.key                                # Private keys
credentials.json                     # Credentials
secrets/                             # Secrets folder
node_modules/                        # Dependencies
dist/                                # Build artifacts
.DS_Store                            # System files
*.log                                # Logs
```

---

## Context Files (7 файлов)

### 1. project.md
Описание проекта: проблема, аудитория, функциональность, MVP scope, метрики успеха.
- **Когда создается:** `/init-project-discovery`
- **Для кого:** Человек и агент
- **Язык:** English

### 2. architecture.md
Tech stack, архитектурные решения, почему выбран тот или иной подход.
- **Когда создается:** `/init-context` или `/init-context-old`
- **Обновляется:** При добавлении новых технологий
- **Язык:** English

### 3. database.md
Database schema, migrations strategy, query patterns, indexing.
- **Когда создается:** `/init-context` (если есть БД)
- **Обновляется:** При изменении schema
- **Язык:** English

### 4. deployment.md
Deployment setup, environment variables, CI/CD pipeline, commands.
- **Когда создается:** `/init-context`
- **Обновляется:** `/setup-infrastructure`
- **Язык:** English

### 5. ux-guidelines.md
UI text, tone of voice, design system, component library.
- **Когда создается:** `/init-context` (если есть UI)
- **Обновляется:** При изменении UI guidelines
- **Язык:** English

### 6. patterns.md
Code patterns, best practices, architectural decisions, code conventions.
- **Когда создается:** Из шаблона (хорошо заполнен)
- **Обновляется:** При появлении новых паттернов
- **Язык:** English

### 7. git-workflow.md
Git branching strategy, commit conventions, PR process, code review rules.
- **Когда создается:** Из шаблона (хорошо заполнен)
- **Обновляется:** `/setup-infrastructure` (CI/CD детали)
- **Язык:** English

---

## Work Items Structure

```
work/feature-name/
├── user-spec.md              # Что хотим (русский)
├── tech-spec.md              # Как реализовать (English)
└── tasks/                    # Atomic задачи
    ├── 1.md                  # Task 1: Backend auth
    ├── 2.md                  # Task 2: Frontend login
    ├── 3.md                  # Task 3: Integration tests
    └── 4.md                  # Task 4: E2E tests
```

**Нумерация:** Локальная для каждой фичи (начинается с 1).

**Frontmatter в каждом task файле:**
```yaml
---
status: planned | in_progress | done
type: implementation | test | documentation
---
```

---

## Templates

### new-project template
Полная структура нового проекта. Копируется через `/init-project`.
- 7 context файлов (templates с примерами)
- `.gitignore` (security-focused)
- `CLAUDE.md` (template)
- `README.md` (template)

### infrastructure template
Инфраструктурные файлы. Используются в `/setup-infrastructure`.
- Pre-commit hooks (gitleaks)
- Test templates (smoke tests)
- Docker templates
- CI/CD templates

### old-folder-audit template
Шаблон для аудита legacy кода. Используется в `/old-folder-audit`.

---

## Принципы организации

### Just-In-Time Context
Агент читает только нужные файлы для текущей задачи:
- Task → читает task.md, tech-spec.md, user-spec.md
- Feature → читает все tasks, tech-spec, context files
- Context update → читает только updated files

### Single Source of Truth
Каждая информация в одном месте:
- Project description → project.md
- Tech stack → architecture.md
- Database schema → database.md
- Deployment → deployment.md

### Progressive Disclosure
Информация раскрывается от общего к частному:
1. project.md (что строим)
2. architecture.md (на чем строим)
3. user-spec.md (что хотим в фиче)
4. tech-spec.md (как реализуем фичу)
5. tasks/*.md (конкретные задачи)

### Git-Friendly Documentation
Всё версионируется в git:
- История изменений через git log
- Review через git diff
- Rollback через git revert
- Reasoning в комментариях и описаниях
