---
name: claude-command-init-project-knowledge
description: Converted Codex workflow from Claude slash command `init-project-knowledge`. Use when the user asks to run the equivalent command or describes this workflow.
---

# Converted Command Workflow: init-project-knowledge

Generated from `~/.claude/commands/init-project-knowledge.md`.
Treat Claude-only tool names as conceptual workflow steps and use available Codex tools/policies.

## Codex Policy Gates

- Ask before external actions such as GitHub repository creation, `git push`, deploys, or sending messages unless the user explicitly requested that exact action.
- Deployments must go through GitHub CI/CD; direct server access is only for emergency debugging of broken production.
- Never ask the user to paste secrets in chat. Direct them to `.env` files or GitHub Actions secrets.

# Instructions

## Project Documentation Autosync

If this command changes any project-local `.claude/**` file, immediately run:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

If sync reports a conflict, stop and report it. Include generated `.codex/**` changes in the same commit as the `.claude/**` source change.

Load and execute `project-planning` skill.

```
Skill(project-planning)
```

After project knowledge is written to `.claude/skills/project-knowledge/`, sync the generated Codex copy:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```
