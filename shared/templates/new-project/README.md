<!--
Scaffold for the project README. README is for humans — write the final content
in the language the user writes in. Headers below are a starting point; localize them too.
-->

# [Project name]

> **This README is for the project owner**, not for AI agents.
> Instructions for agents live in CLAUDE.md and .claude/skills/project-knowledge/references/

## About

[Short description: what the project does and why it exists]

## Project structure

```
.claude/                    # Knowledge base for AI agents
├── skills/
│   └── project-knowledge/  # Project docs (architecture, patterns, etc.)
└── ...

backlog.md        # Feature ideas and bugs (what to do later)
work/             # Active features and bugs (what we're doing now)
├── templates/    # Templates for specs and tasks
└── [features]/   # Each feature in its own folder

src/              # Source code
```

## Development methodology

The project uses a **spec-driven approach** with AI agents:

1. **User Spec** (user's language) → describe WHAT and WHY
2. **Tech Spec** (English) → describe HOW to implement
3. **Tasks** → decomposition into tasks
4. **Implementation** → AI agent writes the code

All features and bugs are tracked in the `work/` folder.

- **guides/** — guides for working with the methodology
