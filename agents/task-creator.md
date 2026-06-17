---
name: task-creator
description: |
  Creates task files from tech-spec Implementation Tasks section.
  Reads actual code files listed in tech-spec, discovers project knowledge,
  generates tasks by updated template with TDD Anchor, reviewers, skills.

  Use when: generating task/*.md files after tech-spec is approved,
  during /decompose-tech-spec or manual task creation from tech-spec.
  Also used in fix mode: receives existing task + validator findings, applies fixes.
  Scope excludes: validating tasks (use task-validator).
model: inherit
color: green
allowed-tools: Read, Glob, Grep, Write, Bash, Edit
---

Create task file for the specified task from tech-spec.

## Input

**Required:**
- feature_path: Path to feature folder (e.g., `work/my-feature`)
- task_number: Task number (e.g., 1, 2, 3)
- task_name: Task name from tech-spec
- files_to_modify: List of code files to modify (from tech-spec's Implementation Tasks)

**Optional:**
- template_path: Path to task template (default: `~/.claude/shared/work-templates/tasks/task.md.template`)
- files_to_read: List of code files to read for context (default: [])
- depends_on: List of task dependency numbers (default: [])
- wave: Wave number for parallel execution (default: 1)
- skills: Array of skills for the task (default: [code-writing])
- reviewers: Array of reviewers (default: [code-reviewer, test-reviewer])
- verify: Array of verification types: [smoke], [user], [smoke, user], or [] (default: []). Derives from tech-spec Verify-smoke: and Verify-user: presence
- teammate_name: Cosmetic name for agent teams (default: none)

**Fix mode (optional):**
- mode: `fix` (default: `create`)
- findings: Array of validator findings — JSON objects with `severity`, `issue`, `fix`

## Process

### If mode=fix

1. Read existing task file at `{feature_path}/tasks/{task_number}.md`
2. Read same context as create mode (steps 1-3 below)
3. Review each finding — understand what's wrong and what the fix suggests
4. Apply fixes to the task while preserving everything that was correct
5. Overwrite task file. Return file path.

### If mode=create (default)

1. Read feature context:
   - {feature_path}/tech-spec.md — find this task in Implementation Tasks
   - {feature_path}/user-spec.md (if exists)
   - {feature_path}/decisions.md (if exists)

2. PK discovery — Glob `.claude/skills/project-knowledge/` to find what exists, then read SKILL.md to understand references.
   Then read:
   - **Always:** project.md, architecture.md (project context is always needed)
   - **By task relevance:** other PK references needed for this task. Examples:
     - Code task (code-writing skill) → patterns.md (Testing section)
     - DB task → architecture.md (Data Model section)
     - UI task → ux-guidelines.md
   - Rule: better to include an extra doc than miss an important one.
   - Use actual discovered paths, not hardcoded ones.

3. Read actual code files from files_to_modify and files_to_read.
   For each file: understand current state — what exists, what functions/classes are there, what needs to change or be added. Use this to write concrete "What to do" and "Details".

4. Copy template to task file:
   - `cp {template_path} {feature_path}/tasks/{task_number}.md`
   - Ensure `tasks/` directory exists first (`mkdir -p {feature_path}/tasks`)

5. Edit each section in the copied file using Edit tool. Work through sections top-to-bottom:
   - Frontmatter: replace placeholder values with actual status, depends_on, wave, skills, verify, reviewers, teammate_name
   - Title: replace `Task N: Name` with actual task number and name
   - Required Skills: replace with actual skills for this task
   - Description, What to do, TDD Anchor, Acceptance Criteria, Context Files, Verification Steps, Details, Reviewers, Post-completion: replace placeholder content with real content based on tech-spec and code analysis
   - For non-code tasks: delete TDD Anchor section entirely

## Task File Structure

### 1. Frontmatter
- status: planned
- depends_on: {from input}
- wave: {from input}
- skills: {from input, array}
- verify: {from input, array of types: [smoke], [user], [smoke, user], or []}
- reviewers: {from input, array}
- teammate_name: {from input, optional — cosmetic name for agent teams}

### 2. Required Skills
Instructions for the implementing agent — which skills to load before starting work on this task.
Duplicate frontmatter skills as explicit load instructions:
"Before starting, load: /skill:{name} — [SKILL.md](path)"

### 3. Description
What this task accomplishes and how it fits the feature. Write as much as needed for clear understanding.

### 4. What to do
Concrete steps — focus on outcomes and deliverables. Use natural language descriptions.

### 5. TDD Anchor
Tests to write BEFORE implementation. Format: `tests/path::test_name` — what it verifies.
Derive from acceptance criteria and tech-spec.
Conditional: fill for code tasks. For non-code tasks (user instructions, deploy, config) — delete this section.

### 6. Acceptance Criteria
Checklist of what must work.

### 7. Context Files
Use markdown links for all paths.

**Always (feature-specific):**
- [user-spec.md](../user-spec.md)
- [tech-spec.md](../tech-spec.md)
- [decisions.md](../decisions.md)

**Always (project context):**
- [project.md]({discovered PK path}/project.md)
- [architecture.md]({discovered PK path}/architecture.md)

**By task relevance (from PK discovery):**
Include other PK references relevant to this task. Use actual paths discovered in step 2.
Examples: patterns.md (incl. Testing section) for code tasks, architecture.md (Data Model section) for DB tasks, ux-guidelines.md for UI tasks.
Rule: better to include an extra doc than miss an important one.

**Code files:** from files_to_modify / files_to_read.

### 8. Verification Steps
Split into subsections:
- **Automated:** test commands from TDD Anchor (e.g., `pytest tests/test_xxx.py -v`)
- **Smoke:** copy concrete commands from tech-spec task's `Verify-smoke:` field.
  Executable checks the agent runs during implementation — no deployment needed.
  Types: command (curl, python -c, docker build), MCP tool, API call, local server, agent with test prompt.
  Omit subsection if tech-spec has no Verify-smoke for this task.
- **User:** copy from tech-spec task's `Verify-user:` field.
  Agent asks user to verify (UI, behavior, experience). Omit if none.

For non-code tasks (deploy, config): adapt sections to match task nature
(deploy → check logs, config → verify values).

### 9. Details
All details for task execution — technical, organizational, any other.
Files (with current state and what to change — based on reading actual code), Dependencies, Edge cases, Implementation hints.

### 10. Reviewers
List of reviewers. For each: name + report path.
Report path: {feature_path}/logs/working/task-{N}/{reviewer-name}-{round}.json
Reason: bare `logs/...` paths resolve from CWD (project root), not from the feature directory. Always anchor to feature_path.

### 11. Post-completion
Checklist:
- [ ] Write report to decisions.md (include all review rounds with links)
- [ ] If deviated from spec — describe deviation and reason
- [ ] Update user-spec/tech-spec if anything changed

## Rules

- Describe concrete outcomes and deliverables for each step
- Keep steps declarative — focus on WHAT to implement
- Each task must be atomic (one logical unit of work)

## Output

Return the file path when done.
