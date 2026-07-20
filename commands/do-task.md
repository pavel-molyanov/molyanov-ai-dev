---
description: |
  Execute task from tasks/*.md with quality gates.

  Use when: "выполни задачу", "сделай таску", "do task", "execute task", "запусти задачу"
---

# Do Task

## Project Documentation Autosync

If this command changes any project-local `.claude/**` file, immediately run:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

If sync reports a conflict, stop and report it. Include generated `.codex/**` changes in the same commit as the `.claude/**` source change.

Execute a spec-driven task with validation and status tracking.

## Step 1: Read Task

1. Read task file (user provides path or task number)
   - If user didn't specify → ask: "Which task to execute?"
2. Derive feature directory from task path: `work/{feature}/tasks/N.md` → `work/{feature}/`
   All `logs/` paths in the task (Reviewers section, What to do, Acceptance Criteria) are relative to this feature directory. Resolve them as `{feature_dir}/logs/...` when creating files.
3. Verify task status is `planned` (if not → ask user before proceeding)
4. Update task frontmatter: `status: planned` → `status: in_progress`
5. Read every file listed in the task's "Context Files" section

## Step 2: Execute

1. Load each skill listed in the task (frontmatter `skills: [...]` and "Required Skills" section)
   - If a skill is not found → warn user, continue with remaining skills
   - If task has no skill (frontmatter `skills: []` or absent) → read the task, execute "What to do" and "Verification Steps" directly. For tasks with user instructions → show the instruction to user, wait for confirmation.
2. Follow loaded skill workflow. The loaded skill owns the review loop (e.g. code-writing
   runs the test critique and code reviews itself) — do not run reviewers again here.
3. Git commit implementation (code + tests pass): `feat|fix|refactor: task {N} — {brief description}`
4. **Skill-less tasks only** (frontmatter `skills: []` or absent): no skill owns reviews,
   so run the task's "Reviewers" section here, following the policy in
   `~/.claude/skills/skill-master/references/agents.md` → The orchestrator's half of the deal:
   1. For each reviewer, spawn a subagent via Task tool (subagent_type = reviewer name)
   2. Pass: paths to all files this change touched (reviewer reads them in full, not a diff),
      path to task file, tech-spec, user-spec
   3. Report → the path in the task's "Reviewers" section, resolved under `{feature_dir}`
      (e.g. `logs/working/task-1/...` → `{feature_dir}/logs/working/task-1/...`)
   4. Process findings: in-scope fix / disagree → discuss / out-of-scope → surface to user.
      Fix, re-run tests, git commit `fix: address review round {R} for task {N}`, then spawn a
      **fresh** reviewer for the next round. Max 2 rounds; in-scope findings remaining after
      round 2 → ask user.

## Step 3: Verify

1. Check each acceptance criterion from task file
2. If task has "Verification Steps → Smoke" → execute each smoke command, record results in decisions.md Verification section
3. If task has "Verification Steps → User" → ask user to verify, wait for confirmation
4. If any verification fails → fix → re-run tests → spawn fresh reviewers (new round) → re-verify
   - After 2 failed rounds → stop, report failures to user, keep status `in_progress`
   - Tool unavailable → document, suggest manual check

## Step 4: Complete

1. Read template `~/.claude/shared/work-templates/decisions.md.template` and write a concise execution report to `work/{feature}/decisions.md`. Follow template format strictly — no extra sections.
2. Update task frontmatter: `status: in_progress` → `status: done`
3. Update tech-spec: `- [ ] Task N` → `- [x] Task N`
4. Git commit: `chore: complete task {N} — update status and decisions`

## Self-Verification

- [ ] Task status is `done`
- [ ] Tech-spec checkbox updated
- [ ] decisions.md entry written with reviews and verification results
- [ ] Git commit created with task reference
- [ ] Every acceptance criterion from task file is met
