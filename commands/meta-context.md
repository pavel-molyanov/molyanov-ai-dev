---
description: Load context for working in ~/.claude/ meta-project
allowed-tools: []
---

# Meta: Global Claude Code Workspace

## Context
You're in `~/.claude/` - the **meta-project** for building AI-First development methodology, NOT a regular project.

## Key Principles
- **Spec-driven approach:** spec → decomposition → tasks → implementation
- **Global configuration:** Changes here affect ALL projects via templates
- **Agent orchestration:** Main agent orchestrates, specialized subagents execute (coding, testing, etc.)
- **User role:** Entrepreneur/product owner (non-developer), building development system with AI

## Structure
- `skills/` - skill system with guides and rules (infrastructure, testing, command-manager, methodology)
- `shared/templates/` - project templates (replicated to all projects)
- `commands/` - slash commands, `agents/` - subagents, `hooks/` - automation hooks
- `projects-registry.json` - registry of all AI-First projects
- `CLAUDE.md` - **GLOBAL** file (affects all projects - ask before changes!)

## Critical
ALWAYS ask before modifying `CLAUDE.md` - these changes propagate to ALL projects.

## Need More Context?
For full methodology documentation, workflows, and detailed guides, invoke the `methodology` skill.
