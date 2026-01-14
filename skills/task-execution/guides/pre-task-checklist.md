# Pre-Task Checklist

Complete these steps before writing any code.

## 1. Validate Task

```bash
# Check task exists and read it
cat work/{feature}/tasks/{N}.md
```

Verify:
- [ ] Status is `planned`
- [ ] Acceptance criteria are clear
- [ ] Edge cases are listed

## 2. Read Context Files

### Required (always read)

```
.claude/skills/project-knowledge/guides/architecture.md
.claude/skills/project-knowledge/guides/patterns.md
.claude/skills/project-knowledge/guides/project.md
work/{feature}/user-spec.md
work/{feature}/tech-spec.md
```

### From Task File

Read all files listed in task's "Context Files" section.

### Conditional

Check task content and read relevant files:
- Database/models → `database.md`
- API/routes → `api.md`
- Deployment → `deployment.md`
- UI/design → `ux-guidelines.md`
- Testing → `~/.claude/skills/testing/guides/*.md`

## 3. Review Approach

Before coding, verify:

- [ ] Solution follows patterns from `patterns.md`
- [ ] No existing code that can be reused
- [ ] Approach makes sense for the architecture
- [ ] No obvious issues or red flags

If anything seems wrong, discuss with user.

## 4. Baseline Tests (Optional)

If tests exist for the area being modified:

```bash
# Run relevant tests
npm test -- path/to/relevant/tests
# or
pytest path/to/relevant/tests
```

Note any failures - they're not our responsibility but good to know.

## Ready to Code

After completing this checklist, proceed to Phase 2: Implementation.
