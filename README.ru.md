[English](README.md) | **Русский**

# AI-First Development Framework

Практическая intent-driven методология разработки с
[Claude Code](https://docs.anthropic.com/en/docs/claude-code) и
[Codex](https://github.com/openai/codex). Она объединяет пропорциональное планирование, долговечную
Project Knowledge, сфокусированные execution skills и доказательное ревью, не заставляя каждую
задачу проходить через один тяжеловесный pipeline.

Пользовательские артефакты создаются на языке пользователя. Техническая документация, код,
промпты и инструкции skills остаются на английском, чтобы проект был переносим между сессиями и
рантаймами.

## Два рантайма, один источник

Файлы Claude — редактируемый источник истины. Файлы Codex — генерируемые runtime-артефакты.

| Источник Claude | Рантайм Codex |
|---|---|
| `~/.claude/skills/**` | `~/.codex/skills/**` |
| `~/.claude/agents/*.md` | `~/.codex/agents/*.toml` |
| `~/.claude/commands/*.md`, если есть | `~/.codex/skills/source-command-*/**` |
| Проектный `CLAUDE.md` | Проектный `AGENTS.md` |
| Проектная `.claude/**` | Проектная `.codex/**` |

После изменения Claude-side источников перегенерируйте и проверьте Codex-рантайм:

```bash
~/.claude/scripts/sync-to-codex.sh --apply
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

Конвертация запускается вручную и сообщает о конфликтах, ошибках валидации и оставшихся managed
orphans вместо неоднозначного автоматического удаления runtime-файлов.

## Быстрый старт

Клонируйте репозиторий:

```bash
git clone https://github.com/pavel-molyanov/molyanov-ai-dev.git
cd molyanov-ai-dev
```

Для новой или пустой установки скопируйте нужный рантайм:

```bash
mkdir -p ~/.claude/scripts ~/.codex
cp -R skills agents ~/.claude/
cp scripts/sync-*.py scripts/sync-*.sh ~/.claude/scripts/
cp -R .codex/skills .codex/agents ~/.codex/
```

Если вы уже используете Claude Code или Codex, не перезаписывайте конфигурацию целиком. Сравните
`CLAUDE.md` и `AGENTS.md` из репозитория со своими файлами и вручную добавьте недостающие инструкции.
Обновляйте framework skills и agents выборочно, удаляйте только устаревшие пакеты фреймворка и не
трогайте личные пакеты и принадлежащую Codex папку `.codex/skills/.system`.

После этого опишите нужный результат обычным языком. Skills маршрутизируются по намерению;
slash-command wrappers не требуются.

Типичные точки входа:

- Новый репозиторий: «Инициализируй этот проект» → `project-initialization`
- Первая или обновлённая документация: «Создай Project Knowledge» → `documentation-writing`
- Фича, которую сначала нужно согласовать: «Давай продумаем эту фичу» → `user-spec-planning`
- Небольшая реализация: «Реализуй/исправь это» → соответствующий execution skill
- Только ревью: «Проверь код/вёрстку/безопасность» → соответствующий review skill

## Как работает методология

### Выбирайте минимальный подходящий путь

| Потребность | Workflow |
|---|---|
| Небольшое однозначное изменение | Сразу соответствующий execution skill |
| Фича, поведение или подход которой нужно согласовать | `user-spec-planning` → утверждение → реализация → финализация |
| Новый репозиторий | `project-initialization` → первая Project Knowledge → фича или ad-hoc работа |
| Только документация | `documentation-writing` с явно заданной границей доказательств |
| Только ревью или аудит | Соответствующий review skill или reviewer без изменения артефакта |

Один запрос может активировать несколько skills. Например, UI-фича с изменением состояния может
объединить `layout-writing` и `code-writing` в одном цикле проверки и ревью.

### Жизненный цикл запланированной фичи

1. **Планирование.** `user-spec-planning` проводит адаптивное интервью, читает нужную Project
   Knowledge, исследует код и создаёт `work/{feature}/user-spec.md` из bundled templates.
2. **Валидация.** Независимые reviewers проверяют качество, адекватность и фактические утверждения
   о кодовой базе. Каждое замечание должно содержать конкретное доказательство, нарушенное
   требование, реалистичные условия и последствия.
3. **Утверждение.** Пользователь явно утверждает user spec до начала реализации.
4. **Реализация.** Нужные execution skills выполняют согласованное изменение и запускают минимальные
   проверки, которые доказывают результат. Применимые reviewers проверяют готовую ревизию.
5. **Финализация.** `documentation-writing` обновляет только затронутую долговечную Project
   Knowledge и переносит папку фичи в `work/completed/{feature}/`.

Небольшому прямому запросу user spec не нужен. Риски и идеи, найденные во время выполнения,
показываются как предложения и не расширяют scope молча.

### Project Knowledge

Долговечные факты проекта живут в `.claude/skills/project-knowledge/`. Её `SKILL.md` служит
роутером и загружает только нужный текущей задаче контекст. В стандартном проекте могут быть:

- `project.md` — назначение, аудитория, функции и scope
- `architecture.md` — стек, структура, интеграции и границы данных
- `patterns.md` — проектные соглашения, тестирование и бизнес-правила
- `deployment.md` — окружения, доставка, эксплуатация и восстановление
- `ux-guidelines.md` — UX-язык и доменные правила, когда это отдельная полезная граница контекста

`CLAUDE.md` остаётся компактной точкой входа и не дублирует эту документацию.

## Skills

### Планирование и контекст проекта

| Skill | Назначение |
|---|---|
| `methodology` | Объясняет маршрутизацию, lifecycle, источники истины и модель ревью |
| `project-initialization` | Создаёт dual-runtime проект, сохраняет существующие файлы, настраивает hooks, Git и приватный GitHub-репозиторий |
| `documentation-writing` | Создаёт, проверяет, обновляет и финализирует Project Knowledge |
| `user-spec-planning` | Создаёт утверждённый user spec через адаптивное интервью, исследование кода и валидацию |

### Реализация

| Skill | Назначение |
|---|---|
| `code-writing` | Поведение приложения, API, состояние, валидация и сфокусированные изменения кода |
| `layout-writing` | Точная UI-реализация, адаптивность и визуальные доказательства |
| `infrastructure-setup` | Локальная среда, Docker, hooks, CI/CD, доставка, мониторинг, бэкапы и эксплуатация |
| `prompt-master` | Создание, улучшение и ревью LLM-промптов |
| `skill-master` | Создание и изменение skills и reviewer agents |

### Тестирование и ревью

| Skill | Назначение |
|---|---|
| `test-master` | Выбирает минимальную надёжную границу тестирования и проверяет качество тестов |
| `code-reviewing` | Проверяет код относительно scope, контрактов проекта и рисков качества |
| `layout-reviewing` | Проверяет визуальную точность, адаптивность и достаточность evidence |
| `security-auditor` | Проверяет изменённые security boundaries по применимым рискам OWASP |

## Agents

Agents дают свежий ограниченный контекст для исследования и скептического ревью. Reviewers только
диагностируют: они не редактируют артефакты и не решают, можно ли выпускать результат.

| Группа | Agents |
|---|---|
| Исследование и валидация user spec | `code-researcher`, `interview-completeness-checker`, `skeptic`, `userspec-quality-validator`, `userspec-adequacy-validator` |
| Ревью реализации и документации | `code-reviewer`, `layout-reviewer`, `test-reviewer`, `security-auditor`, `documentation-reviewer`, `infrastructure-reviewer`, `prompt-reviewer` |
| Ревью skills | `skill-checker`, `skill-logic-reviewer`, `skill-simplicity-reviewer` |

Claude-определения находятся в `agents/*.md`, нативные Codex-определения — в
`.codex/agents/*.toml`.

## Bundled resources skills

Ресурсы теперь находятся рядом со skill, которому принадлежат; legacy shared resource tree удалён.

- `project-initialization/assets/new-project/` — dual-runtime scaffold, Project Knowledge, hooks,
  безопасный для секретов `.gitignore`, backlog и архив work
- `user-spec-planning/assets/` и `scripts/` — шаблоны user spec, интервью, решений и
  детерминированная инициализация папки фичи
- `documentation-writing/assets/` и `references/` — интервью Project Knowledge и правила её
  структуры
- `layout-writing/scripts/` — capture, overlay и visual comparison utilities с тестами
- `infrastructure-setup/references/` — deployment, release, monitoring и alerting guidance
- `test-master/references/` — unit, integration, smoke, end-to-end и test-review guidance
- `skill-master/references/` — формы skills, интервью, контракты reviewers и output patterns

## Scripts и поддержка Codex

- `scripts/sync-to-codex.py` / `.sh` конвертируют Claude skills, agents, commands и проектные
  инструкции в runtime-артефакты Codex.
- `scripts/sync-mcp-to-codex.py` / `.sh` отдельно preview/import MCP-конфигурацию.
- `.codex/skills/` и `.codex/agents/` содержат готовый очищенный snapshot рантайма Codex.
- Codex-owned `.system` skills и локальное состояние `.codex/.sync/` намеренно исключены.

## Требования

- Claude Code CLI и/или Codex CLI
- Python 3.11+
- Bash-совместимая оболочка (macOS/Linux, WSL или Git Bash в Windows)
- Git; GitHub CLI (`gh`) для `project-initialization`
- Context7 MCP, используемый bundled project template
- Node.js для bundled layout capture и comparison scripts

## Лицензия и автор

[MIT](LICENSE) © [Павел Молянов](https://molyanov.ru)
