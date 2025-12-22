---
name: command-manager
description: |
  Manage ~/.claude/ slash commands: create, analyze, edit, refactor, delete.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "создай команду", "проанализируй команду", "измени команду", "переделай команду", "удали команду"

  Do NOT use for: running commands (use SlashCommand tool)
---

# Command Manager

## Overview

This skill provides comprehensive command management capabilities for the AI-First development methodology. It enables creating new slash commands following best practices, editing existing commands, refactoring commands for better quality, safely deleting commands with dependency checks, and generating command documentation.

## Core Capabilities

The skill supports five main operations:

1. **Creating Commands** - Build new slash commands with proper structure, validation, and best practices
2. **Editing Commands** - Modify existing commands while maintaining quality standards
3. **Refactoring Commands** - Analyze and improve command quality, structure, and reliability
4. **Deleting Commands** - Safely remove commands after checking for dependencies
5. **Generating Command Index** - Create up-to-date documentation of all available commands

## Creating Commands

To create a new slash command, follow this workflow:

### 1. Load Command Creation Rules

READ the complete command creation rules from `references/command-creation-rules.md` bundled with this skill. These rules define:
- Required frontmatter structure
- TodoWrite requirements for multi-step commands
- Shell compatibility requirements (zsh on macOS)
- Validation checklist
- Edge case handling

### 2. Conduct User Interview

ASK the user these essential questions:
- What should the command do?
- What is the command name? (e.g., `/deploy-app`)
- What are the expected inputs/parameters?
- What edge cases should be handled?
- Should it work with existing files or create new ones?
- Are there any git operations required?
- Should it handle secrets or sensitive data?

### 3. Plan Command Structure

Based on user requirements, CREATE a todo list using TodoWrite:

```json
[
  {"content": "Read command creation rules", "status": "pending", "activeForm": "Reading rules"},
  {"content": "Interview user about requirements", "status": "pending", "activeForm": "Interviewing user"},
  {"content": "Create command file", "status": "pending", "activeForm": "Creating command"},
  {"content": "Validate against checklist", "status": "pending", "activeForm": "Validating command"},
  {"content": "Get user approval", "status": "pending", "activeForm": "Getting approval"},
  {"content": "Report completion", "status": "pending", "activeForm": "Reporting"}
]
```

**Important:** TodoWrite items must be in Russian (user-facing).

### 4. Write Command File

CREATE the command file at `~/.claude/commands/{command-name}.md` following these requirements:

**Frontmatter (mandatory):**
```yaml
---
description: Brief description for /help output
allowed-tools:
  - Tool1
  - Tool2
---
```

**List ONLY tools that this specific command uses.** Common tools:
- `Bash(*)` - Execute bash commands
- `Read` - Read files
- `Write` - Create/write files
- `Edit` - Edit files (exact string replacement)
- `Glob` - Find files by patterns
- `Grep` - Search file contents
- `SlashCommand` - Call other commands
- `TodoWrite` - Multi-step task tracking
- `Task` - Launch specialized agents

**Command Structure:**
1. Start with git check if command modifies files
2. Use TodoWrite if >1 step (in Russian)
3. Write imperative instructions (EXECUTE, RUN, CREATE, not "example")
4. Use zsh-compatible bash (avoid complex inline constructions)
5. Add validation checks after critical steps
6. Handle edge cases explicitly
7. Separate bash (facts) from LLM (logic/communication)
8. Use whole step numbers (1, 2, 3, not 0.5, 1.5)

**Example Command Template:**
```markdown
---
description: Deploy application to staging
allowed-tools:
  - Bash(*)
  - TodoWrite
  - Read
---

# Instructions

## 0. Create task tracking

Use TodoWrite to create plan in Russian.

## 1. Check git status

EXECUTE:
```bash
git status --porcelain
```

If output not empty, ask user about uncommitted changes.

## 2. Build application

EXECUTE:
```bash
npm run build
```

Verify build succeeded:
```bash
if [ ! -d dist ]; then
  echo "❌ Build failed!"
  exit 1
fi
```

## 3. Deploy to staging

EXECUTE deployment command and validate success.

## 4. Report to user (Russian)

Report: "✅ Приложение задеплоено на staging!"
```

### 5. Validate Against Checklist

RUN `scripts/analyze_command.py` to validate the command:

```bash
python3 ~/.claude/skills/command-manager/scripts/analyze_command.py ~/.claude/commands/{command-name}.md
```

Review the validation report. Fix any issues found.

**Manual Validation Checklist:**
- [ ] Frontmatter with description and specific allowed-tools
- [ ] TodoWrite for multi-step (>1 step), in Russian
- [ ] Imperative instructions (EXECUTE, not "example")
- [ ] zsh-compatible bash (no complex inline logic)
- [ ] Edge cases discussed with user
- [ ] Validation checks after critical steps
- [ ] Bash returns facts, LLM handles communication
- [ ] Whole step numbers only
- [ ] Ready to test on real project

### 6. Get User Approval

SHOW user the created file: "Команда создана. Проверь файл: [commands/{name}.md](commands/{name}.md). Всё ок?"

WAIT for user confirmation before proceeding.

### 7. Report Completion

COMMUNICATE in Russian:
```
✅ Команда /{name} создана

Протестируй её на реальном проекте перед использованием!
```

## Editing Commands

To edit an existing command:

### 1. Read Current Command

READ the command file: `~/.claude/commands/{command-name}.md`

ANALYZE current structure, tools used, and logic flow.

### 2. Understand User's Request

ASK the user:
- What needs to be changed?
- Why is the change needed?
- Should we preserve backward compatibility?
- Are there new edge cases to handle?

### 3. Load Command Patterns

REFERENCE `references/command-patterns.md` for examples of:
- Well-structured commands
- Common patterns for similar operations
- Best practices for specific scenarios

### 4. Make Changes

EDIT the command file following command creation rules.

ENSURE changes maintain:
- Proper frontmatter
- TodoWrite if >1 step
- zsh compatibility
- Validation checks
- Edge case handling

### 5. Validate Changes

RUN validation script:
```bash
python3 ~/.claude/skills/command-manager/scripts/analyze_command.py ~/.claude/commands/{command-name}.md
```

REVIEW validation report and fix issues.

### 6. Get Approval

SHOW user changes and ask for confirmation before saving.

## Refactoring Commands

To refactor/improve an existing command:

### 1. Analyze Current Quality

RUN comprehensive analysis:
```bash
python3 ~/.claude/skills/command-manager/scripts/analyze_command.py ~/.claude/commands/{command-name}.md --detailed
```

The script checks:
- Frontmatter completeness
- TodoWrite usage (for multi-step)
- Instruction clarity (imperative vs examples)
- Shell compatibility
- Validation checks
- Error handling
- Edge case coverage

### 2. Load Validation Checklist

READ `references/validation-checklist.md` for detailed refactoring criteria.

### 3. Identify Improvements

ANALYZE the command and identify opportunities:

**Structure Improvements:**
- Missing frontmatter fields
- Incorrect tool permissions
- Missing TodoWrite for multi-step

**Instruction Clarity:**
- Vague "example" language → imperative EXECUTE
- Missing validation checks
- Unclear error handling

**Shell Compatibility:**
- Complex bash inline constructions
- Non-portable shell features
- Missing error handling (`|| true`, exit codes)

**Edge Cases:**
- Unhandled file existence
- Missing git checks
- No secret handling
- Production branch safety

### 4. Load Command Patterns

REFERENCE `references/command-patterns.md` to find:
- Better patterns for similar operations
- Examples of well-structured commands
- Reusable validation patterns

### 5. Propose Improvements

CREATE a refactoring plan with TodoWrite (in Russian):

```json
[
  {"content": "Анализ текущей команды", "status": "completed", "activeForm": "Анализирую"},
  {"content": "Улучшить структуру frontmatter", "status": "pending", "activeForm": "Улучшаю frontmatter"},
  {"content": "Добавить TodoWrite для мульти-шаговых", "status": "pending", "activeForm": "Добавляю TodoWrite"},
  {"content": "Улучшить bash-код для zsh", "status": "pending", "activeForm": "Улучшаю bash"},
  {"content": "Добавить обработку edge cases", "status": "pending", "activeForm": "Добавляю edge cases"},
  {"content": "Валидация изменений", "status": "pending", "activeForm": "Валидирую"},
  {"content": "Согласование с пользователем", "status": "pending", "activeForm": "Согласовываю"}
]
```

PRESENT improvements to user with examples:

```
Найдены возможности для улучшения команды /{name}:

1. **Структура**: Добавить TodoWrite (команда >1 шага)
2. **Bash**: Упростить конструкцию для zsh-совместимости
3. **Edge cases**: Обработать случай существующих файлов
4. **Валидация**: Добавить проверки после критических шагов

Показать детали каждого улучшения?
```

### 6. Apply Improvements

With user approval, IMPLEMENT improvements one by one.

MARK each todo as completed after applying.

### 7. Validate Refactored Command

RUN validation again:
```bash
python3 ~/.claude/skills/command-manager/scripts/analyze_command.py ~/.claude/commands/{command-name}.md
```

ENSURE all issues resolved.

### 8. Report Results

COMMUNICATE in Russian:
```
✅ Команда /{name} улучшена

Изменения:
- Добавлен TodoWrite для отслеживания
- Улучшена zsh-совместимость bash
- Добавлена обработка edge cases
- Добавлены validation checks

Протестируй команду на реальном проекте!
```

## Deleting Commands

To safely delete a command:

### 1. Check Command Dependencies

RUN dependency check script:
```bash
python3 ~/.claude/skills/command-manager/scripts/find_command_references.py {command-name}
```

The script searches for command references in:
- Other commands (SlashCommand calls)
- Documentation files (skills/*/guides/, README.md)
- Configuration files (CLAUDE.md)

### 2. Review Dependency Report

ANALYZE the report. Example output:
```
Поиск упоминаний команды /deploy-app:

Найдено в командах:
- commands/release.md:45 - вызывает /deploy-app
- commands/test-and-deploy.md:23 - использует /deploy-app

Найдено в документации:
- skills/methodology/guides/deployment.md:12 - описывает /deploy-app
```

### 3. Warn User About Dependencies

If dependencies found, WARN user:
```
⚠️ Команда /{name} используется в других местах:

**Команды:**
- /release (commands/release.md:45)
- /test-and-deploy (commands/test-and-deploy.md:23)

**Документация:**
- Deployment Guide (skills/methodology/guides/deployment.md:12)

Удалить всё равно? Это может сломать другие команды.
```

ASK for explicit confirmation.

### 4. Delete Command File

With confirmation, DELETE the command:
```bash
rm ~/.claude/commands/{command-name}.md
```

VERIFY deletion:
```bash
if [ -f ~/.claude/commands/{command-name}.md ]; then
  echo "❌ Ошибка: файл не удалён"
  exit 1
fi
```

### 5. Update Documentation

If command was documented, REMIND user to update:
```
⚠️ Не забудь обновить документацию:
- skills/methodology/guides/deployment.md:12
```

### 6. Report Completion

COMMUNICATE in Russian:
```
✅ Команда /{name} удалена

Проверь зависимые команды:
- /release
- /test-and-deploy
```

## Generating Command Index

To generate up-to-date command documentation:

### 1. Run Index Generator

EXECUTE:
```bash
python3 ~/.claude/skills/command-manager/scripts/generate_command_index.py
```

The script:
- Scans all files in `~/.claude/commands/`
- Parses frontmatter (description, allowed-tools)
- Analyzes command complexity
- Groups commands by category
- Generates markdown table

### 2. Review Generated Index

The output includes:
- Command name and description
- Allowed tools count
- Estimated complexity (simple/medium/complex)
- Optional categorization

Example output:
```markdown
# Claude Code Commands Index

Generated: 2025-11-07

## Project Initialization
| Command | Description | Tools | Complexity |
|---------|-------------|-------|------------|
| /init-project | Initialize a new project from template | 8 | Complex |
| /init-git | Initialize git repository and create GitHub remote | 4 | Medium |

## Feature Development
| Command | Description | Tools | Complexity |
|---------|-------------|-------|------------|
| /start-feature | Start feature development in autopilot mode | 6 | Complex |
| /new-feature | Create new feature with user spec | 5 | Complex |

... (more categories)
```

### 3. Use Index for Analysis

USE the generated index to:
- Find similar commands when creating new ones
- Identify redundant commands
- Understand command ecosystem
- Document available commands for users

### 4. Optional: Save Index

If user wants to save it:
```bash
python3 ~/.claude/skills/command-manager/scripts/generate_command_index.py > /tmp/command-index.md
```

SHOW user the file path.

## Resources

### references/

**command-creation-rules.md** - Complete rules for creating commands:
- Frontmatter requirements
- TodoWrite usage
- Shell compatibility (zsh)
- Validation checklist
- Edge case handling
- Best practices

**validation-checklist.md** - Detailed validation criteria:
- Frontmatter completeness check
- TodoWrite requirements for multi-step
- Instruction clarity criteria
- Shell compatibility patterns
- Edge case coverage
- Error handling standards

**command-patterns.md** - Examples of well-structured commands:
- Simple single-step commands
- Multi-step commands with TodoWrite
- Commands with git operations
- Commands with validation checks
- Commands handling edge cases
- Commands with user interviews

### scripts/

**generate_command_index.py** - Scans all commands and generates documentation:
- Parses frontmatter from all command files
- Analyzes command complexity
- Groups by categories
- Outputs markdown table

**analyze_command.py** - Validates command against checklist:
- Checks frontmatter structure
- Validates TodoWrite usage
- Analyzes instruction clarity
- Checks shell compatibility
- Identifies missing validations
- Suggests improvements

**find_command_references.py** - Finds command dependencies:
- Searches other commands for SlashCommand calls
- Scans documentation for command mentions
- Checks rules and guides
- Generates dependency report

All scripts can be executed directly:
```bash
python3 ~/.claude/skills/command-manager/scripts/{script-name}.py [args]
```
