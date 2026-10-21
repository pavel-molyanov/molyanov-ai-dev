<!--
Scaffold for the project README. README is the project's description on GitHub: what the
project is and why it exists, for people opening the repository. It holds no instructions,
workflows or rules for agents — those live in CLAUDE.md and the skills. Write the final content
in the language the user writes in. Headers below are a starting point; localize them too.
-->

# [Project name]

> **This README describes the project on GitHub.** Instructions for AI agents live in CLAUDE.md
> and the .claude/skills/ skills.

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
