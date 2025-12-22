# Work Items: Структура и управление

## Обзор

Папка `work/` содержит все активные фичи, баги, и рефакторинги. Каждый work item следует структуре: User Spec → Tech Spec → Tasks.

**Принцип:** Одна папка = одна фича/баг/рефакторинг со всеми specs и задачами.

---

## Структура Work Item

```
work/
├── feature-name/                # Активная фича
│   ├── user-spec.md             # Что хотим (русский)
│   ├── tech-spec.md             # Как реализовать (English)
│   └── tasks/                   # Atomic задачи
│       ├── 1.md                 # Task 1
│       ├── 2.md                 # Task 2
│       └── 3.md                 # Task 3
├── bug-fix-name/                # Активный баг
│   ├── user-spec.md
│   ├── tech-spec.md
│   └── tasks/
├── completed/                   # Архив законченных фич
│   └── auth-system/             # Пример законченной фичи
│       ├── user-spec.md
│       ├── tech-spec.md
│       └── tasks/
└── templates/                   # Шаблоны для specs/tasks
    ├── user-spec-template.md
    ├── tech-spec-template.md
    └── task-template.md
```

---

## Компоненты Work Item

### 1. user-spec.md

**Назначение:** Описание что хотим и почему (для человека).

**Язык:** Русский (user-facing документ).

**Создается:** Через `/new-feature` (интервью с пользователем).

**Содержит:**
- **Название** - Краткое название фичи/бага
- **Тип** - Feature / Bug / Refactoring / Improvement
- **Проблема** - Что не так сейчас или чего не хватает
- **Решение** - Как должно работать после реализации
- **Acceptance Criteria** - Критерии приемки (как проверить что готово)
- **Constraints** - Ограничения (time, budget, технологии)
- **Out of Scope** - Что НЕ включается (важно!)

**Пример:**
```markdown
# Интеграция платежей

## Тип
Feature

## Проблема
Пользователи не могут оплатить подписку. Теряем 80% conversion на этапе оплаты.

## Решение
Интегрировать Stripe для приема платежей по картам. Пользователь вводит карту, получает подтверждение, его аккаунт активируется.

## Acceptance Criteria
- [ ] Пользователь может оплатить через Stripe
- [ ] После оплаты аккаунт активируется автоматически
- [ ] Email подтверждение отправляется
- [ ] Работает на staging

## Constraints
- Бюджет: $500/месяц на Stripe fees
- Срок: 1 неделя
- Только карты (no PayPal, no crypto)

## Out of Scope
- Recurring subscriptions (отдельная фича)
- Refunds (отдельная фича)
- Invoices (отдельная фича)
```

---

### 2. tech-spec.md

**Назначение:** Технический план реализации (для агента).

**Язык:** English (tech doc).

**Создается:** Через `/create-tech-spec feature-name` (после утверждения User Spec).

**Содержит:**
- **Overview** - Краткий технический обзор
- **Linked User Spec** - Ссылка на user-spec.md
- **Technical Approach** - Как реализуем
- **Components to Change** - Какие файлы/компоненты затрагиваются
- **Database Changes** - Изменения schema (если есть)
- **API Changes** - Новые/измененные endpoints
- **Testing Requirements** - Integration tests / E2E tests
- **Edge Cases** - Граничные случаи
- **Dependencies** - Новые npm/pip packages
- **Security Considerations** - OWASP проверки
- **Task Breakdown Preview** - Краткий список задач

**Пример:**
```markdown
# Tech Spec: Payment Integration

## Overview
Integrate Stripe payment processing for subscription payments.

## Linked User Spec
[user-spec.md](user-spec.md)

## Technical Approach
- Backend: Express endpoint `/api/payments/create-session`
- Frontend: React component with Stripe Elements
- Database: Add `subscription` table with status field
- Webhook: Handle Stripe events for payment confirmation

## Components to Change
- `src/routes/payments.ts` (new)
- `src/services/stripe.ts` (new)
- `src/models/subscription.ts` (new)
- `src/components/PaymentForm.tsx` (new)
- `database.md` (update schema)

## Database Changes
```sql
CREATE TABLE subscriptions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  stripe_subscription_id VARCHAR(255),
  status VARCHAR(50),
  created_at TIMESTAMP
);
```

## API Changes
- `POST /api/payments/create-session` - Create Stripe checkout session
- `POST /api/webhooks/stripe` - Handle Stripe webhook events

## Testing Requirements
**Integration Tests:**
- Test create-session endpoint
- Test webhook handler
- Test subscription activation

**E2E Tests:** None (small feature)

## Task Breakdown Preview
1. Setup Stripe SDK and configuration
2. Implement backend payment session creation
3. Implement webhook handler
4. Create frontend payment form
5. Integration tests
```

---

### 3. tasks/ folder

**Назначение:** Atomic задачи для реализации фичи.

**Создается:** Через `/tech-spec-decompose feature-name` (после утверждения Tech Spec).

**Нумерация:** Локальная для каждой фичи (начинается с 1).

**Структура задачи:**
```markdown
---
status: planned | in_progress | done
type: implementation | test | documentation
---

# Task: Setup Stripe SDK

## Description
Install Stripe SDK, create configuration file, setup environment variables.

## Acceptance Criteria
- [ ] Stripe SDK installed (`npm install stripe`)
- [ ] `.env` has `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET`
- [ ] Config file `src/config/stripe.ts` created
- [ ] Environment variables loaded correctly

## Implementation Notes
- Use Stripe SDK v12+ (check Context7 for latest)
- Store keys in `.env`, never hardcode
- Add `.env` to `.gitignore` (should already be there)

## Testing
- Unit test: verify config loads from env vars
- Smoke test: create Stripe client successfully

## Dependencies
None (first task)
```

**Типы задач:**
- **implementation** - Код, функциональность
- **test** - Integration tests, E2E tests (если выделены отдельно)
- **documentation** - Обновление context files, guides

**Статусы:**
- **planned** - Не начата
- **in_progress** - В работе
- **done** - Завершена

---

## Жизненный цикл Work Item

### 1. Создание

```bash
/new-feature
```

**Что происходит:**
1. Интервью с пользователем (2-10 вопросов)
2. Агент определяет тип (feature/bug/refactoring)
3. Предлагает feature name (lowercase-with-dashes)
4. Создает `work/feature-name/user-spec.md`
5. Пользователь ревьювит и утверждает
6. Git commit

**Результат:** `work/feature-name/` с user-spec.md

---

### 2. Техническая спецификация

```bash
/create-tech-spec feature-name
```

**Что происходит:**
1. Читает user-spec и все 7 context файлов
2. Анализирует complexity
3. Использует Context7 для актуальных best practices
4. Создает детальный tech-spec.md
5. Пользователь ревьювит и утверждает
6. Git commit

**Результат:** `work/feature-name/tech-spec.md`

---

### 3. Декомпозиция на задачи

```bash
/tech-spec-decompose feature-name
```

**Что происходит:**
1. Читает tech-spec
2. Создает atomic task файлы (1.md, 2.md, ...)
3. Tasks инкрементальные и non-breaking
4. Integration/E2E tests = отдельные задачи
5. Пользователь ревьювит
6. Git commit

**Результат:** `work/feature-name/tasks/` с задачами

---

### 4. Реализация

**Single Task Mode:**
```bash
/start-task feature-name task-number
```

**Feature Autopilot Mode:**
```bash
/start-feature feature-name
```

**Что происходит:**
1. code-developer реализует задачу (код + unit tests)
2. code-reviewer проверяет качество
3. security-auditor проверяет безопасность
4. Task status: `planned → in_progress → done`
5. Git commit после каждой задачи (gitleaks pre-commit hook автоматически сканирует секреты)
6. Tech Spec обновляется (☐ → ✅)

**Результат:** Все задачи выполнены, код закоммичен

---

### 5. Тестирование и Deploy

1. **Integration tests** (если есть задача)
2. **Merge в dev** (если используется)
3. **E2E tests** (если были написаны)
4. **Manual testing** на dev
5. **Merge в main** (после утверждения)
6. **Deploy to production**

---

### 6. Закрытие и архивация

**После успешного testing и deploy:**

```bash
# Обновить статус в specs
# Agent делает автоматически
user-spec.md: status → completed
tech-spec.md: status → implemented

# Переместить в архив
mv work/feature-name work/completed/feature-name

# Git commit
git add .
git commit -m "chore: archive completed feature-name"
```

**Зачем архивировать:**
- **Чистота** - work/ содержит только активные фичи
- **История** - completed/ сохраняет specs для reference
- **Поиск** - легко найти как была реализована похожая фича

**Результат:** `work/completed/feature-name/`

---

## Naming Conventions

### Feature Names

**Правило:** lowercase-with-dashes

**Хорошо:**
- `payment-integration`
- `user-authentication`
- `dark-mode-toggle`
- `bug-fix-duplicate-emails`

**Плохо:**
- `PaymentIntegration` (CamelCase)
- `payment_integration` (snake_case)
- `payment integration` (spaces)
- `feature1` (неописательное)

### File Names

**Specs:**
- `user-spec.md` (фиксированное имя)
- `tech-spec.md` (фиксированное имя)

**Tasks:**
- `1.md`, `2.md`, `3.md` (числа, локальная нумерация)

---

## Best Practices

### Atomic Tasks
- Каждая задача = one commit
- Легко откатить конкретную задачу
- Non-breaking changes

### Incremental Progress
- Commit после каждой задачи
- Не ждем завершения всей фичи
- Можно deploy частично

### Clear Acceptance Criteria
- В User Spec: как пользователь проверит
- В Tasks: как агент проверит (unit tests)

### Proper Archiving
- Не удаляем законченные фичи
- Переносим в `work/completed/`
- Сохраняем историю и контекст

---

## Troubleshooting

### Feature name имеет spaces/CamelCase
- Переименуй папку: `mv "Payment Integration" payment-integration`
- Обнови ссылки в specs
- Git commit

### User Spec недостаточно детальный
- `/create-tech-spec` валидирует детальность
- Допиши User Spec вручную или перезапусти `/new-feature`
- Минимум: problem, solution, acceptance criteria

### Tasks слишком большие
- Перезапусти `/tech-spec-decompose` с просьбой разбить мельче
- Atomic task = 1-3 часа работы
- Можно закоммитить без breaking changes

### Task статус не обновляется
- Агент обновляет автоматически в `/start-task` и `/start-feature`
- Можно обновить вручную в frontmatter
- Git commit после изменения

### work/ folder переполнена
- Архивируй законченные фичи в `work/completed/`
- Используй `git mv` чтобы сохранить историю
- Держи в work/ только активные items

### Нужно вернуться к старой фиче
- Проверь `work/completed/`
- Specs и tasks сохранены
- Можно изучить как была реализована
