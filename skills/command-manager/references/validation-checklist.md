# Command Validation Checklist - Detailed Criteria

This document provides detailed validation criteria for each item in the command creation checklist. Use this as a reference when analyzing and refactoring commands.

---

## 1. Frontmatter Completeness

### Criteria

**MUST have:**
```yaml
---
description: Brief description (one sentence)
allowed-tools:
  - Tool1
  - Tool2
---
```

### Validation Steps

**Check description:**
- [ ] Present and not empty
- [ ] One clear sentence
- [ ] Describes what command does (not how)
- [ ] Shows in `/help` output
- [ ] No placeholders like "[TODO]" or "TBD"

**Check allowed-tools:**
- [ ] Present and not empty
- [ ] Lists ONLY tools this command actually uses
- [ ] No wildcards like "- *" (except `Bash(*)`)
- [ ] Valid tool names from allowed list
- [ ] No commented-out tools

### Valid Tool Names

```
Bash(*)           - Execute bash commands
Read              - Read files
Write             - Create/write files
Edit              - Edit files (exact replacement)
Glob              - Find files by patterns
Grep              - Search file contents
SlashCommand      - Call other commands
TodoWrite         - Multi-step task tracking
AskUserQuestion   - Ask user for input
Task              - Launch specialized agents
WebFetch          - Fetch web content
WebSearch         - Search the web
```

### Common Issues

❌ **Missing description:**
```yaml
---
allowed-tools:
  - Read
---
```

❌ **Overly permissive tools:**
```yaml
---
description: Deploy app
allowed-tools:
  - *  # TOO BROAD!
---
```

❌ **Unused tools listed:**
```yaml
---
description: Read config file
allowed-tools:
  - Read
  - Write    # NOT USED IN COMMAND
  - Edit     # NOT USED IN COMMAND
---
```

---

## 2. TodoWrite Usage (Multi-Step Commands)

### Criteria

Commands with **more than 1 step** MUST use TodoWrite.

### Validation Steps

**Count steps in command:**
- [ ] Count all `## N.` headings (exclude `## 0.` if present)
- [ ] If count > 1: TodoWrite required
- [ ] If count = 1: TodoWrite optional

**Check TodoWrite format:**
- [ ] JSON format with array of objects
- [ ] Each object has: `content`, `status`, `activeForm`
- [ ] `content` in Russian (user-facing)
- [ ] `activeForm` in Russian (user-facing)
- [ ] Initial status is `"pending"`
- [ ] All major steps represented

### TodoWrite Template

```json
[
  {"content": "Шаг 1 описание", "status": "pending", "activeForm": "Выполняю шаг 1"},
  {"content": "Шаг 2 описание", "status": "pending", "activeForm": "Выполняю шаг 2"},
  {"content": "Шаг 3 описание", "status": "pending", "activeForm": "Выполняю шаг 3"}
]
```

### Common Issues

❌ **Missing TodoWrite for multi-step:**
```markdown
## 1. Check git status
## 2. Build project
## 3. Deploy
## 4. Report success

# NO TodoWrite - FAIL!
```

❌ **TodoWrite in English:**
```json
[
  {"content": "Check git status", "status": "pending", "activeForm": "Checking git"}
]
# MUST BE RUSSIAN!
```

❌ **Incomplete steps:**
```markdown
## 1. Read rules
## 2. Interview user
## 3. Create command
## 4. Validate
## 5. Report

TodoWrite:
[
  {"content": "Создать команду", "status": "pending", "activeForm": "Создаю"}
]
# Missing steps 1, 2, 4, 5!
```

---

## 3. Instruction Clarity (Imperative Form)

### Criteria

Instructions MUST be imperative and explicit. Avoid examples, suggestions, or vague language.

### Validation Steps

**Check for imperative verbs:**
- [ ] Uses EXECUTE, RUN, CREATE, VERIFY, CHECK, ASK
- [ ] No "example", "you can", "consider", "might"
- [ ] No "similar to", "like this", "something like"
- [ ] Specific commands, not placeholders

### Good Examples

✅ **Imperative and explicit:**
```markdown
EXECUTE this command:
```bash
git status --porcelain
```

If output is not empty, ASK user about uncommitted changes.
```

✅ **Clear validation:**
```markdown
VERIFY that directory was created:
```bash
if [ ! -d expected_dir ]; then
  echo "❌ ERROR: Directory not created"
  exit 1
fi
```
```

### Bad Examples

❌ **Vague example language:**
```markdown
You can check git status. Example approach:
```bash
git status
```
Use similar command for your needs.
```

❌ **Placeholder commands:**
```markdown
Run something like:
```bash
your-command-here
```
```

❌ **Non-imperative:**
```markdown
It would be good to check if the file exists.
Consider running validation.
```

---

## 4. Shell Compatibility (zsh on macOS)

### Criteria

Bash code MUST work on zsh (macOS default shell). Avoid complex inline constructions that behave differently in bash vs zsh.

### Validation Steps

**Check for problematic patterns:**
- [ ] No complex `$(...)` with pipes and conditionals
- [ ] No `echo "$VAR" | while read` loops
- [ ] No bashisms (arrays with `[@]`, `[[...]]` with regex)
- [ ] No process substitution `<(command)`
- [ ] Uses temp files for complex logic

### Safe Patterns

✅ **Temp files:**
```bash
command > /tmp/result.txt || true
while read -r line; do
  echo "$line"
done < /tmp/result.txt
rm -f /tmp/result.txt
```

✅ **Simple one-liners:**
```bash
git status --porcelain
find . -name "*.js"
ls -la
```

✅ **Basic conditionals:**
```bash
if [ -f file.txt ]; then
  echo "File exists"
fi
```

### Problematic Patterns

❌ **Complex inline:**
```bash
RESULT=$(command | grep pattern || true)
echo "$RESULT" | while read -r line; do
  process "$line"
done
```

❌ **Process substitution:**
```bash
diff <(command1) <(command2)
```

❌ **Bash arrays:**
```bash
FILES=(*.js)
for file in "${FILES[@]}"; do
  echo "$file"
done
```

---

## 5. Edge Case Coverage

### Criteria

Commands MUST handle common edge cases for their domain. Edge cases should be discussed with user before implementation.

### Common Edge Cases by Domain

**File Operations:**
- [ ] File/directory already exists
- [ ] File/directory doesn't exist
- [ ] No write permissions
- [ ] Disk full

**Git Operations:**
- [ ] Git not initialized
- [ ] Uncommitted changes exist
- [ ] On production/main branch
- [ ] Merge conflicts
- [ ] Remote not configured

**Network Operations:**
- [ ] Network unavailable
- [ ] Timeout
- [ ] Authentication failure
- [ ] Rate limiting

**Build/Deploy Operations:**
- [ ] Dependencies not installed
- [ ] Build fails
- [ ] Tests fail
- [ ] Environment variables missing

**Secret Handling:**
- [ ] Secrets in files (warn before commit)
- [ ] `.env` files in git
- [ ] API keys hardcoded

### Validation Steps

**Check command includes:**
- [ ] Git status check (if modifying files)
- [ ] File existence check (if required)
- [ ] Permission check (if needed)
- [ ] Error handling for failures
- [ ] User confirmation for destructive ops

### Examples

✅ **File existence check:**
```bash
if [ -d expected_dir ]; then
  echo "⚠️ Directory already exists"
  # Ask user what to do
fi
```

✅ **Git check:**
```bash
git status --porcelain
# If not empty, ask user about uncommitted changes
```

✅ **Production branch protection:**
```bash
BRANCH=$(git branch --show-current)
if [ "$BRANCH" = "main" ] || [ "$BRANCH" = "master" ]; then
  echo "⚠️ You're on $BRANCH!"
  # Ask for confirmation
fi
```

---

## 6. Validation After Critical Steps

### Criteria

Commands MUST validate success after critical operations. Don't assume operations succeeded.

### Critical Operations Requiring Validation

**File/Directory Creation:**
```bash
mkdir new_dir

# VALIDATE:
if [ ! -d new_dir ]; then
  echo "❌ ERROR: Directory creation failed"
  exit 1
fi
```

**File Copying/Moving:**
```bash
cp source.txt dest.txt

# VALIDATE:
if [ ! -f dest.txt ]; then
  echo "❌ ERROR: File copy failed"
  exit 1
fi
```

**Build Operations:**
```bash
npm run build

# VALIDATE:
if [ ! -d dist ]; then
  echo "❌ ERROR: Build failed"
  exit 1
fi
```

**Git Operations:**
```bash
git commit -m "message"

# VALIDATE:
git log -1 --oneline
if [ $? -ne 0 ]; then
  echo "❌ ERROR: Commit failed"
  exit 1
fi
```

### Validation Patterns

✅ **Check file exists:**
```bash
if [ ! -f expected_file ]; then
  echo "❌ ERROR: File not created"
  exit 1
fi
```

✅ **Check directory exists:**
```bash
if [ ! -d expected_dir ]; then
  echo "❌ ERROR: Directory not created"
  exit 1
fi
```

✅ **Check command succeeded:**
```bash
command_that_might_fail
if [ $? -ne 0 ]; then
  echo "❌ ERROR: Command failed"
  exit 1
fi
```

✅ **Check output contains expected string:**
```bash
OUTPUT=$(command)
if ! echo "$OUTPUT" | grep -q "expected"; then
  echo "❌ ERROR: Unexpected output"
  exit 1
fi
```

---

## 7. Separation of Concerns (Bash vs LLM)

### Criteria

**Bash** returns facts (file exists, git status, command output).
**LLM** interprets facts and communicates with user.

### Validation Steps

**Check bash doesn't:**
- [ ] Output user-facing messages in Russian
- [ ] Make decisions (use LLM for logic)
- [ ] Ask questions interactively
- [ ] Print complex explanations

**Check LLM handles:**
- [ ] Interpreting bash output
- [ ] Communicating with user
- [ ] Making decisions based on facts
- [ ] Asking user questions

### Good Examples

✅ **Bash returns facts:**
```bash
# Bash checks fact
git show-ref --quiet refs/heads/feature && echo "branch-exists"
```

```markdown
# LLM interprets and communicates
**If output contains "branch-exists":**
ASK user: "Ветка feature уже существует. Переключиться на неё?"
```

✅ **Bash reports status codes:**
```bash
# Bash executes, reports result
npm run build
echo "BUILD_EXIT_CODE=$?"
```

```markdown
# LLM interprets
**If BUILD_EXIT_CODE=0:** Report success
**Otherwise:** Report build failed, show errors
```

### Bad Examples

❌ **Bash makes decisions:**
```bash
if [ -f file.txt ]; then
  echo "Файл существует. Перезаписать?"
  read -p "[y/n] " ANSWER
  if [ "$ANSWER" = "y" ]; then
    rm file.txt
  fi
fi
```

❌ **Bash outputs user messages:**
```bash
echo "✅ Команда выполнена успешно!"
echo "Теперь можно запустить тесты."
```

---

## 8. Step Numbering

### Criteria

Steps MUST use whole numbers (1, 2, 3), NOT decimals (0.5, 1.5, 2.5).

### Validation Steps

**Check all step headings:**
- [ ] Format: `## 0. ...` or `## 1. ...` etc
- [ ] Only whole numbers
- [ ] No decimals: `## 1.5. ...` ❌
- [ ] No letters: `## 1a. ...` ❌
- [ ] Sequential (1, 2, 3, not 1, 3, 5)

### Valid Examples

✅ **Correct numbering:**
```markdown
## 0. Create task tracking
## 1. Check git status
## 2. Build project
## 3. Deploy
## 4. Report success
```

### Invalid Examples

❌ **Decimal steps:**
```markdown
## 1. Step one
## 1.5. Sub-step
## 2. Step two
```

❌ **Letter sub-steps:**
```markdown
## 1. Step one
## 1a. Sub-step A
## 1b. Sub-step B
## 2. Step two
```

❌ **Non-sequential:**
```markdown
## 1. First
## 3. Third (WHERE IS 2?)
## 5. Fifth
```

---

## 9. Testing Readiness

### Criteria

Command should be ready to test on a real project. No placeholders, TODOs, or incomplete sections.

### Validation Steps

**Check for placeholders:**
- [ ] No `[TODO]`, `[TBD]`, `[FIXME]`
- [ ] No `{placeholder}` or `<placeholder>`
- [ ] No "example command here"
- [ ] No "your-value-here"

**Check completeness:**
- [ ] All steps have instructions
- [ ] All bash commands are complete
- [ ] All validation checks present
- [ ] Error messages defined

**Check documentation:**
- [ ] Edge cases documented
- [ ] User-facing output in Russian
- [ ] Technical instructions in English

### Examples

❌ **Has placeholders:**
```markdown
## 2. Deploy to environment

EXECUTE:
```bash
deploy-command {your-environment-here}
```
```

❌ **Incomplete:**
```markdown
## 3. Validate deployment

TODO: Add validation steps
```

✅ **Complete:**
```markdown
## 3. Validate deployment

EXECUTE:
```bash
curl -f https://staging.example.com/health
```

VERIFY health check succeeded:
```bash
if [ $? -ne 0 ]; then
  echo "❌ ERROR: Health check failed"
  exit 1
fi
```

Report to user: "✅ Deployment validated successfully"
```

---

## Summary Checklist

Use this quick checklist when validating any command:

- [ ] **Frontmatter:** description + specific allowed-tools
- [ ] **TodoWrite:** Used if >1 step, in Russian
- [ ] **Instructions:** Imperative (EXECUTE, not "example")
- [ ] **Shell:** zsh-compatible, no complex inline
- [ ] **Edge Cases:** Handled and documented
- [ ] **Validation:** Checks after critical steps
- [ ] **Separation:** Bash=facts, LLM=logic
- [ ] **Numbering:** Whole numbers only (1, 2, 3)
- [ ] **Testing:** No placeholders, ready to run

---

## Severity Levels

**CRITICAL (Must fix):**
- Missing frontmatter
- Wrong tools in allowed-tools
- Missing TodoWrite for multi-step
- Unsafe bash code
- No validation for critical ops

**WARNING (Should fix):**
- Unclear instructions
- Missing edge case handling
- Non-imperative language
- Bash making decisions

**INFO (Nice to have):**
- Could use better variable names
- Could add more comments
- Could improve error messages
