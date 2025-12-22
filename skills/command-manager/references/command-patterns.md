# Command Patterns - Examples and Best Practices

This document provides examples of well-structured commands demonstrating various patterns and best practices.

---

## Pattern 1: Simple Single-Step Command

**Use when:** Command performs a single operation with no validation or complex logic.

### Example: Loading Project Context

```markdown
---
description: Load key project context files
allowed-tools:
  - Read
---

# Instructions

Read and study the following project context files:
- `.claude/skills/project-knowledge/guides/project.md`
- `.claude/skills/project-knowledge/guides/architecture.md`
- `.claude/skills/project-knowledge/guides/git-workflow.md`
- `.claude/skills/project-knowledge/guides/deployment.md`

If you need more information during the session, you can find it in:
- `.claude/skills/project-knowledge/guides/patterns.md` - for code design
- `.claude/skills/project-knowledge/guides/ux-guidelines.md` - for UI/UX work
- `.claude/skills/project-knowledge/guides/database.md` - for database work
```

### Pattern Characteristics

**✅ Good:**
- Clear frontmatter with minimal tools (only `Read`)
- Single, straightforward operation
- No TodoWrite needed (single step)
- Direct imperative instructions
- Helpful additional context

**When to use:**
- Reading configuration
- Loading context
- Simple queries
- Single file operations

---

## Pattern 2: Multi-Step Command with TodoWrite

**Use when:** Command has >1 step and requires progress tracking.

### Example: Creating a Command

```markdown
---
description: Create new slash command following best practices
allowed-tools:
  - Read
  - Write
  - AskUserQuestion
  - TodoWrite
---

# Instructions

## 0. Create task tracking

**Use TodoWrite to create plan:**

```json
[
  {"content": "Read command creation rules", "status": "pending", "activeForm": "Reading rules"},
  {"content": "Ask user about command", "status": "pending", "activeForm": "Interviewing user"},
  {"content": "Create command file", "status": "pending", "activeForm": "Creating command"},
  {"content": "Validate command по чек-листу", "status": "pending", "activeForm": "Validating command"},
  {"content": "Согласовать с пользователем", "status": "pending", "activeForm": "Согласование с пользователем"},
  {"content": "Report completion", "status": "pending", "activeForm": "Reporting"}
]
```

Mark each step as `in_progress` when starting, `completed` when done.

## 1. Read command creation rules

- Read `references/command-creation-rules.md`
- Understand all requirements

## 2. Ask user about command

- What command to create?
- What should it do?
- What edge cases to consider?

## 3. Create command file

- Follow ALL rules from `references/command-creation-rules.md`
- If you need to break any rule, discuss with user first
- Save to `commands/{command-name}.md`

## 4. Validate command

**Mark todo as in_progress.**

Check command against Validation Checklist from `references/command-creation-rules.md`.

**If any issues found:**
- Fix them immediately
- Re-check against checklist

**Mark todo as completed.**

## 5. Get user approval

Show user created files, ask confirmation.

## 6. Report to user (Russian)

```
✅ Команда /{name} создана

Протестируй её на реальном проекте перед использованием!
```
```

### Pattern Characteristics

**✅ Good:**
- TodoWrite at step 0 (in Russian!)
- All major steps represented in TodoWrite
- Clear step-by-step workflow
- User interaction points defined
- Validation step included
- Russian output for user

**Key Elements:**
1. **Step 0**: Create TodoWrite with ALL steps
2. **Each step**: Clear instructions with imperative verbs
3. **Validation**: Explicit validation step
4. **User approval**: Get confirmation before finalizing
5. **Reporting**: User-facing output in Russian

---

## Pattern 3: Command with Git Operations

**Use when:** Command modifies files and needs git safety checks.

### Example: Git Repository Initialization

```markdown
---
description: Initialize git repository and create GitHub remote
allowed-tools:
  - Bash(git *)
  - Bash(gh *)
  - TodoWrite
  - AskUserQuestion
---

# Instructions

## 0. Create Task Tracking

**Use TodoWrite to create plan:**

```json
[
  {"content": "Проверить что git не инициализирован", "status": "pending", "activeForm": "Проверка git"},
  {"content": "Инициализировать локальный git", "status": "pending", "activeForm": "Инициализация git"},
  {"content": "Спросить имя репозитория", "status": "pending", "activeForm": "Вопрос об имени репозитория"},
  {"content": "Создать приватный GitHub репозиторий", "status": "pending", "activeForm": "Создание GitHub repo"},
  {"content": "Сделать initial commit и push в main", "status": "pending", "activeForm": "Коммит и push в main"},
  {"content": "Создать и запушить dev ветку", "status": "pending", "activeForm": "Создание dev ветки"},
  {"content": "Вывести статус", "status": "pending", "activeForm": "Вывод статуса"}
]
```

## 1. Check if Git Already Initialized

**EXECUTE this check:**

```bash
test -d .git && echo "GIT_EXISTS" || echo "NO_GIT"
```

**Handle result:**
- If `GIT_EXISTS`: Show status, STOP with message
- If `NO_GIT`: Continue to step 2

## 2. Initialize Local Git

**EXECUTE git initialization:**

```bash
git init && test -d .git && echo "INIT_SUCCESS" || echo "INIT_FAILED"
```

**Handle result:**
- If `INIT_FAILED`: STOP with error message
- If `INIT_SUCCESS`: Continue

## 3. Ask for Repository Name

**Ask user (Russian):**

```
Введи название GitHub репозитория (например: my-project):
```

Store the name for next step.

## 4. Create GitHub Repository

**Check gh CLI availability:**

```bash
command -v gh &> /dev/null && echo "GH_INSTALLED" || echo "GH_NOT_INSTALLED"
gh auth status &> /dev/null && echo "GH_AUTHENTICATED" || echo "GH_NOT_AUTHENTICATED"
```

**Handle results:**
- If `GH_NOT_INSTALLED`: STOP with installation instructions
- If `GH_NOT_AUTHENTICATED`: STOP with auth instructions
- If both OK: Continue

**Create private repository:**

```bash
gh repo create {name} --private --source=. --remote=origin && echo "REPO_CREATED" || echo "REPO_FAILED"
```

**Validate:**
- If `REPO_FAILED`: STOP with error
- If `REPO_CREATED`: Continue

## 5. Make Initial Commit and Push

**Add and commit files:**

```bash
git add .
test -z "$(git status --porcelain)" && echo "NO_FILES" || echo "HAS_FILES"
```

**If HAS_FILES, create commit:**

```bash
git commit -m "Initial commit

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>" && echo "COMMITTED" || echo "COMMIT_FAILED"
```

**Push to GitHub:**

```bash
BRANCH=$(git branch --show-current)
git push -u origin "$BRANCH" && echo "PUSH_SUCCESS" || echo "PUSH_FAILED"
```

**Validate push:**
- If `PUSH_FAILED`: STOP with error
- If `PUSH_SUCCESS`: Continue

## 6. Report Status

**Get repository info:**

```bash
gh repo view --json url -q .url 2>/dev/null
```

**Report (Russian):**

```
✅ Git repository initialized and pushed to GitHub!

Repository: [URL]
Branches: main (protected), dev (current)
```
```

### Pattern Characteristics

**✅ Excellent:**
- **Early git check**: Prevents re-initialization
- **Validation after each critical step**: `&& echo "SUCCESS" || echo "FAILED"`
- **Error handling**: STOP with clear messages
- **Tool prerequisites**: Checks `gh` installed and authenticated
- **User interaction**: Asks for repository name
- **Detailed TodoWrite**: Every major step tracked
- **Success validation**: Verifies operations succeeded

**Key Safety Patterns:**

1. **Check Before Action:**
```bash
test -d .git && echo "EXISTS" || echo "NOT_EXISTS"
# Check first, act second
```

2. **Validate After Action:**
```bash
command && echo "SUCCESS" || echo "FAILED"
# Always check result
```

3. **Stop on Error:**
```markdown
**If FAILED:** STOP with message: "❌ Error description"
```

4. **Check Prerequisites:**
```bash
command -v tool &> /dev/null && echo "INSTALLED" || echo "MISSING"
```

---

## Pattern 4: Command with Validation Checks

**Use when:** Critical operations that must not fail silently.

### Validation After File Creation

```markdown
## 2. Create configuration file

**EXECUTE:**

```bash
cat > config.json <<'EOF'
{
  "name": "my-app",
  "version": "1.0.0"
}
EOF
```

**VERIFY file created:**

```bash
if [ ! -f config.json ]; then
  echo "❌ ERROR: config.json not created"
  exit 1
fi
```

**VERIFY content is valid JSON:**

```bash
if ! cat config.json | python3 -m json.tool > /dev/null 2>&1; then
  echo "❌ ERROR: Invalid JSON in config.json"
  exit 1
fi
```

Report: "✅ Configuration file created and validated"
```

### Pattern Characteristics

**✅ Good:**
- Creates file with heredoc
- Validates file existence
- Validates file content
- Reports success/failure
- Stops on error

---

## Pattern 5: Edge Case Handling

**Use when:** Command needs to handle common failure scenarios.

### Example: File Already Exists

```markdown
## 2. Create output directory

**CHECK if directory exists:**

```bash
test -d output && echo "DIR_EXISTS" || echo "DIR_NOT_EXISTS"
```

**Handle based on result:**

**If DIR_EXISTS:**
- ASK user: "Папка output уже существует. Что делать?"
  - [1] Удалить и пересоздать
  - [2] Использовать существующую
  - [3] Отменить операцию

**If option 1 selected:**
```bash
rm -rf output
mkdir output
```

**If option 2 selected:**
Continue with existing directory.

**If option 3 selected:**
STOP with message: "✅ Операция отменена"

**If DIR_NOT_EXISTS:**
```bash
mkdir output && echo "DIR_CREATED" || echo "DIR_FAILED"
```

**VERIFY:**
```bash
if [ ! -d output ]; then
  echo "❌ ERROR: Failed to create directory"
  exit 1
fi
```
```

### Pattern Characteristics

**✅ Excellent:**
- Checks for existing resources
- Offers user choices
- Handles all scenarios
- Validates after action
- Clear error messages

**Common Edge Cases to Handle:**

1. **File/Directory Exists:**
   - Ask user: overwrite, skip, or cancel

2. **Git Not Initialized:**
   - Check with `test -d .git`
   - Offer to initialize or stop

3. **Uncommitted Changes:**
   - Check with `git status --porcelain`
   - Ask user: commit, stash, or continue

4. **Production Branch:**
   - Check with `git branch --show-current`
   - Warn if on main/master

5. **Missing Dependencies:**
   - Check with `command -v tool`
   - Provide installation instructions

---

## Pattern 6: Bash Returns Facts, LLM Handles Logic

**Use when:** Need to separate system checks from user interaction.

### Example: Branch Detection

❌ **Bad - Bash makes decisions:**

```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ]; then
  echo "Ты на main! Переключиться на dev?"
  echo "[1] Да  [2] Нет"
  exit 1
fi
```

✅ **Good - Bash returns facts, LLM decides:**

```bash
# Bash just reports the fact
git branch --show-current
```

```markdown
# LLM interprets and communicates
**Store branch name from output.**

**If branch is "main" or "master":**
ASK user (Russian): "⚠️ Ты на ветке {branch}! Это может быть опасно для продакшена. Переключиться на dev?"

**If user confirms:**
```bash
git checkout dev
```

**If branch is other:**
Continue normally.
```

### Pattern Characteristics

**✅ Good:**
- Bash executes, returns raw output
- LLM stores and interprets result
- LLM communicates with user
- LLM makes decisions based on facts
- User-facing messages in Russian

---

## Pattern 7: zsh-Compatible Bash

**Use when:** Need to handle complex logic on macOS (zsh default).

### Example: Processing Multiple Files

❌ **Bad - Complex inline (breaks in zsh):**

```bash
RESULT=$(find . -name "*.js" | grep -v node_modules || true)
echo "$RESULT" | while read -r file; do
  echo "Processing: $file"
  # Complex processing here
done
```

✅ **Good - Use temp files:**

```bash
# Step 1: Find files and save to temp
find . -name "*.js" | grep -v node_modules > /tmp/js_files.txt || true

# Step 2: Check if any files found
if [ -s /tmp/js_files.txt ]; then
  echo "FILES_FOUND"
else
  echo "NO_FILES"
fi
```

```markdown
**If NO_FILES:**
Report: "Не найдено .js файлов"
STOP

**If FILES_FOUND:**
Continue to process files:

```bash
# Step 3: Process each file
while read -r file; do
  echo "Processing: $file"
  # Process file here
done < /tmp/js_files.txt

# Step 4: Cleanup
rm -f /tmp/js_files.txt
```
```

### Pattern Characteristics

**✅ Good:**
- Uses temp files instead of pipes with subshells
- Simple, sequential operations
- Easy to debug
- Works in both bash and zsh
- Cleans up temp files

**Safe zsh Patterns:**

1. **Temp files for complex logic:**
```bash
command > /tmp/result.txt
process_file < /tmp/result.txt
rm /tmp/result.txt
```

2. **Simple one-liners:**
```bash
git status --porcelain
find . -name "*.js"
```

3. **Basic conditionals:**
```bash
if [ -f file.txt ]; then
  echo "exists"
fi
```

---

## Pattern 8: Comprehensive Command Template

**Use this as a starting point for new commands.**

```markdown
---
description: [One sentence describing what command does]
allowed-tools:
  - [List only tools this command uses]
---

# Instructions

## 0. Create task tracking

**Use TodoWrite to create plan:**

```json
[
  {"content": "[Step 1 description in Russian]", "status": "pending", "activeForm": "[Active form in Russian]"},
  {"content": "[Step 2 description in Russian]", "status": "pending", "activeForm": "[Active form in Russian]"},
  {"content": "[Step 3 description in Russian]", "status": "pending", "activeForm": "[Active form in Russian]"}
]
```

Mark each step as `in_progress` when starting, `completed` when done.

## 1. [First Step Name]

**[If command modifies files, check git first:]**

```bash
git status --porcelain
```

**If output not empty:**
ASK user: "Есть uncommitted changes. Продолжить, закоммитить, или остановиться?"

**[Check prerequisites if needed:]**

```bash
command -v required-tool &> /dev/null && echo "TOOL_INSTALLED" || echo "TOOL_MISSING"
```

**If TOOL_MISSING:**
STOP with message: "❌ Required tool not installed. Install with: [installation command]"

**[Execute main operation:]**

```bash
your-command-here && echo "SUCCESS" || echo "FAILED"
```

**VALIDATE operation:**

```bash
if [ ! -f expected-result ]; then
  echo "❌ ERROR: Operation failed"
  exit 1
fi
```

## 2. [Second Step Name]

**[Handle edge cases:]**

```bash
test -d directory && echo "EXISTS" || echo "NOT_EXISTS"
```

**If EXISTS:**
ASK user: "Directory exists. Overwrite, skip, or cancel?"

**[Based on user choice, execute appropriate action]**

**VALIDATE:**

```bash
# Check operation succeeded
```

## 3. [Final Step - Report]

**Get final status:**

```bash
# Commands to gather final information
```

**Report to user (Russian):**

```
✅ [Success message in Russian]

[Details about what was done]
[Next steps if any]
```

**If any errors occurred:**

```
❌ [Error message in Russian]

[Explanation]
[Suggested fix]
```
```

---

## Summary: Command Quality Checklist

Use this checklist when creating or reviewing commands:

**Structure:**
- [ ] Complete frontmatter (description + specific allowed-tools)
- [ ] TodoWrite for multi-step (>1 step), in Russian
- [ ] Whole number step headings (1, 2, 3)

**Instructions:**
- [ ] Imperative language (EXECUTE, not "example")
- [ ] Clear, explicit commands (no placeholders)
- [ ] Bash returns facts, LLM handles logic

**Safety:**
- [ ] Git check before file modifications
- [ ] Edge case handling (file exists, tool missing, etc.)
- [ ] Validation after critical operations
- [ ] Error messages with clear instructions

**Compatibility:**
- [ ] zsh-compatible bash (temp files, not complex pipes)
- [ ] Prerequisites checked before use
- [ ] Tool availability validated

**User Experience:**
- [ ] Russian for user-facing output
- [ ] English for technical instructions
- [ ] Clear success/error messages
- [ ] Next steps provided

---

## Anti-Patterns to Avoid

❌ **Don't do these:**

1. **Vague instructions:**
```markdown
You can use commands similar to git status to check...
```

2. **Missing validation:**
```bash
mkdir important_dir
# No check if it worked!
```

3. **Complex bash in zsh:**
```bash
RESULT=$(cmd | while read line; do echo $line; done)
```

4. **Bash making decisions:**
```bash
if [ condition ]; then
  echo "What do you want to do? [y/n]"
fi
```

5. **Missing TodoWrite for multi-step:**
```markdown
## 1. Step one
## 2. Step two
## 3. Step three
# No TodoWrite = BAD
```

6. **Placeholders in production:**
```markdown
Run: deploy-to {your-environment}
```

7. **No edge case handling:**
```bash
rm -rf directory  # What if it doesn't exist? What if it's important?
```

8. **English user messages:**
```markdown
Report: "✅ Command completed successfully"
# MUST BE RUSSIAN!
```
