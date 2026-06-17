---
name: claude-command-do-task
description: Converted Codex workflow from Claude slash command `do-task`. Use when the user asks to run the equivalent command or describes this workflow.
---

# Converted Command Workflow: do-task

Generated from `~/.claude/commands/do-task.md`.
Treat Claude-only tool names as conceptual workflow steps and use available Codex tools/policies.

## Codex Policy Gates

- Ask before external actions such as GitHub repository creation, `git push`, deploys, or sending messages unless the user explicitly requested that exact action.
- Deployments must go through GitHub CI/CD; direct server access is only for emergency debugging of broken production.
- Never ask the user to paste secrets in chat. Direct them to `.env` files or GitHub Actions secrets.

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
2. Follow loaded skill workflow
3. Git commit implementation (code + tests pass): `feat|fix|refactor: task {N} — {brief description}`
4. For each reviewer from the task's "Reviewers" section (if present):
   1. Spawn subagent via spawn_agent (subagent_type = reviewer name, e.g. `code-reviewer`)
   2. Pass: git diff of changes, path to task file, path to tech-spec, path to user-spec
   3. Reviewer loads its own skill automatically (via agent frontmatter `skills:`)
   4. Report is written to the path specified in the task's "Reviewers" section, resolved relative to the feature directory (e.g., `logs/working/task-1/...` → `{feature_dir}/logs/working/task-1/...`)
   5. Read report. If findings exist → fix, re-run tests, git commit: `fix: address review round {N} for task {N}`, repeat (max 3 rounds)

## Step 3: Verify

1. Check each acceptance criterion from task file
2. If task has "Verification Steps → Smoke" → execute each smoke command, record results in decisions.md Verification section
3. If task has "Verification Steps → User" → ask user to verify, wait for confirmation
4. If any verification fails → fix → re-run tests → re-run reviewers (new round) → re-verify
   - After 3 failed rounds → stop, report failures to user, keep status `in_progress`
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
