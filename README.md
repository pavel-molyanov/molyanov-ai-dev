# Claude Code Framework

Фреймворк для эффективной работы с Claude Code — набор skills, commands и agents для AI-First разработки.

## Что это?

Коллекция методологий, автоматизаций и шаблонов для Claude Code CLI. Решает ключевую проблему — **потерю контекста между сессиями** через:

- Распределённую базу знаний вместо монолитного CLAUDE.md
- Spec-driven workflow (Context → User Spec → Tech Spec → Tasks → Code)
- Оркестрацию специализированных агентов
- Автоматизацию качества (code review, тесты, security audit)

## Установка

```bash
# Вариант 1: Скопировать в существующую ~/.claude/
git clone https://github.com/pavel-molyanov/claude-code-framework.git
cp -r claude-code-framework/* ~/.claude/

# Вариант 2: Клонировать напрямую (если ~/.claude/ пустая)
git clone https://github.com/pavel-molyanov/claude-code-framework.git ~/.claude
```

---

## Skills

Skills — модульные пакеты знаний, которые автоматически подключаются к контексту Claude Code.

### methodology

**AI-First методология разработки.** Описывает структуру проектов, workflow для новых и legacy проектов, правила работы с документацией. Вызывается когда нужно понять "как правильно организовать проект" или "какой workflow использовать". Содержит decision tree для выбора подхода.

### infrastructure

**Настройка DevOps инфраструктуры.** Покрывает CI/CD (GitHub Actions), Docker, pre-commit hooks (gitleaks для защиты от утечки секретов), тестовую инфраструктуру. Вызывается при создании нового проекта или добавлении автодеплоя. Содержит готовые шаблоны конфигов.

### testing

**Стратегия тестирования.** Описывает тестовую пирамиду: smoke → unit → integration → E2E. Объясняет когда какие тесты писать, как организовать, какой coverage нужен. Вызывается при планировании тестов или когда непонятно "нужны ли тесты для этого кода".

### documentation

**Управление документацией проекта.** Помогает создавать, проверять и обновлять 11 файлов в `.claude/skills/project-knowledge/guides/`. Проводит аудит на bloat (лишний код в доках, очевидная информация). Вызывается при "заполни документацию" или "проверь доки".

### project-planning

**Планирование нового проекта.** Проводит адаптивное интервью и заполняет три файла: project.md (что строим), features.md (полный список фич), roadmap.md (план разработки). Вызывается в начале нового проекта для формирования vision.

### user-spec-planning

**Создание user specification.** Проводит интервью для понимания фичи/бага с точки зрения пользователя. Выясняет проблему, сценарии использования, критерии готовности, edge cases. Результат — user-spec.md на русском языке для согласования с заказчиком.

### tech-spec-planning

**Создание технической спецификации.** На основе user-spec создаёт tech-spec.md с архитектурными решениями и декомпозирует на атомарные задачи (tasks/*.md). Каждая задача — non-breaking increment, готовый к реализации. Включает 3-уровневую валидацию через subagent (tech-spec, decomposition, каждый task).

### task-execution

**Выполнение задач с quality gates.** Реализует задачи из tasks/*.md через 3-фазовый TDD workflow:
- **PRE-TASK**: Валидация задачи, чтение context files (architecture, patterns, specs), review подхода
- **IMPLEMENTATION**: Тесты первые → код → запуск тестов → проверка acceptance criteria
- **POST-TASK**: Запуск тестов, опциональные reviews (code-reviewer, security-auditor), коммит, обновление статуса

Вызывается командой `/do-task` или фразой "выполни задачу".

### command-manager

**Управление slash-командами.** Создаёт, редактирует, рефакторит и удаляет команды в `~/.claude/commands/`. Проверяет зависимости перед удалением, валидирует структуру. Содержит скрипты для анализа и генерации индекса команд.

### skill-creator

**Создание новых skills.** Гайд по структуре skill (SKILL.md + bundled resources), правилам написания description для автотриггера, progressive disclosure. Содержит скрипты инициализации и упаковки skills.

---

## Commands

Slash-команды для автоматизации рутинных задач. Вызываются через `/command-name`.

### /init-project

**Инициализация нового проекта.** Копирует шаблон из `shared/templates/new-project/`, создаёт структуру `.claude/skills/project-knowledge/`, инициализирует git, создаёт GitHub репозиторий (private), регистрирует проект. Поддерживает миграцию legacy-проектов (перемещает старый код в `old/`).

### /init-context

**Заполнение технического контекста.** После планирования проекта заполняет 4-6 файлов: architecture.md, database.md, deployment.md, ux-guidelines.md. Использует Context7 для проверки актуальности tech stack. Проводит интервью с пользователем для уточнения предпочтений.

### /new-user-spec

**Создание user specification.** Обёртка над skill `user-spec-planning`. Проводит интервью, создаёт `work/{feature}/user-spec.md`. Используется когда нужно продумать фичу с бизнес-стороны перед техническим планированием.

### /new-tech-spec

**Создание технической спецификации.** Обёртка над skill `tech-spec-planning`. Читает user-spec, создаёт tech-spec.md и tasks/*.md. Используется после согласования user-spec для перехода к реализации.

### /do-task

**Выполнение задачи.** Обёртка над skill `task-execution`. Реализует одну задачу из tasks/*.md с полным TDD workflow и quality gates. Используется после создания tech-spec для пошаговой реализации фичи.

### /plan-task-waves

**Планирование параллельного выполнения.** Анализирует зависимости между задачами и группирует их в "волны" для параллельной реализации. Показывает какие задачи можно выполнять одновременно, а какие должны идти последовательно.

### /project-context

**Загрузка контекста проекта.** Читает ключевые файлы: project.md, architecture.md, git-workflow.md, deployment.md. Используется в начале сессии для быстрого погружения в проект. Указывает где искать дополнительную информацию.

### /meta-context

**Контекст для работы в ~/.claude/.** Объясняет что это мета-проект для разработки методологии, какая структура, какие файлы критичны. Предупреждает что изменения в CLAUDE.md влияют на все проекты.

---

## Agents

Специализированные субагенты, запускаемые через Task tool.

### code-developer

**Реализация задач по спецификации.** Читает task.md и context-файлы, пишет код следуя patterns.md, создаёт тесты, проверяет acceptance criteria, запускает тесты. Использует Context7 для актуальной документации. Возвращает JSON с результатами.

### code-reviewer

**Code review реализации.** Проверяет архитектуру, separation of concerns, читаемость, error handling, типизацию, тестовое покрытие, безопасность, производительность. Проверяет cross-file consistency (правильность вызовов функций между файлами). Возвращает статус: approved / approved_with_suggestions / changes_required.

### secret-scanner

**Сканирование на секреты перед коммитом.** Ищет API keys, токены, пароли, private keys, connection strings. Различает реальные секреты от placeholder'ов. Запускается автоматически перед git commit. Возвращает passed/failed с детальными findings.

### security-auditor

**Аудит безопасности по OWASP Top 10.** Проверяет SQL injection, XSS, CSRF, аутентификацию, авторизацию, криптографию, зависимости (npm audit). Запускается после code-reviewer для кода с user input, auth, database queries. Возвращает findings с severity и рекомендациями.

---

## Структура проекта

```
~/.claude/
├── skills/                 # Методологии и knowledge base
│   ├── methodology/        # AI-First разработка
│   ├── infrastructure/     # DevOps и деплой
│   ├── testing/            # Стратегии тестирования
│   ├── documentation/      # Управление документацией
│   ├── project-planning/   # Планирование проектов
│   ├── user-spec-planning/ # User specifications
│   ├── tech-spec-planning/ # Technical specifications
│   ├── task-execution/     # Выполнение задач с TDD
│   ├── command-manager/    # Создание команд
│   └── skill-creator/      # Создание skills
│
├── commands/               # Slash-команды
├── agents/                 # Субагенты
├── shared/templates/       # Шаблоны проектов
├── hooks/                  # Git/tool hooks
├── scripts/                # Утилиты
├── CLAUDE.md               # Глобальные инструкции
└── .gitignore
```

## Структура проекта после /init-project

```
my-project/
├── .claude/skills/project-knowledge/guides/
│   ├── project.md          # Описание проекта
│   ├── architecture.md     # Tech stack
│   ├── database.md         # База данных
│   ├── deployment.md       # Деплой
│   ├── patterns.md         # Паттерны кода
│   ├── git-workflow.md     # Git стратегия
│   └── ux-guidelines.md    # UI/UX
│
├── work/                   # Рабочие items
│   └── feature-name/
│       ├── user-spec.md    # Что делаем (RU)
│       ├── tech-spec.md    # Как делаем (EN)
│       └── tasks/          # Атомарные задачи
│
├── CLAUDE.md               # Инструкции для Claude
└── README.md
```

---

## Workflow

### Новый проект
1. `/init-project` — создать структуру
2. `project-planning` skill — интервью, заполнить project.md + features.md + roadmap.md
3. `/init-context` — заполнить технический контекст

### Разработка фичи
1. `/new-user-spec` — создать user specification
2. `/new-tech-spec` — создать tech spec + tasks
3. `/plan-task-waves` — (опционально) спланировать параллельное выполнение
4. `/do-task` — выполнять задачи по одной с TDD и quality gates
5. Review через `code-reviewer` + `security-auditor` (автоматически в /do-task)

---

## Лицензия

MIT License — используйте свободно.

## Автор

Pavel Molyanov — [@pavel-molyanov](https://github.com/pavel-molyanov)
