---
name: deploy-pipeline
description: |
  Sets up CI/CD pipelines, deployment configuration, and automated deploy workflows.
  GitHub Actions, platform-specific deploy (Vercel, Railway, Fly.io, AWS, VPS),
  secrets management in CI.

  Use when: "подготовь деплой", "настрой автодеплой", "настрой CI/CD",
  "setup deploy", "configure deployment", "настрой пайплайн"
---

# Deploy Pipeline

## Project Documentation Autosync

Project documentation source of truth is Claude-side: `CLAUDE.md` and `.claude/**`.
Codex-side `AGENTS.md` and `.codex/**` are generated runtime files.

After changing any project-local `.claude/**` file, immediately run:

```bash
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply
```

If sync reports a conflict, stop and report it. Include generated `.codex/**` changes in the same commit as the `.claude/**` source change.

## Gathering Deployment Context

Read project-knowledge to understand the deployment target:
- `.claude/skills/project-knowledge/references/deployment.md`
- `.claude/skills/project-knowledge/references/architecture.md`
- `.claude/skills/project-knowledge/references/patterns.md`

If deployment target is not documented, ask the user:
- Target platform (Vercel, Railway, Fly.io, AWS ECS, VPS, NPM, Chrome Web Store)
- Environment details (URLs, project/service IDs, server access)
- Required secrets and where to obtain them

After gathering answers, immediately update `deployment.md` before proceeding with setup.

## CI/CD Convention

Create `.github/workflows/ci.yml` following this structure:

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  check-skip:
    runs-on: ubuntu-latest
    outputs:
      should_skip: ${{ steps.check.outputs.should_skip }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 2
      - id: check
        run: |
          FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD)
          if echo "$FILES" | grep -vqE '\.(md|txt)$|^\.claude/|^\.spec/|^docs/'; then
            echo "should_skip=false" >> $GITHUB_OUTPUT
          else
            echo "should_skip=true" >> $GITHUB_OUTPUT
          fi

  test:
    needs: check-skip
    if: needs.check-skip.outputs.should_skip != 'true'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # setup, install, lint, type-check, test, build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      # platform-specific deploy action
```

Adapt: add language setup, install steps, platform-specific deploy action.

## Platform Selection

| Platform | Choose when |
|----------|------------|
| Vercel | Next.js, React, static sites, serverless |
| Railway | Full-stack apps needing managed DB |
| Fly.io | Docker containers, global edge |
| AWS ECS | Enterprise, full infrastructure control |
| Custom VPS | Persistent sessions, multi-device |
| NPM | Node.js packages or CLI tools |
| Chrome Web Store | Browser extensions |

For VPS deployments: server-specific details (IPs, SSH keys, paths) go to `deployment.md`.

## Secrets Convention

Document all required secrets in `.claude/skills/project-knowledge/references/deployment.md`. For each secret:
- Name (GitHub Actions key)
- Where to obtain value (dashboard URL or CLI command)
- Which workflow uses it

Guide user to add secrets in GitHub repository settings. Create `.env.example` with application-level variable names.

## Documentation Updates

After configuring, update project-knowledge references. Append to existing content.

**deployment.md:** deploy target, pipeline overview, required secrets table, manual deploy command, rollback steps.

**patterns.md (Git Workflow section):** CI triggers, pipeline jobs, skip logic pattern, PR workflow.

## Decision Framework

**Add deploy job?**
YES if: deployment target defined, user requests it, stable main branch.
NO if: early development, manual deploys preferred, manual review step needed (Chrome Web Store).

**Use matrix strategy?**
YES if: NPM package, cross-platform library.
NO if: single-environment app, internal tool.

**Add staging?**
YES if: project uses main + dev branches (default workflow).
NO if: Vercel preview deploys sufficient.
