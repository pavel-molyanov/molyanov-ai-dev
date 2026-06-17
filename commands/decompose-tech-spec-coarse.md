---
description: Decompose approved coarse tech-spec into tasks with validation (uses task-decomposition-coarse skill)
allowed-tools:
  - Skill
---

# Instructions

## Project Documentation Autosync

If this command changes any project-local `.claude/**` file, immediately run:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

If sync reports a conflict, stop and report it. Include generated `.codex/**` changes in the same commit as the `.claude/**` source change.

Use the `task-decomposition-coarse` skill.
