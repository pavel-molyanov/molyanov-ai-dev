---
description: Technical Planning для нового проекта - заполнение context файлов
allowed-tools:
  - Read
  - Edit
  - Bash(git *)
  - Bash(ls *)
  - Bash(test *)
  - TodoWrite
  - AskUserQuestion
  - Grep
  - Skill
---

# Instructions

## 0. Create Task Tracking

**Use TodoWrite to create plan (Russian):**

```json
[
  {"content": "Проверить окружение", "status": "pending", "activeForm": "Проверка окружения"},
  {"content": "Спросить про незакоммиченные изменения", "status": "pending", "activeForm": "Проверка git статуса"},
  {"content": "Проверить project.md заполнен", "status": "pending", "activeForm": "Проверка project.md"},
  {"content": "Проверить что НЕТ папки old/", "status": "pending", "activeForm": "Проверка отсутствия old/"},
  {"content": "Прочитать project.md", "status": "pending", "activeForm": "Чтение project.md"},
  {"content": "Спросить пожелания и вопросы у пользователя", "status": "pending", "activeForm": "Интервью с пользователем"},
  {"content": "Сформировать и проверить tech stack через Context7", "status": "pending", "activeForm": "Формирование tech stack"},
  {"content": "Заполнить context файлы (4-6 шт)", "status": "pending", "activeForm": "Заполнение context файлов"},
  {"content": "Review с пользователем", "status": "pending", "activeForm": "Согласование с пользователем"},
  {"content": "Закоммитить изменения", "status": "pending", "activeForm": "Коммит изменений"}
]
```

Mark each step as `in_progress` when starting, `completed` when done.

---

## 0.5. Load Documentation Skill (for guidance)

**CRITICAL: Load documentation skill BEFORE filling any files.**

This provides guidance for writing high-quality, concise documentation following best practices.

**Execute:**

```
Skill(documentation)
```

**Why load this skill:**
- Provides principles for concise, project-specific documentation
- Prevents common anti-patterns:
  - ❌ Code examples in docs (code should be self-documenting)
  - ❌ Obvious content (framework basics everyone knows)
  - ❌ Bloated explanations (keep it concise)
  - ❌ Inconsistent terminology across files
- Ensures consistency between planning docs (project.md, features.md, roadmap.md) and technical docs (architecture.md, database.md, etc.)

**After skill loads:**
- You now have access to documentation quality principles
- Use these principles when filling files in Step 8
- Proceed to Step 1

---

## 1. Check Environment

**EXECUTE these checks:**

```bash
# Check 1: В проекте?
test -f CLAUDE.md && echo "HAS_CLAUDE_MD" || echo "NO_CLAUDE_MD"

# Check 2: Есть .claude/skills/project-knowledge/guides/?
test -d .claude/skills/project-knowledge/guides && echo "HAS_CONTEXT_DIR" || echo "NO_CONTEXT_DIR"

# Check 3: Есть git?
git rev-parse --git-dir 2>/dev/null && echo "HAS_GIT" || echo "NO_GIT"

# Check 4: Количество файлов совпадает с template?
TEMPLATE_COUNT=$(ls -1 ~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/*.md 2>/dev/null | wc -l)
PROJECT_COUNT=$(ls -1 .claude/skills/project-knowledge/guides/*.md 2>/dev/null | wc -l)
test "$TEMPLATE_COUNT" -eq "$PROJECT_COUNT" && echo "FILES_MATCH" || echo "FILES_MISMATCH"
```

**Handle errors:**
- If `NO_CLAUDE_MD`: STOP with message: "❌ Не в проекте. Откройте папку проекта."
- If `NO_CONTEXT_DIR` or `FILES_MISMATCH`: STOP with message: "❌ Запустите `/init-project`"
- If `NO_GIT`: STOP with message: "❌ Запустите `/init-project`"
- If all checks pass: Proceed

---

## 2. Git Check

**EXECUTE:**

```bash
git status --porcelain
```

**If uncommitted changes exist:**

Use **AskUserQuestion** (Russian):

```
Незакоммиченные изменения:

[список изменений]

Что делать?
1. Закоммитить и продолжить
2. Продолжить без коммита
3. Остановить команду
```

**Handle response:**
- Option 1: Create commit with changes, then proceed
- Option 2: Proceed without commit
- Option 3: STOP with message: "Команда остановлена. Запустите снова когда будете готовы."

---

## 3. Check project.md

**READ file:**

```bash
cat .claude/skills/project-knowledge/guides/project.md
```

**Validate:**
- ❌ File doesn't exist → STOP: "Запустите `/init-project`"
- ❌ File is template (contains `[Description]`, `[Name]`, etc.) → STOP: "Запустите `/init-project-discovery`"
- ✅ File is filled → proceed

---

## 4. Check NO old/ Folder

**EXECUTE:**

```bash
test -d old && echo "HAS_OLD" || echo "NO_OLD"
```

**Handle result:**
- ⚠️ Has old/ → STOP with message: "Эта команда для новых проектов. Используйте `/init-context-old`"
- ✅ No old/ → proceed

---

## 5. Read project documentation

**READ project.md:**

```bash
cat .claude/skills/project-knowledge/guides/project.md
```

**Check for additional planning docs:**

```bash
test -f .claude/skills/project-knowledge/guides/features.md && echo "HAS_FEATURES" || echo "NO_FEATURES"
test -f .claude/skills/project-knowledge/guides/roadmap.md && echo "HAS_ROADMAP" || echo "NO_ROADMAP"
```

**If features.md exists:** Read it to understand complete feature list and priorities
**If roadmap.md exists:** Read it to understand development phases and timeline

**Analyze from all available docs:**
- Project type
- Features (from project.md or features.md)
- Priorities (from features.md if available)
- Development phases (from roadmap.md if available)
- Target audience
- Scope

Use this information for tech stack decisions.

---

## 6. Ask User Preferences and Questions

**Use AskUserQuestion** - formulate questions adaptively based on project.

**Structure (Russian):**

```
На основе project.md я вижу что это [краткое описание проекта].

**Есть ли пожелания по:**
- Технологиям (языки, фреймворки)?
- Deployment?
- База данных?
- UI/UX (дизайн, язык интерфейса)?

**Вопросы:**
1. Где обычно размещаете проекты? (Vercel, Railway, свой сервер)
[+ 2-4 adaptive questions based on project - about data, auth, language, design]

Опишите своими словами.
```

**Formulate 3-5 questions total** in simple language for non-developer.

Record user's answer.

---

## 7. Tech Stack via Context7

**Process:**

### Formulate Initial Tech Stack

Based on:
- project.md analysis
- User's answers from Step 6

**Decide on:**
- Frontend framework
- Backend framework
- Database
- Deployment platform
- Key dependencies

**DO NOT show to user yet.**

### Verify via Context7

For each technology, check latest best practices:

```
"[technology] latest version best practices use context7"
"[framework] 2025 guide use context7"
"[platform] deployment 2025 use context7"
```

**If Context7 is unavailable:**

Use **AskUserQuestion** (Russian):

```
Context7 недоступен. Как проверить актуальность tech stack?

1. Поискать в интернете
2. Продолжить без проверки
3. Остановить команду

Выберите вариант (1/2/3):
```

**Handle response:**
- Option 1: Use **WebSearch** to research latest versions and best practices
- Option 2: Skip Context7 verification, proceed to Step 7.4 (propose tech stack to user)
- Option 3: STOP with message: "Команда остановлена. Запустите снова когда Context7 будет доступен."

### Update Stack

Based on Context7 findings, update stack if:
- Technology is deprecated
- New version has breaking changes
- Better alternative exists

### Propose to User

**Use AskUserQuestion** (Russian):

```
Предлагаю tech stack:

**Frontend:** [technology] - [WHY this choice]
**Backend:** [technology] - [WHY this choice]
**Database:** [technology] - [WHY this choice]
**Deployment:** [platform] - [WHY this choice]

Согласны или есть правки?
```

### Iterate Until Approval

If user suggests changes:
- Update stack
- Re-verify via Context7 if needed
- Show updated proposal
- Repeat until approval

---

## 8. Fill Context Files

**IMPORTANT: Follow documentation quality principles from Step 0.5 (documentation skill):**
- NO code examples (code should be self-documenting)
- NO obvious content (framework basics everyone knows)
- NO bloated explanations (keep it concise)
- ENSURE consistency with planning docs (project.md, features.md, roadmap.md)

Based on:
- Approved tech stack
- User's answers
- **project.md** (high-level project overview)
- **features.md** (complete feature list with priorities)
- **roadmap.md** (development phases and milestones)
- Context7 best practices
- **Documentation skill guidance** (loaded in Step 0.5)

**Files to ALWAYS edit (4 required):**

### architecture.md
Tech stack and project architecture.

### database.md
Database configuration and structure.

### deployment.md
Deployment setup and process.

### ux-guidelines.md
UI text and design guidelines.

**OPTIONAL files (update ONLY if relevant info exists in planning docs):**

### monitoring.md
**Update if** project.md/features.md/roadmap.md mentions:
- Monitoring requirements (metrics, alerts, dashboards)
- Observability needs (logging, tracing, APM)
- Performance tracking (SLAs, SLOs)
- Error tracking (Sentry, error reporting)
- Analytics requirements (user behavior, conversion tracking)

**If no monitoring info:** Leave minimal template as-is

### business-rules.md
**Update if** project.md/features.md/roadmap.md mentions:
- Complex domain logic (validation rules, workflows)
- Business constraints (limits, quotas, permissions)
- Calculation rules (pricing, scoring, recommendations)
- State machines (order flow, approval process)
- Data validation rules (formats, dependencies)

**If no business rules:** Leave minimal template as-is

**DO NOT TOUCH:**
- patterns.md (already well-filled in template)
- git-workflow.md (already well-filled in template)

**Use Edit tool** to replace template placeholders with real content.

**Content language:** English

---

## 9. Review with User

**Show links to files** (Russian):

```
Технический контекст заполнен (4 обязательных файла):

- [architecture.md](.claude/skills/project-knowledge/guides/architecture.md) - Tech stack и архитектура
- [database.md](.claude/skills/project-knowledge/guides/database.md) - База данных
- [deployment.md](.claude/skills/project-knowledge/guides/deployment.md) - Деплой
- [ux-guidelines.md](.claude/skills/project-knowledge/guides/ux-guidelines.md) - UI/UX guidelines

[IF monitoring.md was updated:]
Опционально обновлены:
- [monitoring.md](.claude/skills/project-knowledge/guides/monitoring.md) - Monitoring и observability

[IF business-rules.md was updated:]
- [business-rules.md](.claude/skills/project-knowledge/guides/business-rules.md) - Бизнес-правила

Посмотри, пожалуйста. Всё правильно? Есть что изменить?
```

**Use AskUserQuestion** to get feedback.

**If changes needed:**
- Use Edit tool to update files
- Show links again
- Repeat until approval

---

## 10. Commit Changes

**Use AskUserQuestion** (Russian):

```
Закоммитить изменения?
```

**If yes:**

**Add files to git:**
```bash
# Always add 4 required files
git add .claude/skills/project-knowledge/guides/architecture.md \
        .claude/skills/project-knowledge/guides/database.md \
        .claude/skills/project-knowledge/guides/deployment.md \
        .claude/skills/project-knowledge/guides/ux-guidelines.md

# If monitoring.md was updated, add it
[IF monitoring.md was updated:]
git add .claude/skills/project-knowledge/guides/monitoring.md

# If business-rules.md was updated, add it
[IF business-rules.md was updated:]
git add .claude/skills/project-knowledge/guides/business-rules.md
```

**Create commit:**
```bash
git commit -m "$(cat <<'EOF'
feat: add technical context for new project

Filled context files:
- architecture.md - tech stack and architecture
- database.md - database configuration
- deployment.md - deployment setup
- ux-guidelines.md - UI/UX guidelines
[IF monitoring.md was updated: + monitoring.md - monitoring setup]
[IF business-rules.md was updated: + business-rules.md - business rules]

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

git status
```

**Final message (Russian):**

```
✅ Технический контекст создан!

Следующий шаг: Phase 4 - Framework & DevOps Setup
```
