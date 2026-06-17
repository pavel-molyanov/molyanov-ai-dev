---
description: Первичное заполнение документации проекта
---

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
