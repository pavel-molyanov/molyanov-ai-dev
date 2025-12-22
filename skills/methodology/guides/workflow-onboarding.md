# Workflow 2: Внедрение в существующий проект

## Когда использовать
Есть работающий проект с legacy кодом, но нет документации и структуры. Хочется применить AI-First методологию.

## Command Sequence
```
/old-project → /old-folder-audit → /init-project-discovery → /init-context-old → /setup-infrastructure-old
```

## Результат
- ✅ Legacy код сохранен в `old/` для reference
- ✅ Структура `.claude/` и `work/` развернута
- ✅ Context создан на основе анализа existing кода
- ✅ Infrastructure и DevOps настроены
- ✅ Готов к созданию задач рефакторинга

---

## Важно: Безопасность миграции

**Все работает в отдельной ветке `feature/migration-ai-first`** - production и dev не затрагиваются. Legacy код сохраняется в `old/` и версионируется в git (история не теряется).

---

## Фаза 1: Legacy Code Preservation

### `/old-project`
Создает migration branch (`feature/migration-ai-first`), переносит все файлы в папку `old/` (кроме .git, node_modules, build artifacts), запускает `/init-project` для создания новой структуры, мерджит old .gitignore rules с префиксом `old/`, проверяет безопасность (git history цела, old/ будет закоммичен), коммитит и опционально пушит.

**Результат:** Legacy код в `old/`, новая структура развернута, работаем в отдельной ветке.

---

## Фаза 2: Product Discovery

### `/init-project-discovery`
Проводит интервью с пользователем (3-15 адаптивных вопросов), создает и заполняет `project.md` на основе существующего проекта. Пользователь ревьювит, агент итерирует до утверждения, коммитит в git.

**Результат:** `project.md` заполнен и версионирован.

---

## Фаза 3: Code Analysis & Audit

### `/old-folder-audit`
Анализирует код в `old/`, создает детальный аудит-репорт `old-folder-audit.md` (текущий tech stack, code quality, security issues, outdated dependencies, рекомендации). Проверяет актуальность технологий через Context7. Пользователь ревьювит audit.

**Результат:** `old-folder-audit.md` заполнен, текущее состояние задокументировано.

---

## Фаза 4: Context Creation

### `/init-context-old`
Читает `old-folder-audit.md` и заполняет context файлы на основе existing code: `architecture.md` (as-is из audit), `database.md` (если есть БД), `deployment.md` (текущий deployment), `ux-guidelines.md` (если есть UI). НЕ трогает `patterns.md` и `git-workflow.md` (остаются шаблонными). Пользователь ревьювит, коммитит.

**Результат:** 5 context файлов заполнены (project, architecture, database, deployment, ux-guidelines).

---

## Фаза 5: Final Documentation Setup

Agent обновляет `CLAUDE.md` на основе `project.md` (краткое описание проекта, заполняет недостающие части шаблона). Коммитит.

**Результат:** `CLAUDE.md` актуален.

---

## Фаза 6: Infrastructure & DevOps

### `/setup-infrastructure-old`
НЕ инициализирует framework (уже существует в `old/`). Добавляет/обновляет Docker (если нужен), настраивает GitHub Actions CI/CD (tests + security scanning), настраивает pre-commit hooks (gitleaks), обновляет `.gitignore` (добавляет `.env`, build папки), создает `.env.example`, обновляет `deployment.md`. Коммитит infrastructure.

**Результат:** Infrastructure настроена, CI/CD работает, pre-commit hooks активны.

---

## Next Steps

Онбординг завершен! Создавай задачи рефакторинга через стандартный workflow → [feature-dev.md](feature-dev.md)

---

## Troubleshooting

### Legacy код слишком большой
- `/old-project` работает только с файлами (игнорирует node_modules, .git, build)
- Если все равно долго: сначала удали ненужные папки вручную
- Используй `.gitignore` чтобы исключить ненужное

### Git history потерялась
- **Невозможно:** `/old-project` только перемещает файлы, не трогает `.git/`
- Проверь: `git log` - все коммиты на месте
- Если паника: отмени миграцию `git reset --hard origin/main`

### old-folder-audit не запускается
- Проверь что `old/` папка существует и не пустая
- Если нет файлов: `/old-project` не был запущен
- Если ошибка Context7: audit создастся без проверки актуальности (manual review нужен)

### Migration branch нельзя удалить
- **Нормально:** Держи ее для rollback
- Если нужно удалить: смержи в main, убедись что все работает, потом `git branch -D feature/migration-ai-first`

### CI/CD падает на legacy code
- **Ожидаемо:** Legacy код может не проходить тесты
- Не блокирует: работай над рефакторингом через `/new-feature`
- Фиксь тесты постепенно в задачах рефакторинга

---

## Rollback инструкции

### Если что-то пошло не так

**До push:**
```bash
git reset --hard HEAD~1  # откат последнего коммита
```

**После push:**
```bash
git checkout main  # переключись на main
git branch -D feature/migration-ai-first  # удали migration branch
git fetch origin  # обнови remote
```

**Если смержили в main (критично):**
```bash
git revert <commit-hash>  # откат конкретного коммита
git push
```

---

## Success Checklist

- [ ] Legacy код сохранен в `old/` и не потерян
- [ ] `old-folder-audit.md` заполнен (в корне проекта)
- [ ] `.claude/skills/project-knowledge/guides/` заполнен (5 файлов: project, architecture, database, deployment, ux-guidelines)
- [ ] `patterns.md` и `git-workflow.md` остаются шаблонными
- [ ] `CLAUDE.md` актуален
- [ ] CI/CD pipeline настроен
- [ ] Pre-commit hooks работают
- [ ] `.env.example` создан (если есть env variables)
- [ ] `.gitignore` обновлен (`.env`, build папки с префиксом `old/`)
