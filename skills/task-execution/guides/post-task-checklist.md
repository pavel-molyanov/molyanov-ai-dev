# Post-Task Checklist

Complete these steps after implementation is done.

## 1. Run Relevant Tests

Run tests for the code that was changed:

```bash
# Run specific tests
npm test -- path/to/changed/tests
# or
pytest path/to/changed/tests -v
```

All tests must pass before proceeding.

**Note:** Do NOT run all tests after each task. Save full test suite for end of feature.

## 2. Ask User About Reviews

Use AskUserQuestion tool:

```
Задача выполнена. Прогнать через ревью?
- code-reviewer (качество кода, архитектура)
- security-auditor (безопасность, OWASP)
```

Options:
- **code-reviewer** - checks code quality, architecture patterns, error handling
- **security-auditor** - checks OWASP Top 10, input validation, auth issues

## 3. Run Selected Reviews

Launch subagents based on user choice:

```
# If code-reviewer selected
Task(subagent_type="code-reviewer", prompt="Review files: {list}")

# If security-auditor selected
Task(subagent_type="security-auditor", prompt="Audit files: {list}")
```

Run in parallel if both selected.

`secret-scanner` runs automatically via pre-commit hook.

## 4. Fix Issues

Based on review results:

| Severity | Action |
|----------|--------|
| Critical | Must fix before commit |
| High | Must fix before commit |
| Medium | Fix if time permits |
| Low | Note for future |

## 5. Git Commit

```bash
git add .
git commit -m "$(cat <<'EOF'
feat|fix|refactor: Brief description

- What changed
- Why changed

Task: work/{feature}/tasks/{N}.md

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

Pre-commit hooks will run automatically (gitleaks, secret-scanner).

## 6. Update Status

Update task file:
```yaml
---
status: done  # was: planned
---
```

Update tech-spec checkbox:
```markdown
- [x] Task N: Description  # was: - [ ]
```

## Done

Task is complete. Ready for next task or feature completion.
