# Workflow 1: Новый проект

## Когда использовать
Создание нового проекта с нуля с применением AI-First методологии.

## Command Sequence
```
/init-project → /init-project-discovery → /init-context → /setup-infrastructure
```

## Результат
- ✅ Проект создан локально и на GitHub
- ✅ Структура `.claude/` и `work/` готова
- ✅ Контекст проекта заполнен (7 context файлов)
- ✅ Framework и DevOps настроены (CI/CD, pre-commit hooks, тесты)
- ✅ Готов к разработке первой фичи

---

## Фаза 1: Project Initialization

### `/init-project`
Универсальная команда для инициализации проекта:
- Определяет тип проекта (новый / миграция old кода)
- Копирует структуру из `~/.claude/shared/templates/new-project/`
- Для old проектов: перемещает код в `old/`, объединяет `.gitignore`
- Инициализирует git, создает GitHub репозиторий
- Регистрирует проект в `projects-registry.json`
- Создает ветки: `main`, `dev` (для old: `feature/migration-ai-first`)

**Результат:** Проект существует локально и на GitHub, структура готова, git настроен.

---

## Фаза 2: Product Discovery

### `/init-project-discovery`
Проводит интервью с пользователем (3-15 адаптивных вопросов в зависимости от сложности), создает и заполняет `project.md`. Пользователь ревьювит, агент итерирует до утверждения, коммитит в git.

**Вопросы:**
- Проблема, которую решаем
- Целевая аудитория
- Основная функциональность
- MVP scope
- Ограничения (бюджет, сроки, технологии)
- Метрики успеха

**Результат:** `project.md` заполнен и версионирован.

---

## Фаза 3: Technical Planning

### `/init-context`
Читает `project.md`, спрашивает технические предпочтения (tech stack, deployment, database, UI). Предлагает tech stack с обоснованием, проверяет актуальность через Context7. После утверждения заполняет 4 context файла: `architecture.md`, `database.md`, `deployment.md`, `ux-guidelines.md`. НЕ трогает `patterns.md` и `git-workflow.md` (хорошо заполнены в шаблоне). Пользователь ревьювит, коммитит.

**Результат:** 4 context файла заполнены, tech stack выбран и задокументирован.

---

## Фаза 4: Framework & DevOps Setup

### `/setup-infrastructure`
Инициализирует выбранный framework, создает folder structure (separation of concerns), настраивает security (gitleaks pre-commit hooks), создает Docker (если нужен), настраивает GitHub Actions CI/CD (tests + auto-deploy), настраивает smoke test, обновляет `deployment.md` и `git-workflow.md`, коммитит инфраструктуру.

**Результат:** Framework настроен, CI/CD работает, pre-commit hooks активны, проект готов к разработке.

---

## Next Steps

Проект готов! Переходи к разработке первой фичи → [feature-dev.md](feature-dev.md)

---

## Troubleshooting

### GitHub authentication fails
- Проверь `gh auth status`
- Если не авторизован: `gh auth login`
- Если проблема с токеном: сгенерируй новый Personal Access Token

### Context7 недоступен
- Проверь MCP server: `claude mcp list`
- Если Context7 не в списке: установи через Claude desktop settings
- Fallback: агент использует свои знания и предупреждает о knowledge cutoff

### Framework initialization fails
- Проверь версию Node.js/Python: `node -v` / `python --version`
- Обнови до LTS версии
- Очисти кэш: `npm cache clean --force` / `pip cache purge`

### Pre-commit hooks не срабатывают
- Проверь установку: `ls .git/hooks/`
- Переустанови: `rm -rf .git/hooks && git init`
- Проверь права: `chmod +x .git/hooks/pre-commit`

### CI/CD pipeline падает
- Проверь GitHub Actions secrets настроены
- Проверь `.env.example` актуален
- Проверь syntax в `.github/workflows/`

---

## Success Checklist

- [ ] GitHub репозиторий создан и доступен
- [ ] `.claude/skills/project-knowledge/guides/` полностью заполнен (7 файлов)
- [ ] `CLAUDE.md` актуален
- [ ] Framework работает локально
- [ ] CI/CD pipeline проходит (первый commit успешен)
- [ ] Pre-commit hooks работают
- [ ] `.env.example` создан (если есть секреты)
- [ ] README.md обновлен с инструкциями
