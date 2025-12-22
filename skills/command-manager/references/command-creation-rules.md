# Command Creation Rules

## Goal

Create reliable, unambiguous slash commands that execute correctly on first try without requiring agent guesswork. Commands should handle edge cases, validate operations, and provide clear user feedback.

---

## 1. Frontmatter is Mandatory

Every command MUST start with YAML frontmatter:

```yaml
---
description: Brief command description (shows in /help)
allowed-tools:
  - Bash(*)          # Execute bash commands
  - Read             # Read files
  - Write            # Create/write files
  - Edit             # Edit files (exact string replacement)
  - Glob             # Find files by patterns (**/*.js)
  - Grep             # Search file contents
  - SlashCommand     # Call other commands
  - TodoWrite        # Multi-step task tracking
  - AskUserQuestion  # Ask user for input
  - Task             # Launch specialized agents
---
```

**Important:** List ONLY the tools your specific command actually uses, not all possible tools.

**Why:**
- `description` appears in `/help` and enables automatic command invocation
- `allowed-tools` restricts what command can do (security)

**See:** https://docs.claude.com/en/docs/claude-code/slash-commands

---

## 2. TodoWrite for Multi-Step Commands

**Rule:** Commands with >1 step MUST use TodoWrite.

Include explicit TodoWrite JSON in command with ALL steps listed.

TodoWrite is visible to users, so write todos in **Russian language** (user-facing).

**See:** `todo-tracking.md` for TodoWrite format and details.

---

## 3. Git Check Before Starting

Before starting work, check for uncommitted changes. If exist, ask user: commit and continue, continue without commit, or stop.

---

## 4. Write Clear, Imperative Instructions

❌ **Don't write:**
```markdown
Use bash with glob patterns. Example approach:
```

✅ **Do write:**
```markdown
**EXECUTE this bash command:**
```

**Rules:**
- Use imperative verbs: EXECUTE, RUN, CREATE, VERIFY
- Avoid: "example", "you can", "consider", "might want to"
- Be explicit: "Run this command" not "Run similar command"

---

## 5. Shell Compatibility (macOS = zsh)

**Problem:** macOS uses zsh by default, not bash. Complex inline bash breaks.

❌ **Avoid:**
```bash
RESULT=$(cmd | grep pattern || true)
echo "$RESULT" | while read -r line; do
  echo "Line: '$line'"
done
```

✅ **Use instead:**
```bash
# Simple approach with temp file
cmd | grep pattern > /tmp/result.txt || true
while read -r line; do
  echo "Line: $line"
done < /tmp/result.txt
rm -f /tmp/result.txt
```

**Safe patterns:**
- Temp files for complex logic
- Simple one-line commands
- Standard utilities: find, cp, mv, mkdir

---

## 6. Think About Edge Cases

**Before writing command**, think about edge cases specific to your command:
- What if file/directory already exists?
- What if git not initialized?
- What if network fails?
- What if user has uncommitted changes?
- What about secrets in files?
- What if running on production branch?

**Discuss edge cases with user before implementing.**

---

## 7. Validate After Critical Steps

Add checks after important operations:

```bash
# Check operation succeeded
if [ ! -d expected_dir ]; then
  echo "❌ ERROR: Operation failed!"
  exit 1
fi
```

---

## 8. Think Before You Write

Before creating command, answer:

1. **What edge cases exist?**
2. **Where can it fail?**
3. **How to validate success?**
4. **Is bash zsh-compatible?**
5. **Need TodoWrite?** (>1 step = yes)

---

## 9. Bash Returns Facts, LLM Handles Logic

Bash commands check facts and return results. LLM interprets and communicates with user.

❌ **Don't:**
```bash
if git show-ref --quiet refs/heads/feature; then
  echo "Переключиться на ветку?"
  echo "  [1] Да [2] Нет"
  exit 1
fi
```

✅ **Do:**
```bash
git show-ref --quiet refs/heads/feature && echo "branch-exists"
```
```markdown
**If output contains "branch-exists":** Ask user if they want to switch.
```

**Why:** Separation of concerns - bash checks, LLM decides and communicates.

---

## 10. Use Whole Step Numbers Only

Steps must use whole numbers (1, 2, 3), NOT decimals (0.5, 1.5).

**Why:** Clarity and consistency.

---

## Validation Checklist

Before finalizing command:

- [ ] Frontmatter with description and specific allowed-tools
- [ ] TodoWrite for multi-step commands (>1 step), in Russian
- [ ] Clear imperative instructions (EXECUTE, not "example")
- [ ] zsh-compatible bash (no complex inline constructions)
- [ ] Edge cases discussed with user
- [ ] Validation checks after critical steps
- [ ] Bash returns facts only, LLM handles user communication
- [ ] Steps use whole numbers (not 0.5, 1.5)
- [ ] Tested on real project

---

## Documentation

- Slash commands: https://docs.claude.com/en/docs/claude-code/slash-commands
- TodoWrite: See `todo-tracking.md` in this directory
