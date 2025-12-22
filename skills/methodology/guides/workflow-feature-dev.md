# Workflow 3: Ежедневная работа

## Когда использовать
Разработка новых фич, исправление багов, рефакторинг, улучшения.

## Command Sequence
```
/new-user-spec → /new-tech-spec → /start-task или /start-feature
```

**New commands (recommended):**
- `/new-user-spec` - creates user-spec.md (optional, for complex features)
- `/new-tech-spec` - creates tech-spec.md + tasks/*.md together
- `/start-task` or `/start-feature` - implementation

**Legacy commands (still available):**
- `/new-feature` → `/create-tech-spec` → `/tech-spec-decompose` → implementation

## Универсальный процесс

Один workflow для всего: feature / bug / refactoring / improvement.

```
Идея → Интервью → User Spec → Tech Spec → Tasks → Реализация → Testing → Deploy
```

---

## Шаг 1: Создание User Spec (Опционально)

### `user-spec-planning` skill
**Когда использовать:** Сложные features где requirements unclear, требуется интервью для прояснения.

Проводит адаптивное интервью (2-10 вопросов в зависимости от сложности), автоматически определяет тип (feature/bug/refactoring), предлагает feature name (lowercase-with-dashes), читает context (project.md, architecture.md), создает `work/feature-name/user-spec.md` (русский, для человека). Пользователь ревьювит, агент итерирует до утверждения, коммитит.

**Вопросы зависят от типа:**
- **Feature:** Как должно работать? Для кого? MVP scope? Constraints?
- **Bug:** Как воспроизвести? Как часто? Expected vs actual? Критичность?
- **Refactoring:** Что проблема? Какой результат? Есть тесты?

**Результат:** User Spec создан, понятное описание задачи без технических деталей.

**Можно пропустить** если requirements ясны и можно сразу tech-spec делать.

---

## Шаг 2: Создание Tech Spec + Tasks

### `tech-spec-planning` skill
**Вход:** user-spec.md (если есть) ИЛИ аудит ИЛИ описание от пользователя

Создает работу feature folder (если нет), читает user-spec или получает описание от пользователя, читает ВСЕ 7 context файлов, задаёт уточняющие вопросы только если нужно (адаптивно, 0-5 вопросов), анализирует complexity (simple → dev branch, complex → feature branch), использует Context7 для best practices, создает `tech-spec.md` (английский) + `tasks/*.md` за один проход. Пользователь ревьювит оба, агент итерирует до утверждения, коммитит и пушит.

**Ключевое отличие от старого workflow:**
- Tech-spec и tasks создаются **вместе** (не отдельные команды)
- Одно одобрение для обоих
- Декомпозиция встроена

**Результат:** Tech Spec + Tasks созданы, готовы к реализации.

---

## Шаг 3: Выбор режима

**Два режима работы:**

### Single Task Mode: `/start-task feature-name task-number`
Выполнить одну конкретную задачу. Используй когда:
- Хочешь контроль над каждой задачей
- Задачи сложные и требуют обсуждения
- Хочешь review после каждого шага

### Feature Autopilot Mode: `/start-feature feature-name`
Выполнить все задачи фичи последовательно без пауз. Используй когда:
- Все задачи понятны и готовы
- Хочешь быстро реализовать всю фичу
- Доверяешь агенту выполнить всё

---

## Реализация

### Single Task Mode

1. Находит и валидирует задачу
2. Переключается на feature branch (если существует)
3. Обновляет task status: `planned → in_progress`
4. Запускает **code-developer** (пишет код, unit тесты, запускает тесты)
5. Обновляет task status: `in_progress → done`
6. Обновляет tech-spec (☐ → ✅)
7. Запускает параллельные проверки:
   - **code-reviewer** (качество, архитектура)
   - **security-auditor** (OWASP Top 10)
8. Если issues → code-developer фиксит, повтор проверок
9. Git commit локально
10. Спрашивает про push

**Результат:** Задача выполнена, протестирована, закоммичена.

---

### Feature Autopilot Mode

1. Находит feature, переключается на feature branch
2. Проверяет task statuses
3. Создает plan через TodoWrite для всех remaining tasks
4. **Для каждой задачи** (цикл):
   - Запускает code-developer (код + тесты)
   - Git commit после каждой задачи (gitleaks pre-commit hook сканирует секреты)
   - Обновляет task status → done
5. **После всех tasks**:
   - Запускает integration tests (если есть)
   - Запускает параллельные финальные проверки:
     - code-reviewer (вся фича)
     - security-auditor (вся фича)
   - Если critical issues → rollback к нужному коммиту, фикс, повтор
   - Обновляет context documentation
   - Финализирует tech-spec (status → implemented)
   - Git push

**Результат:** Вся фича реализована, протестирована, запушена.

---

## После реализации

### Testing & Deploy

1. **Merge в dev** (если нужен)
2. **E2E Tests** (опционально, если были написаны)
   - Agent предлагает запустить
   - User решает: запустить или пропустить
3. **Manual Testing на dev**
   - User тестирует все сценарии из User Spec
   - Проверяет edge cases
   - Тестирует на реальных данных

### Если найдены баги

- User сообщает о проблемах
- Agent обновляет `tech-spec.md`
- Agent создает новые задачи в той же фиче
- Реализует через `/start-task` или `/start-feature`
- Повтор testing

### Закрытие фичи

После успешного testing и deploy:
- Agent обновляет status в User Spec и Tech Spec: `completed`
- Git commit и push
- **Архивация:** Переместить `work/feature-name/` → `work/completed/feature-name/`
  - Держит work folder чистым (только активные фичи)
  - Сохраняет историю для reference
  - Git commit после перемещения
- Фича завершена

---

## Troubleshooting

### Команда не находит feature
- Проверь папку: `ls work/`
- Проверь имя: lowercase-with-dashes (не spaces, не CamelCase)
- Если пусто: сначала запусти `/new-feature`

### User Spec недостаточно детальный
- `/create-tech-spec` валидирует детальность
- Если недостаточно: допиши User Spec вручную или перезапусти `/new-feature`
- Минимум: описание проблемы, expected result, acceptance criteria

### Tasks слишком большие
- Перезапусти `/tech-spec-decompose` с просьбой разбить мельче
- Atomic task = можно закоммитить без breaking changes
- Хороший размер: 1-3 часа работы

### Тесты падают
- code-developer автоматически фиксит failing tests
- Если не помогает: проверь test environment (DB, env variables)
- Если test logic неправильный: обнови task description, перезапусти `/start-task`

### Code reviewer находит critical issues
- **В Single Task Mode:** code-developer фиксит, повтор review
- **В Feature Autopilot:** rollback к коммиту задачи, code-developer переделывает, повтор
- Если не согласен с reviewer: обнови patterns.md с своими правилами

### Feature branch конфликтует с main
- Перед `/start-feature`: `git pull origin main` и resolve conflicts
- Во время работы: не мерджи другие фичи в main
- После: если конфликты при merge → resolve вручную

### E2E tests не запускаются
- Проверь test environment: dev сервер доступен?
- Проверь env variables: все секреты настроены?
- Если нет E2E инфраструктуры: пропусти, используй manual testing

---

## Принципы работы

**Работаем с одной фичей/веткой за раз**
- Внутри фичи может быть несколько tasks in_progress
- Задачи из разных фич не смешиваем

**Commit после каждой задачи**
- Atomic commits: легко откатить конкретную задачу
- Сохраняем commit hash в TodoWrite для rollback

**Push после фичи**
- Single Task: push опционален после каждой задачи
- Feature Autopilot: push в конце после всех проверок

**Тесты пишем сразу**
- Unit тесты: вместе с кодом (не deferred)
- Integration тесты: отдельная задача
- E2E тесты: отдельная задача или опционально
