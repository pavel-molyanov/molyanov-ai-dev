# AI-First Development Framework

[English](README.md) | **Русский**

Фреймворк для AI-First разработки с [Claude Code](https://docs.anthropic.com/en/docs/claude-code) и [Codex](https://github.com/openai/codex). Единая методология, два совместимых runtime.

В основе — spec-driven pipeline: сначала детально планируем работу через интервью с пользователем и исследование кодовой базы, согласуем спецификации, и только потом пишем код. Каждый этап проверяется специализированными агентами-валидаторами. Код пишется через TDD.

Фреймворк мультиязычный: общение, интервью и спеки для пользователя — на том языке, на котором пишет пользователь, а техническая документация (tech-spec, задачи, код) — на английском.

Язык задаётся в одном месте — в файле инструкций: `~/.claude/CLAUDE.md` для Claude и `~/.codex/AGENTS.md` для Codex (или в `CLAUDE.md` / `AGENTS.md` конкретного проекта). В секции `## Language` объявите свой язык, например `This user writes in Russian.` Скиллы и агенты берут язык оттуда, поэтому даже субагенты, не видящие чат, выдают результат на вашем языке.

## Два runtime: Claude и Codex

Методология поддерживает оба агента сразу.

- **Claude — источник истины.** Редактируются файлы в `~/.claude/`, `CLAUDE.md` и `.claude/**` проектов.
- **Codex — сгенерированный runtime.** `~/.codex/`, `AGENTS.md` и `.codex/**` создаются из Claude-источников скриптом `scripts/sync-to-codex.py`. Вручную их не правят.

Команды (`/new-user-spec`, `/do-task`, `/done` и т.д.), скиллы, агенты — те же самые. Меняется только интерпретатор.

### Установка

Скопируйте файлы фреймворка в свои runtime-папки:

```bash
# Claude (источник):
mkdir -p ~/.claude
cp -r skills agents commands shared hooks ~/.claude/

# Codex (готовый снапшот):
mkdir -p ~/.codex
cp -r .codex/skills .codex/agents ~/.codex/

# Либо положить скрипт и перегенерировать Codex из своих ~/.claude/**:
mkdir -p ~/.claude/scripts
cp scripts/sync-to-codex.py scripts/sync-to-codex.sh ~/.claude/scripts/
~/.claude/scripts/sync-to-codex.sh --apply
```

### После любых правок методологии

Если вы правите `~/.claude/**` локально — перегенерируйте Codex:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # глобальные изменения
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # проектные .claude/**
```

Альтернатива без копирования скрипта: запустить из клона репозитория — `python3 scripts/sync-to-codex.py --apply`.

Собственные скиллы фреймворка делают это автоматически — каждый скилл, который правит `.claude/**`, сначала пишет Claude-side источник, а затем регенерирует Codex-рантайм. Если вы добавляете **свой** скилл, который создаёт или меняет файлы `.claude/**`, вставьте такой же блок автосинка в начало его `SKILL.md`, чтобы изменения попадали в оба рантайма:

````markdown
## Autosync to Codex

This skill edits Claude-side source of truth (`~/.claude/**` for global skills, or a project's `.claude/**`). Codex-side `~/.codex/**` / `AGENTS.md` is generated runtime. After editing those files, regenerate Codex:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # global ~/.claude/**
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # project .claude/**
```

Commit the generated `.codex/**` / `AGENTS.md` changes together with the source.
````

Если вы пользуетесь только Claude или только Codex — это можно пропустить: синк нужен лишь когда оба рантайма работают от одних источников.

## Quick Start

**Новый проект:**

`/init-project` → `/init-project-knowledge` → начинаем фичи

**Новая фича:**

`/new-user-spec` → `/new-tech-spec` → `/decompose-tech-spec` → `/do-feature` (или `/do-task`) → `/done`

**Быстрая задача без спеки:**

`/write-code`

---

## Как устроена методология

### Документация проекта — Project Knowledge

Вся документация проекта хранится не в CLAUDE.md, а в отдельном скилле **Project Knowledge** — наборе файлов в `.claude/skills/project-knowledge/references/`:

| Файл | Что внутри |
|---|---|
| `project.md` | Назначение проекта, аудитория, ключевые фичи, scope |
| `architecture.md` | Технический стек, структура проекта, зависимости, модель данных |
| `patterns.md` | Конвенции кода, git workflow, стратегия тестирования, бизнес-правила |
| `deployment.md` | Платформа, переменные окружения, CI/CD pipeline, мониторинг |
| `ux-guidelines.md` | UI-язык, тон общения, доменный глоссарий (опционально) |

CLAUDE.md остаётся минимальным — название проекта, ссылка на Project Knowledge, дефолтная ветка. Агент подгружает только те файлы из Project Knowledge, которые нужны для текущей задачи (just-in-time context), а не весь контекст целиком.

Для создания Project Knowledge в новом проекте используется скилл **`project-planning`** (команда `/init-project-knowledge`) — он проводит интервью с пользователем, заполняет все файлы Project Knowledge и создаёт бэклог проекта (features + roadmap). Для обновления документации по ходу разработки — скилл **`documentation-writing`**.

---

### Pipeline разработки фичи

Полный путь от идеи до продакшена. На каждом шаге работают автоматические валидаторы, после каждого раунда валидации делается git-коммит (можно откатиться к любому промежуточному состоянию).

#### Шаг 1. User Spec — что делаем (`/new-user-spec`)

Агент подгружает скилл **`user-spec-planning`**, читает Project Knowledge, сканирует кодовую базу и проводит с пользователем структурированное интервью в 3 цикла:

1. **Общие вопросы** — что хотим сделать, зачем, для кого
2. **С учётом кода** — агент уже изучил проект и задаёт уточняющие вопросы по интеграции, существующим паттернам, зависимостям
3. **Edge cases** — граничные случаи, ошибки, что если...

После интервью агент `interview-completeness-checker` проверяет, не осталось ли пробелов. Затем агент составляет user-spec.md — спецификацию требований на языке пользователя, понятную человеку без технического бэкграунда.

Два валидатора проверяют результат (до 3 итераций исправлений):
- **`userspec-quality-validator`** — структура документа, тестируемость acceptance criteria
- **`userspec-adequacy-validator`** — осуществимость решения, нет ли over/underengineering

Пользователь читает и утверждает спеку.

**Результат:** `work/{feature}/user-spec.md` (статус: approved)

#### Шаг 2. Tech Spec — как делаем (`/new-tech-spec`)

Агент подгружает скилл **`tech-spec-planning`**, берёт утверждённый user-spec и переводит его в техническую спецификацию: архитектура, ключевые решения, стратегия тестирования, план реализации с разбивкой на задачи.

Пишется на английском — это документ для агента, не для человека. Если вы не разбираетесь в разработке, здесь уже ничего не поймёте — и это нормально, для этого был предыдущий шаг.

На этом этапе агент исследует кодовую базу (через агента `code-researcher`), проверяет зависимости, использует Context7 MCP для получения актуальной документации внешних библиотек.

5 валидаторов работают параллельно (до 3 итераций исправлений):
- **`skeptic`** — ищет миражи: ссылки на несуществующие файлы, функции, API
- **`completeness-validator`** — двусторонняя трассировка: все ли требования из user-spec покрыты, нет ли лишнего
- **`security-auditor`** — проверка архитектурных решений по OWASP Top 10
- **`test-reviewer`** — адекватность стратегии тестирования
- **`tech-spec-validator`** — соответствие шаблону, качество задач, конфликты зависимостей

Пользователь утверждает tech-spec.

**Результат:** `work/{feature}/tech-spec.md` (статус: approved)

#### Шаг 3. Декомпозиция на задачи (`/decompose-tech-spec`)

Агент подгружает скилл **`task-decomposition`**, берёт утверждённый tech-spec и для каждой задачи из плана реализации создаёт отдельный файл. Задачи создаются параллельно агентом `task-creator`.

Каждый task-файл содержит: acceptance criteria, TDD-якорь (какие тесты писать первыми), список файлов контекста, нужные скиллы, ревьюеров, волну выполнения и зависимости от других задач.

2 валидатора проверяют результат (до 3 итераций):
- **`task-validator`** — соответствие шаблону, качество описания
- **`reality-checker`** — существуют ли указанные файлы, функции, зависимости в реальной кодовой базе

**Результат:** `work/{feature}/tasks/*.md`

#### Шаг 4. Разработка и QA

Два режима на выбор:

**`/do-task`** — одна задача за раз, ручной контроль. Агент читает task-файл, подгружает указанные скиллы (обычно `code-writing`), пишет тесты, потом код, проходит ревью. После каждого раунда ревью — коммит с исправлениями. Подходит для отладки, сложных задач, итеративной работы.

**`/do-feature`** — параллельное выполнение всех задач командой агентов. Скилл **`feature-execution`** поднимает тимлида, который создаёт команду через TeamCreate и распределяет задачи по волнам. В каждой волне задачи выполняются параллельно: один агент = одна задача. Каждый агент самостоятельно коммитит код, проходит ревью (до 3 раундов), фиксит замечания. Тимлид координирует и коммитит статусы.

Оба режима используют TDD: сначала тесты, потом код. После кода — автоматический code review и security audit.

Финальная часть разработки любой фичи — QA. Задачи на QA добавляются автоматически в конец tech-spec:
- **Pre-deploy QA** — запуск тестов, проверка acceptance criteria из user-spec и tech-spec
- **Post-deploy QA** — верификация на живом окружении через MCP-инструменты (Playwright, curl, Telegram MCP и т.д.)

Также есть **`/write-code`** — для написания кода без спецификации. Быстрая задача, баг-фикс, эксперимент. Использует скилл `code-writing` напрямую: план → тесты → код → code review + security audit. Без предварительного планирования через user-spec/tech-spec.

#### Шаг 5. Финализация (`/done`)

Закрывает фичу: читает user-spec, tech-spec и decisions.md (решения, принятые в ходе разработки), обновляет затронутые файлы Project Knowledge (architecture.md, patterns.md и т.д.), архивирует `work/{feature}/` в `work/completed/{feature}/`.

---

### Структура work-директории

```
work/{feature}/
├── user-spec.md       # Что делаем (язык пользователя, для человека)
├── tech-spec.md       # Как делаем (английский, для агента)
├── decisions.md       # Решения, принятые в ходе разработки
├── tasks/
│   ├── 1.md           # Атомарные задачи
│   ├── 2.md
│   └── 3.md
└── logs/              # Рабочие логи (интервью, исследования, ревью)
```

Завершённые фичи архивируются в `work/completed/{feature}/`.

---

## Инициализация проекта

Для нового проекта:

1. **`/init-project`** — создаёт структуру проекта из шаблона: папку `.claude/` с Project Knowledge файлами, `CLAUDE.md`, `.gitignore` с правилами для секретов и зависимостей. Инициализирует git-репозиторий, создаёт приватный GitHub-репозиторий через `gh` CLI, делает initial commit, создаёт ветки `main` и `dev`. Если в папке уже есть файлы — предложит переместить их в `old/`.

2. **`/init-project-knowledge`** — запускает скилл `project-planning`, который проводит подробное интервью о проекте и заполняет все файлы Project Knowledge (`project.md`, `architecture.md`, `patterns.md`, `deployment.md`), а также создаёт бэклог проекта с фичами и roadmap.

После этого можно начинать разработку фич через `/new-user-spec`.

---

## Создание новых skills

Фреймворк расширяется через создание новых skills в таком же стиле:

- **`skill-master`** — гайд и правила по созданию skills: структура, паттерны, типы (процедурные и информационные), шаблоны
- **`skill-tester`** — полный цикл тестирования skills: проектирование сценариев, запуск с параллельными раннерами, оценка, отчёт

---

## Справочник

### Все команды

| Команда | Что делает |
|---|---|
| `/init-project` | Создаёт структуру проекта из шаблона, инициализирует git, создаёт приватный GitHub-репозиторий, настраивает ветки (main + dev) |
| `/init-project-knowledge` | Проводит интервью о проекте, заполняет все файлы Project Knowledge и создаёт бэклог (features + roadmap) |
| `/new-user-spec` | Проводит интервью с пользователем, исследует код, создаёт спецификацию требований с валидацией (2 валидатора, до 3 итераций) |
| `/new-tech-spec` | Исследует кодовую базу, создаёт техническую спецификацию с архитектурой, решениями, стратегией тестирования и планом реализации (5 валидаторов) |
| `/decompose-tech-spec` | Разбивает tech-spec на атомарные задачи с acceptance criteria, TDD-якорями и зависимостями (2 валидатора) |
| `/do-task` | Выполняет одну задачу: TDD (тесты → код), code review, security audit. Коммит после реализации и после каждого раунда ревью |
| `/do-feature` | Создаёт команду агентов, распределяет задачи по волнам, каждый агент выполняет задачу параллельно с TDD и ревью |
| `/write-code` | Пишет код без спецификации: план → тесты → код → code review + security audit |
| `/done` | Читает спеки и decisions.md, обновляет Project Knowledge, архивирует фичу в `work/completed/` |

### Все агенты

Агенты — изолированные субпроцессы со своим контекстом. Получают задачу, делают одну работу, возвращают структурированный результат.

#### Валидаторы и создатели
| Агент | Что делает |
|---|---|
| `userspec-quality-validator` | Проверяет структуру user-spec, покрытие, тестируемость acceptance criteria |
| `userspec-adequacy-validator` | Проверяет осуществимость решения, масштаб, нет ли over/underengineering |
| `interview-completeness-checker` | Ищет пробелы в интервью для user-spec |
| `tech-spec-validator` | Проверяет структуру tech-spec, соответствие шаблону, качество задач |
| `skeptic` | Ищет миражи — ссылки на несуществующие файлы, функции, API |
| `completeness-validator` | Двусторонняя трассировка требований user-spec ↔ tech-spec, детекция over/underengineering |
| `task-creator` | Создаёт task-файлы из плана реализации tech-spec |
| `task-validator` | Проверяет соответствие task-файлов шаблону, качество описания |
| `reality-checker` | Проверяет, существуют ли указанные в задачах файлы, функции, зависимости |
| `skill-checker` | Проверяет соответствие skills стандартам skill-master |

#### Ревьюеры
| Агент | Что проверяет |
|---|---|
| `code-reviewer` | Качество кода: архитектура, читаемость, error handling, тесты |
| `code-researcher` | Исследует кодовую базу: файлы, паттерны, тесты, интеграции, риски |
| `documentation-reviewer` | Качество Project Knowledge: полнота, актуальность, отсутствие bloat |
| `test-reviewer` | Качество тестов: находит проблемы и предлагает конкретные исправления |
| `security-auditor` | Безопасность по OWASP Top 10: SQL injection, XSS, auth, криптография |
| `deploy-reviewer` | CI/CD pipeline: GitHub Actions, secrets management, конфигурация деплоя |
| `infrastructure-reviewer` | Инфраструктура: структура проекта, Docker, pre-commit hooks, .gitignore |
| `prompt-reviewer` | Качество LLM-промптов по принципам prompt-master |

#### QA
| Агент | Что делает |
|---|---|
| `pre-deploy-qa` | Запускает тесты, проверяет acceptance criteria из user-spec и tech-spec |
| `post-deploy-qa` | Верификация на живом окружении через MCP-инструменты (Playwright, curl, Telegram MCP) |

### Все skills

#### Планирование
| Skill | Назначение |
|---|---|
| `methodology` | Описание всей методологии: pipeline, структура, принципы |
| `project-planning` | Интервью о новом проекте → заполнение Project Knowledge + бэклог (features, roadmap) |
| `user-spec-planning` | Интервью с пользователем → user-spec.md с требованиями |
| `tech-spec-planning` | Исследование кода → tech-spec.md с архитектурой и планом реализации |
| `task-decomposition` | Tech-spec → атомарные task-файлы с TDD-якорями |

#### Разработка
| Skill | Назначение |
|---|---|
| `code-writing` | Процесс написания кода: план → тесты → код → ревью |
| `feature-execution` | Оркестрация фичи: тимлид создаёт команду агентов, распределяет задачи по волнам |
| `prompt-master` | Написание, улучшение и проверка промптов для LLM |

#### Качество
| Skill | Назначение |
|---|---|
| `code-reviewing` | Методология code review по 11 измерениям: архитектура, безопасность, производительность и т.д. |
| `test-master` | Стратегия тестирования: тестовая пирамида, когда unit/integration/e2e, как обеспечить качество тестов |
| `security-auditor` | Аудит безопасности по OWASP Top 10: инъекции, аутентификация, криптография |
| `pre-deploy-qa` | Приёмочное тестирование: запуск тестов, проверка acceptance criteria без живого окружения |
| `post-deploy-qa` | Верификация после деплоя на живом окружении через MCP-инструменты |

#### Инфраструктура и документация
| Skill | Назначение |
|---|---|
| `infrastructure-setup` | Настройка инфраструктуры нового проекта: фреймворк, Docker, pre-commit hooks (gitleaks), тесты |
| `deploy-pipeline` | Настройка CI/CD: GitHub Actions, деплой (Vercel, Railway, Fly.io, AWS, VPS), secrets management |
| `documentation-writing` | Управление Project Knowledge: аудит, обновление, проверка консистентности |

#### Мета
| Skill | Назначение |
|---|---|
| `skill-master` | Создание и обновление skills: структура, паттерны, правила |
| `skill-tester` | Полный цикл тестирования skills: проектирование сценариев, запуск, оценка, отчёт |

---

## Shared — шаблоны и скрипты

Папка `shared/` содержит исходные материалы, которые используются скиллами и командами:

| Папка | Что внутри |
|---|---|
| `templates/new-project/` | Шаблон нового проекта: структура `.claude/`, Project Knowledge файлы, CLAUDE.md, .gitignore. Используется командой `/init-project` |
| `templates/infrastructure/` | Шаблоны инфраструктуры (Docker, CI/CD конфиги). Используются скиллом `infrastructure-setup` |
| `work-templates/` | Шаблоны рабочих документов: `user-spec.md.template`, `tech-spec.md.template`, `task.md.template`, `decisions.md.template`, `checkpoint.yml.template`, `execution-plan.md.template`. Скиллы копируют их при создании новых спеков и задач |
| `interview-templates/` | Структуры интервью для скиллов планирования: `feature.yml` (для user-spec), `skill.yml` (для skill-tester) |
| `scripts/` | Вспомогательные скрипты: `init-feature-folder.sh` — создание work-директории для новой фичи |

---

## Hooks — автоматизация

Папка `hooks/` содержит хуки Claude Code, которые автоматически срабатывают на определённые события:

| Хук | Событие | Что делает |
|---|---|---|
| `post-compact-restore.sh` | SessionStart (compact) | Восстанавливает контекст feature-execution после компактификации: находит checkpoint, проверяет что текущая сессия — тимлид, выводит инструкции для возобновления работы |

---

## Scripts и .codex — поддержка Codex runtime

Папка `scripts/`:

| Файл | Что делает |
|---|---|
| `sync-to-codex.py` + `sync-to-codex.sh` | Генерирует Codex-совместимые скиллы/команды/агенты и `AGENTS.md` из Claude-источников. CLI поддерживает `--dry-run`, `--apply`, `--project`. |
| `sync-mcp-to-codex.py` + `sync-mcp-to-codex.sh` | Импортирует MCP-конфиги из `~/.claude/.mcp*.json` и проектов в локальный приватный Codex-конфиг (`~/.codex/mcp-imported/` и блок в `~/.codex/config.toml`). MCP-секреты в публичный репо не уходят. |

Папка `.codex/` — pre-generated snapshot Codex runtime: `skills/` (методологические скиллы плюс слэш-команды в виде скиллов `source-command-*`) и `agents/` (нативные Codex-сабагенты `*.toml`). Можно скопировать в `~/.codex/` как есть, или перегенерировать локально (см. раздел "Два runtime" выше).

Подробнее про dual-runtime — скилл `methodology`.

---

## Требования

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) и/или [Codex CLI](https://github.com/openai/codex) — фреймворк поддерживает оба runtime
- [Context7 MCP сервер](https://github.com/upstash/context7) — агент использует его для получения актуальной документации библиотек вместо того, чтобы полагаться на данные из обучения
- Python 3.10+ — нужен для `scripts/sync-to-codex.py`, если используется Codex runtime

---

## Лицензия

MIT License — используйте свободно.

## Автор

Pavel Molyanov — [molyanov.ru](https://molyanov.ru)
