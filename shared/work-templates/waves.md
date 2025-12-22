---
feature: {{FEATURE_NAME}}
status: pending
total_waves: {{TOTAL_WAVES}}
completed_waves: 0
created_at: {{DATE}}
---

# Task Execution Waves: {{FEATURE_NAME}}

**Total tasks:** {{TOTAL_TASKS}}
**Total waves:** {{TOTAL_WAVES}}

---

## Wave 1

**Status:** pending
**Tasks:** {{WAVE_1_TASKS_COUNT}}

- [ ] [Task {{TASK_NUMBER}}: {{TASK_TITLE}}](tasks/{{TASK_NUMBER}}.md)

**Dependencies:** None (foundation tasks)

---

## Wave 2

**Status:** pending
**Tasks:** {{WAVE_2_TASKS_COUNT}}

- [ ] [Task {{TASK_NUMBER}}: {{TASK_TITLE}}](tasks/{{TASK_NUMBER}}.md)
  - Depends on: Task {{DEPENDENCY_TASK_NUMBER}} from Wave 1

**Dependencies:** Requires Wave 1

---

## Dependency Analysis

{{DEPENDENCY_REASONING}}

### Key Conflicts Avoided

{{CONFLICTS_AVOIDED_LIST}}

---

## Safety Notes

✅ All tasks in same wave are 100% independent
✅ No file conflicts within waves
✅ No code dependencies within waves
✅ No test conflicts expected
✅ Maximum 3 tasks per wave for system stability
⚠️ If any task fails, others in wave continue execution
⚠️ Review this plan carefully before execution
