<!--
Scaffold for the project README. README is for humans — write the final content
in the language the user writes in. Headers below are a starting point; localize them too.
-->

# [Project name]

> **This README is for the project owner**, not for AI agents.
> Instructions for agents live in CLAUDE.md and the .claude/skills/project-knowledge/ skill.

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
└── [features]/   # Each planned feature has one user-spec.md

src/              # Source code
```

## Development methodology

The project uses a **spec-driven approach** with AI agents:

1. **User Spec** (user's language) → agree on the complete outcome
2. **Implementation** → a new AI-agent chat executes that user-spec directly
3. **Finalization** → project documentation is updated and the feature is archived

Future feature ideas and known bugs are tracked in `backlog.md`. Active feature and bug work lives
in the `work/` folder.
