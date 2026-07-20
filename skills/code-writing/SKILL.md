---
name: code-writing
description: |
  Universal quality coding process: plan, TDD, reviews.
  Use whenever code needs to be written — ad-hoc or as part of a task.

  Use when: "напиши код", "закодь", "реализуй", "write code", "implement"

  Do NOT use for pure layout from Figma, Claude Design, screenshots, or an existing visual
  style ("сверстай", "подвинь блок", responsive) — use layout-writing instead.
  Direct mixed layout + business-logic work uses both layout-writing and code-writing.

  For planning tasks → tech-spec-planning skill. For specs → user-spec-planning skill.
---

# Code Writing

## Phase 1: Preparation

1. **Parse Requirements**
   - Extract what needs to be built from user message or passed acceptance criteria
   - Clarify ambiguities — ask user if unclear
   - Formulate acceptance criteria (what "done" looks like)

2. **Read Project Context (Graceful)**

   **Working on a task?** Read all files listed in the task's "Context" section — it already specifies everything needed.

   **Standalone (no task file)?** Read (skip if missing):
   - `.claude/skills/project-knowledge/references/project.md` — project overview
   - `.claude/skills/project-knowledge/references/architecture.md` — system structure
   - `.claude/skills/project-knowledge/references/patterns.md` — project conventions

   Then read `.claude/skills/project-knowledge/SKILL.md` (if exists).
   Consider which domain-specific guides are relevant to your task and read those
   (e.g., `architecture.md` Data Model section for DB work, `ux-guidelines.md` for UI tasks).

   **No project patterns?** Apply baseline from [universal-patterns.md](references/universal-patterns.md) — naming, error handling, structure.

3. **Analyze & Review Approach**

   Before coding, output your findings:
   - Grep for usages of code to be modified
   - Read all files that will be changed
   - Verify solution follows project patterns (or universal patterns)
   - Identify existing code that can be reused
   - If modifying existing code, run existing tests for the area to establish baseline

   If concerns → discuss with user before proceeding.

**Checkpoint:** List completed preparation steps before moving to implementation.

## Phase 2: Implementation (TDD)

1. **Write Tests First**

   **Before writing tests**, read [testing-guide.md](references/testing-guide.md) — when to write which test type, test structure.

   - Write tests for: business logic, validations, transforms, error handling. Skip trivial code without logic (simple getters, one-liners, configs)
   - Write tests for requirements and edge cases
   - Tests should fail initially (no implementation yet)
   - One test = one scenario, test behavior not implementation
   - If mocking >3 dependencies → wrong test type, use integration test

2. **Critique Tests** (before writing code)

   Spawn a fresh `test-reviewer` in `design` mode. No implementation exists yet, so it
   attacks test design (behavior-not-implementation, edge/error coverage, meaningful
   assertions, right test type) rather than the litmus test, which needs running code.
   Pass: paths to the test files you wrote + acceptance criteria.
   Report path: `logs/working/task-{N}/test-reviewer-design-{round}.json`
   (`{N}` = task number, `"standalone"` if no task file). This phase's 2-round cap is
   independent of the Phase 3 code-review cap — each critic phase gets its own two rounds.

   Process findings by the Phase 3 "Process Findings" rules (in-scope fix / disagree →
   discuss / out-of-scope → surface to user). Strengthen the tests, then spawn a **new**
   `test-reviewer` for the next round — a fresh instance, not the same one.
   Limit: 2 rounds. If in-scope findings remain after round 2 → ask the user before
   writing code. Reason: catching a hollow test now is cheaper than discovering after
   the code is built that the tests never protected it.

3. **Write Code**
   - Implement to pass tests
   - Follow project patterns (from Phase 1) or apply baseline from [universal-patterns.md](references/universal-patterns.md)
   - Use env vars for secrets, validate inputs at boundaries
   - Handle edge cases, comment WHY not WHAT

4. **Run Tests**
   - All new tests pass
   - Fix any failures

**Checkpoint:** List implemented functionality and test results.

## Phase 3: Post-work

1. **Run Lint/Format**
   - Run project's linter and formatter before reviews

2. **Run Relevant Tests**
   - Tests for files changed
   - Tests mentioned in task (if applicable)
   - Save full test suite for end of feature

3. **Smoke Verification** (if task has Verification Steps → Smoke or User)

   Execute each command from the Smoke section. Record results in decisions.md Verification section.
   If a check fails — fix the code before proceeding to reviews.
   If the task has User checks — ask the user to verify, wait for confirmation.

   Smoke catches integration bugs that mocked tests miss:
   real API responses, library initialization, config validity.

4. **Run Reviews** (launch in parallel)

   **Reviewer selection:**
   - Working on a task file → run reviewers from the task's "Reviewers" section
   - Standalone (no task file) → default: code-reviewer, security-auditor, test-reviewer

   For each reviewer:
   1. Spawn subagent via Task tool (subagent_type = reviewer name, e.g. `code-reviewer`)
   2. Pass: paths to all files this change touched (the reviewer reads them in full,
      not a diff — a hole usually lives where a change contradicts an untouched part),
      path to task file, path to tech-spec, path to user-spec. For `test-reviewer` use
      `full` mode here (code exists, so the litmus test applies).
   3. Reviewer loads its own skill automatically (via agent frontmatter `skills:`)
   4. Report path: from the task's "Reviewers" section (or `logs/working/` if standalone)

   Reviewers write JSON reports to `logs/working/task-{N}/{reviewer-name}-{round}.json`.
   `{N}` = task number from task file; `"standalone"` if no task file.
   On re-review: spawn a **fresh** reviewer instance (not the same one) — it re-reads the
   touched files from scratch. Write a new file with an incremented round number.

5. **Process Findings**

   Evaluate each finding on merit — severity is metadata, not a filter.
   A valid minor fix still improves quality. Reason: skipping valid findings
   silently degrades the codebase over time.

   Scope: in-scope = this task's acceptance criteria + files this change touched.
   Out-of-scope = anything beyond that (new behavior, untouched files, an unrelated
   pre-existing defect). For each finding:
   - **Valid, in-scope, agree** → apply (any severity: critical, major, minor, low)
   - **In-scope but you disagree or are uncertain** → discuss with user (explain reasoning)
   - **Out of scope** → surface to user, don't fix silently — the user decides whether
     it's worth expanding the work

   Produce a findings log:
   | # | Source | Severity | Finding | Action | Reason |
   Each finding appears in this table — transparent decision trail.

   After applying fixes → re-run tests → spawn a fresh reviewer instance for the next round.
   Limit: 2 review rounds. If in-scope findings remain after round 2 → ask user.
   Reason: fixes can introduce new issues — a second pass catches regressions; beyond two
   rounds the remaining findings need human judgment, not another loop.

**Checkpoint:** List post-work steps completed.

## Self-Verification

Verify each item before marking complete. If any item fails, return to the relevant phase.

- [ ] All phases completed (Preparation, Implementation, Post-work)
- [ ] Tests pass
- [ ] Smoke verification executed (if task had Smoke/User checks)
- [ ] Each reviewer finding evaluated and logged
- [ ] Findings log table produced
- [ ] Review JSON reports saved to `logs/working/task-{N}/`

