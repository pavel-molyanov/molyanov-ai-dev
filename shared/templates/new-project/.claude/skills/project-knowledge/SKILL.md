---
name: project-knowledge
description: Use when you need information about this project's architecture, tech stack, coding patterns, database schema, deployment setup, git workflow, or UX guidelines. Contains comprehensive project documentation including design decisions, technical specifications, and development standards.
---

# Project Knowledge

This skill provides access to all project documentation and context files that define how this project works, how code should be written, and how features should be developed.

## When to use

Activate this skill when you need to:
- Understand project architecture and tech stack
- Learn coding patterns and conventions
- Check database schemas and data models
- Review deployment and infrastructure setup
- Follow git workflow and branch strategy
- Apply UX guidelines and design system
- Make technical decisions aligned with project standards

## Available guides

All documentation is in the `guides/` folder:

- **[project.md](guides/project.md)** - Project overview, purpose, target audience, core features, scope boundaries
- **[features.md](guides/features.md)** - Complete feature inventory with priorities, dependencies, and status
- **[roadmap.md](guides/roadmap.md)** - Development phases, milestones, timeline, and migration plan (if applicable)
- **[architecture.md](guides/architecture.md)** - Tech stack, project structure, dependencies, external integrations, data flow
- **[patterns.md](guides/patterns.md)** - Coding standards, naming conventions, code organization, error handling, security practices, testing patterns
- **[database.md](guides/database.md)** - Database type, main tables/collections, constraints, migration strategy, naming conventions, sensitive data handling
- **[deployment.md](guides/deployment.md)** - Deployment platform, SSH access, environment variables, deployment triggers, rollback procedures, environments
- **[git-workflow.md](guides/git-workflow.md)** - Branch structure, branch decision criteria, testing strategy before merge, security gates, PR process
- **[ux-guidelines.md](guides/ux-guidelines.md)** - Interface language, tone of voice, domain glossary, text patterns, design system, accessibility requirements
- **[monitoring.md](guides/monitoring.md)** - Logging, error tracking, metrics, health checks, alerting for production monitoring
- **[business-rules.md](guides/business-rules.md)** - Domain workflows, validation rules, calculations, state machines (optional - delete if not needed)

## How to use

Read specific guides as needed for your task. The skill description indicates when to activate, but you can always proactively read individual files when:

- Starting feature development - read `project.md`, `architecture.md`, `patterns.md`
- Implementing database changes - read `database.md`
- Working on UI/UX - read `ux-guidelines.md`
- Setting up deployment - read `deployment.md`
- Creating branches or PRs - read `git-workflow.md`

All guides are maintained as single source of truth for project knowledge.
