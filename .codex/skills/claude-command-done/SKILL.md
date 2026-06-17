---
name: claude-command-done
description: Converted Codex workflow from Claude slash command `done`. Use when the user asks to run the equivalent command or describes this workflow.
---

# Converted Command Workflow: done

Generated from `~/.claude/commands/done.md`.
Treat Claude-only tool names as conceptual workflow steps and use available Codex tools/policies.

## Codex Policy Gates

- Ask before external actions such as GitHub repository creation, `git push`, deploys, or sending messages unless the user explicitly requested that exact action.
- Deployments must go through GitHub CI/CD; direct server access is only for emergency debugging of broken production.
- Never ask the user to paste secrets in chat. Direct them to `.env` files or GitHub Actions secrets.

# Done — Finalize Feature

## Project Documentation Autosync

If this command changes any project-local `.claude/**` file, immediately run:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

If sync reports a conflict, stop and report it. Include generated `.codex/**` changes in the same commit as the `.claude/**` source change.

## Step 1: Load Documentation Skill

Use Skill tool: `documentation-writing`

## Step 2: Identify Feature

User typically provides feature directory with the command (e.g., `/done work/my-feature`).
- If provided → use it
- If not → ask: "Which feature to finalize? Provide path to work/{feature}/ directory."

## Step 3: Read Feature Artifacts

Read these files from the feature directory:
1. `user-spec.md` — what was planned
2. `tech-spec.md` — how it was implemented
3. `decisions.md` — what decisions were made during implementation

If `decisions.md` is missing or sparse, use `git log --oneline` for feature-related commits to understand what changed.

**Completeness check:** If the feature looks incomplete (tasks not marked done in tech-spec, missing implementation, failing tests) — warn the user: "Feature appears incomplete: {reason}. Continue with finalization anyway?"

## Step 4: Update Project Knowledge

If `.claude/skills/project-knowledge/references/` does not exist or is empty — skip this step, inform the user that project knowledge has not been initialized.

Otherwise, read current PK files and update only those affected by the feature:
- `architecture.md` — new components, changed structure, data model / schema changes
- `patterns.md` — new project-specific patterns, testing approaches, business rules
- `deployment.md` — deployment or monitoring changes
- If the project has a backlog file, note any status updates for the user

Apply quality principles from documentation-writing skill: no code examples, no obvious content, only project-specific information.

## Step 5: Archive

Move `work/{feature}/` → `work/completed/{feature}/` (create `work/completed/` if it doesn't exist).

## Step 6: Commit & Report

1. Commit PK file changes and feature archive move.
   ```
   docs: update project knowledge after {feature-name}
   ```

2. Report to user:
   - What was done (brief summary from specs)
   - What PK files were updated and what changed
   - Feature archived to `work/completed/{feature}/`

## Self-Verification

- [ ] Documentation-writing skill loaded
- [ ] Feature artifacts read and understood
- [ ] Completeness assessed (user warned if incomplete)
- [ ] PK files updated (only affected ones)
- [ ] Feature archived to work/completed/
- [ ] Changes committed
- [ ] Report delivered to user
