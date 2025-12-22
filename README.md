# Claude Code Framework

Фреймворк для эффективной работы с Claude Code — набор skills, commands и agents для AI-First разработки.

## Что это?

Это коллекция методологий, автоматизаций и шаблонов для работы с Claude Code CLI. Фреймворк помогает:

- Структурировать проекты по AI-First методологии
- Автоматизировать рутинные задачи (создание проектов, спецификаций, задач)
- Использовать специализированных агентов для code review, тестирования, безопасности
- Следовать best practices в разработке

## Установка

1. Скопируйте содержимое в вашу директорию `~/.claude/`:

```bash
git clone https://github.com/pavel-molyanov/claude-code-framework.git
cp -r claude-code-framework/* ~/.claude/
```

2. Или клонируйте напрямую:

```bash
git clone https://github.com/pavel-molyanov/claude-code-framework.git ~/.claude
```

## Структура

```
~/.claude/
├── skills/                 # Методологии и knowledge base
│   ├── methodology/        # AI-First разработка
│   ├── infrastructure/     # DevOps и деплой
│   ├── testing/            # Стратегии тестирования
│   ├── documentation/      # Документирование
│   ├── project-planning/   # Планирование проектов
│   ├── user-spec-planning/ # User specifications
│   ├── tech-spec-planning/ # Technical specifications
│   ├── command-manager/    # Создание команд
│   └── skill-creator/      # Создание skills
│
├── commands/               # Автоматизированные команды
│   ├── init-project.md     # Инициализация проекта
│   ├── init-context.md     # Настройка контекста
│   ├── new-user-spec.md    # Создание user spec
│   ├── new-tech-spec.md    # Создание tech spec
│   ├── plan-task-waves.md  # Декомпозиция на задачи
│   ├── start-feature-tasks.md   # Autopilot режим
│   └── start-feature-waves.md   # Parallel waves режим
│
├── agents/                 # Специализированные агенты
│   ├── code-developer.md   # Разработка по спецификации
│   ├── code-reviewer.md    # Code review
│   ├── secret-scanner.md   # Поиск секретов
│   └── security-auditor.md # Аудит безопасности
│
├── shared/                 # Шаблоны
│   ├── templates/          # Шаблоны проектов
│   └── interview-templates/# Шаблоны интервью
│
├── hooks/                  # Git/tool hooks
├── scripts/                # Утилиты
└── CLAUDE.md               # Глобальные инструкции
```

## Использование

### Команды (slash commands)

Вызывайте команды через `/command-name`:

- `/init-project` — создать новый проект с правильной структурой
- `/new-user-spec` — провести интервью и создать user specification
- `/new-tech-spec` — создать техническую спецификацию
- `/plan-task-waves` — декомпозировать спецификацию на задачи
- `/start-feature-tasks` — запустить autopilot разработку
- `/project-context` — загрузить контекст проекта

### Skills

Skills автоматически подключаются к контексту Claude Code и предоставляют методологии:

- **methodology/** — AI-First Development подход
- **infrastructure/** — Terraform, Docker, CI/CD
- **testing/** — Unit, Integration, E2E тесты
- **documentation/** — Документирование кода и API

### Agents

Агенты запускаются автоматически через Task tool:

- **code-developer** — реализует задачи по спецификации
- **code-reviewer** — проверяет качество кода
- **secret-scanner** — сканирует на утечки секретов
- **security-auditor** — OWASP аудит

## Кастомизация

### CLAUDE.md

Отредактируйте `~/.claude/CLAUDE.md` под свои предпочтения:

- Язык общения
- Правила для задач
- Политики безопасности
- Git конвенции

### Добавление skills

Создайте `.md` файл в `skills/your-skill/` с инструкциями для Claude.

### Добавление commands

Создайте `.md` файл в `commands/` со структурой slash-команды.

## Лицензия

MIT License — используйте свободно.

## Автор

Pavel Molyanov — [@pavel-molyanov](https://github.com/pavel-molyanov)
