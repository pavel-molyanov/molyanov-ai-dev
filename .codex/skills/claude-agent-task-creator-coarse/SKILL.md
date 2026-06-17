---
name: claude-agent-task-creator-coarse
description: Converted Codex role prompt from Claude agent `task-creator-coarse`. Use when the user asks for this reviewer/validator role or when a workflow explicitly references it.
---

# Converted Role: task-creator-coarse

Generated from `~/.claude/agents/task-creator-coarse.md`.
Codex does not have native Claude custom agent types. Use this as a role/reference prompt with `worker` or `explorer` subagents when subagents are explicitly appropriate.

Create task file for the specified task from coarse tech-spec. Coarse task covers one skill's cohesive scope in the feature — several related steps grouped under a single skill, with commit points between steps.

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
- skills: Array of skills for the task (default: [code-writing]) — expected to be length 1 for coarse tasks, except for audit/QA tasks that use methodology skills
- reviewers: Array of reviewers (default: [code-reviewer, security-auditor, test-reviewer])
- verify: Array of verification types: [smoke], [user], [smoke, user], or [] (default: [])
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
   - Title: replace `Task N: Название` with actual task number and name
   - Required Skills: replace with actual skills for this task
   - Description: explain the skill's scope in this feature — what the role accomplishes and how it fits the whole
   - What to do: write as a checklist of related steps with commit points between them (see Task File Structure section 4)
   - TDD Anchor: list tests covering all steps in What to do (for code tasks)
   - Acceptance Criteria, Context Files, Verification Steps, Details, Reviewers, Post-completion: replace placeholder content with real content based on tech-spec and code analysis
   - For non-code tasks: delete TDD Anchor section entirely

## Task File Structure

### 1. Frontmatter
- status: planned
- depends_on: {from input}
- wave: {from input}
- skills: {from input, array of length 1 for coarse tasks, except audit/QA}
- verify: {from input, array of types: [smoke], [user], [smoke, user], or []}
- reviewers: {from input, array}
- teammate_name: {from input, optional — cosmetic name for agent teams}

### 2. Required Skills
Instructions for the implementing agent — which skills to load before starting work on this task.
Duplicate frontmatter skills as explicit load instructions:
"Before starting, load: /skill:{name} — [SKILL.md](path)"

### 3. Description
What this task accomplishes and how it fits the feature. Coarse tasks cover one skill's scope — describe the role's full responsibility in this feature. Write as much as needed for clear understanding.

### 4. What to do
Checklist of concrete related steps. Each item is one logical unit of work with a commit point after it.

Format:
```markdown
- [ ] Step 1: {what} — commit: `feat: {message}`
- [ ] Step 2: {what} — commit: `feat: {message}`
- [ ] Step 3: {what} — commit: `feat: {message}`
```

Focus on WHAT, not HOW. No pseudocode, no algorithms. Each step should be independently committable (tests pass after the commit).

For non-code tasks (user instructions, deploy, config): adapt format — checklist without commits if no code is produced.

### 5. TDD Anchor
Tests to write BEFORE implementation, covering all steps in What to do. Format: `tests/path::test_name` — what it verifies.
Derive from acceptance criteria and tech-spec.
Conditional: fill for code tasks. For non-code tasks (user instructions, deploy, config) — delete this section.

### 6. Acceptance Criteria
Checklist of what must work after all steps are done.

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

For non-code tasks (deploy, config): adapt sections to match task nature.

### 9. Details
All details for task execution — technical, organizational, any other.
Files (with current state and what to change — based on reading actual code), Dependencies, Edge cases, Implementation hints.

For coarse tasks: Files subsection lists all files touched by the skill's scope, grouped by What-to-do step if helpful.

### 10. Reviewers
List of reviewers. For each: name + report path.
Report path: {feature_path}/logs/working/task-{N}/{reviewer-name}-{round}.json
Reason: bare `logs/...` paths resolve from CWD (project root), not from the feature directory. Always anchor to feature_path.

### 11. Post-completion
Checklist:
- [ ] Write report to decisions.md (include all review rounds with links). For coarse tasks: entry summarizes what was done per What-to-do step
- [ ] If deviated from spec — describe deviation and reason
- [ ] Update user-spec/tech-spec if anything changed

## Rules

- Each task covers one skill's cohesive work scope in the feature
- Multiple related steps grouped together, with commit points between them
- Independent work within the same skill goes to separate tasks (enables parallelism within wave)
- Different skills → always different tasks
- Steps within a task share a common outcome (removing any step leaves the feature's role incomplete)
- Describe concrete outcomes and deliverables for each step
- Keep steps declarative — focus on WHAT to implement

## Output

Return the file path when done.
