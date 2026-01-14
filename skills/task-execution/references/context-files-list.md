# Context Files Reference

Complete list of context files and when to read them.

## Always Required

Read these for every task:

| File | Purpose |
|------|---------|
| `.claude/skills/project-knowledge/guides/architecture.md` | System architecture, components |
| `.claude/skills/project-knowledge/guides/patterns.md` | Code patterns, conventions |
| `.claude/skills/project-knowledge/guides/project.md` | Project overview, stack |
| `work/{feature}/user-spec.md` | Business requirements |
| `work/{feature}/tech-spec.md` | Technical decisions |

## From Task File

Always read files listed in task's "Context Files" section.

## Conditional by Task Type

### Database/Schema/Model Tasks
- `.claude/skills/project-knowledge/guides/database.md`

### API/Endpoint/Route Tasks
- `.claude/skills/project-knowledge/guides/api.md`

### Deployment/Infrastructure Tasks
- `.claude/skills/project-knowledge/guides/deployment.md`

### Git/CI-CD Tasks
- `.claude/skills/project-knowledge/guides/git-workflow.md`

### UI/Text/Design Tasks
- `.claude/skills/project-knowledge/guides/ux-guidelines.md`

## Testing Guides

From global skills:

| File | When |
|------|------|
| `~/.claude/skills/testing/guides/unit-tests.md` | Writing unit tests |
| `~/.claude/skills/testing/guides/integration-tests.md` | Writing integration tests |
| `~/.claude/skills/testing/guides/e2e-tests.md` | Writing E2E tests |
| `~/.claude/skills/testing/guides/smoke-tests.md` | Writing smoke tests |

## How to Determine Task Type

Check task file for keywords:

- **Database**: schema, model, migration, table, query, ORM
- **API**: endpoint, route, handler, request, response, REST, GraphQL
- **Deployment**: deploy, docker, CI, CD, pipeline, kubernetes
- **Git**: commit, branch, merge, hook, workflow
- **UI**: component, style, layout, text, design, accessibility
