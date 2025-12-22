---
description: Initialize project with template, git, and GitHub
allowed-tools:
  - Bash(*)
  - Read
  - Edit
  - TodoWrite
  - AskUserQuestion
---

# Instructions

## 0. Create Task Tracking

**Use TodoWrite to create plan:**

```json
[
  {"content": "Проверка окружения", "status": "pending", "activeForm": "Проверка окружения"},
  {"content": "Определение типа проекта", "status": "pending", "activeForm": "Определение типа проекта"},
  {"content": "Подготовка к перемещению (для old проектов)", "status": "pending", "activeForm": "Подготовка к перемещению"},
  {"content": "Перемещение и копирование шаблона", "status": "pending", "activeForm": "Копирование шаблона"},
  {"content": "Объединение .gitignore (для old проектов)", "status": "pending", "activeForm": "Объединение .gitignore"},
  {"content": "Регистрация проекта", "status": "pending", "activeForm": "Регистрация проекта"},
  {"content": "Инициализация git и GitHub", "status": "pending", "activeForm": "Инициализация git и GitHub"},
  {"content": "Итоговый отчёт", "status": "pending", "activeForm": "Формирование отчёта"}
]
```

Mark each step as `in_progress` when starting, `completed` when done.

## 1. Check Environment

**EXECUTE git check if .git exists:**

```bash
if [ -d .git ]; then
  git status --porcelain
fi
```

**Handle uncommitted changes:**
- If output not empty: Ask user (Russian):
  ```
  ⚠️ Незакоммиченные изменения:

  [список изменений]

  Что делать?
  1. Закоммитить и продолжить
  2. Продолжить без коммита
  3. Остановить
  ```
  Wait for user choice. If [1] - help commit first. If [3] - STOP.

- If empty or no .git: Continue.

## 2. Determine Project Type

**EXECUTE directory check:**

```bash
ls -A
```

**Analyze output:**
- Empty directory (only .git or completely empty) → **NEW PROJECT** (skip to step 4)
- Has files → **ASK USER** (Russian):
  ```
  Вижу код в папке. Что делать?

  1. Переместить в old/ (миграция старого проекта)
  2. Оставить как есть (рискованно, может перезаписать одноимённые файлы)
  3. Остановить
  ```

**Store user choice** for next steps:
- [1] → `PROJECT_TYPE=OLD`
- [2] → `PROJECT_TYPE=NEW`
- [3] → STOP

## 3. Prepare for Migration (OLD projects only)

**Skip this step if PROJECT_TYPE=NEW.**

If PROJECT_TYPE=OLD and git is initialized:

**Ask user about commit (Russian):**
```
Рекомендую закоммитить перед перемещением в old/
(это сохранит историю старого кода в git).

Закоммитить сейчас?
1. Да
2. Нет (история не сохранится)
```

**If [1] - create commit:**

```bash
git add .
git commit -m "Save old code before migration

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

**If [2] - warn user:**
```
⚠️ История старого кода не будет сохранена в git.
Продолжаем...
```

## 4. Move to old/ and Copy Template

**If PROJECT_TYPE=OLD, move files to old/:**

```bash
mkdir old

# Move everything except .git and old/
find . -maxdepth 1 ! -name '.' ! -name '..' ! -name '.git' ! -name 'old' -exec mv {} old/ \;
```

**For all project types, copy template:**

```bash
cp -r ~/.claude/shared/templates/new-project/. .
```

**Verify basic structure:**

```bash
test -d .claude/skills/project-knowledge
```

If check fails, tell user:
```
❌ Ошибка копирования шаблона.
Попробуй вручную: cp -r ~/.claude/shared/templates/new-project/. .
```

## 5. Merge .gitignore (OLD projects only)

**Skip this step if PROJECT_TYPE=NEW.**

**Read both .gitignore files:**
- Read `old/.gitignore` (old project rules)
- Current `.gitignore` is already from template

**Analyze old .gitignore:**

Parse old .gitignore and identify:
1. **Common rules** (already in new .gitignore):
   - Secrets: `.env`, `*.key`, `credentials.json`, `secrets/`
   - Dependencies: `node_modules/`, `venv/`, `__pycache__/`
   - Build outputs: `dist/`, `build/`, `.next/`, `out/`
   - IDE: `.vscode/`, `.idea/`
   - OS: `.DS_Store`
   - Logs: `*.log`, `logs/`

2. **Project-specific rules** (need to add with `old/` prefix):
   - Custom paths like `/public/uploads/`, `/storage/`
   - Config files like `config/database.php`
   - Any other unique patterns

**Create section for old-specific rules:**

Based on analysis, prepare section like:
```gitignore
# Old project specific rules
old/public/uploads/
old/storage/logs/
old/config/database.php
old/cache/
```

**Edit .gitignore:**

Add the old-specific rules section to the end of current `.gitignore`.

Save old .gitignore as backup:
```bash
cp old/.gitignore old/.gitignore.backup
```

**Security check:**

```bash
git status --porcelain
```

Check output for sensitive files that shouldn't be tracked:
- `old/.env*`
- `old/*.key`
- `old/*.pem`
- `old/credentials.json`
- `old/secrets/`

**If found sensitive files:**
- STOP immediately
- Show user the files
- Ask: "В .gitignore не все правила. Добавить эти файлы в .gitignore?"
- If yes - add rules and re-check
- If no - STOP

**If git status is clean or only expected files:**
- Continue to next step

## 6. Register Project

**Determine platform and path:**

```bash
if [[ "$HOME" == "/Users/"* ]]; then
  echo "mac"
elif [[ "$HOME" == "/home/"* ]] || [[ "$HOME" == "/root" ]]; then
  echo "vps"
else
  echo "unknown"
fi

pwd
```

Store PLATFORM and PROJECT_PATH from output.

**Read registry:**

Read `~/.claude/projects-registry.json` using Read tool.

**Check if path exists:**

Search for PROJECT_PATH in any `paths.mac` or `paths.vps` fields.

**If path found:**
- Show matching project entry
- Ask (Russian): "Этот проект уже зарегистрирован. Всё верно?"
- Wait for confirmation

**If path NOT found:**
- Ask (Russian): "Перечисли названия проекта через запятую (например: MyProject, Мой Проект, my-project):"
- Get user input
- Edit `~/.claude/projects-registry.json`:
  - Add new object to `projects` array
  - Set `names` to array from user input (split by comma)
  - Set `paths.mac` or `paths.vps` (based on PLATFORM) to PROJECT_PATH
  - Set other platform path to empty string
  - Set `github` to empty string
- Tell user (Russian): "Проект зарегистрирован! Проверь файл: [projects-registry.json](~/.claude/projects-registry.json)"

## 7. Initialize Git and GitHub

### 7.1. Initialize Git (if needed)

```bash
if [ ! -d .git ]; then
  git init
fi

git branch --show-current
```

Store current branch name.

### 7.2. Check gh CLI

```bash
command -v gh
gh auth status
```

**Handle results:**
- If gh not installed: STOP with message: "❌ gh CLI не установлен. Установи: `brew install gh` (macOS) или `sudo apt install gh` (Linux), затем: `gh auth login`"
- If not authenticated: STOP with message: "❌ gh не аутентифицирован. Запусти: `gh auth login`"
- If both OK: Continue

### 7.3. Ask for Repository Name

Ask user (Russian):
```
Введи название GitHub репозитория (например: my-project):
```

Store repository name.

### 7.4. Create GitHub Repository

```bash
gh repo create {repository-name} --private --source=. --remote=origin
```

If command fails, tell user:
```
❌ Ошибка создания GitHub репозитория.
Проверь название (возможно, уже существует).
```

### 7.5. Initial Commit and Push

```bash
git add .

git commit -m "Initial commit with AI-First template

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push -u origin $(git branch --show-current)
```

If push fails:
```
❌ Ошибка push в GitHub.
Проверь статус: git status
```

### 7.6. Create Dev Branch

```bash
git checkout -b dev
git push -u origin dev
```

### 7.7. Create Migration Branch (OLD projects only)

**Skip if PROJECT_TYPE=NEW.**

```bash
git checkout -b feature/migration-ai-first dev
git push -u origin feature/migration-ai-first
```

## 8. Final Report

**Get repository URL:**

```bash
gh repo view --json url -q .url
```

**For NEW projects, report (Russian):**

```
✅ Проект инициализирован!

GitHub: {url}
Ветки: main, dev (текущая)

Что создано:
  .claude/          - контекст и настройки проекта
  guides/           - документация
  work/             - папка для фич и задач
  .gitignore        - правила игнорирования
  CLAUDE.md         - настройки для Claude Code

Следующий шаг:
- Запусти project-planning skill для планирования проекта
```

**For OLD projects, report (Russian):**

```
✅ Проект инициализирован с миграцией!

GitHub: {url}
Ветки: main, dev, feature/migration-ai-first (текущая)
Old код: ./old/

.gitignore:
- Базовые правила (секреты, зависимости, build outputs)
- Специфичные правила из старого проекта (с префиксом old/)

Проверь git status - всё ОК с .gitignore?

Следующий шаг:
- Запусти /old-folder-audit для анализа legacy кода
- Затем /fill-context-from-audit для заполнения контекста
```

# Important Notes

- This command handles both NEW and OLD projects in one workflow
- For OLD projects: preserves history with optional commit, merges .gitignore rules
- Simplified checks: LLM understands context without excessive validation
- Git and GitHub initialization in one flow
- All user communication in Russian
- Technical content (code, docs) in English
