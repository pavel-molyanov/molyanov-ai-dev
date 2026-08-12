---
name: infrastructure-setup
description: |
  Provides project infrastructure conventions and review criteria for local setup, Docker,
  Git hooks, CI/CD, service delivery, release artifacts, monitoring, backups, and operations.

  Use when: "настрой инфраструктуру", "измени CI/CD", "подготовь деплой", "настрой Docker",
  "собери release artifact", "настрой мониторинг", "проверь инфраструктуру", "оцени деплой",
  "setup infrastructure", "review infrastructure"
  Do NOT use for: choosing or writing application tests without an infrastructure change.
---

# Infrastructure Conventions

## Manual Claude-to-Codex Sync

Claude-side is the source of truth for the converter's allowlist: global `skills/**`,
`agents/*.md`, and `commands/*.md`; or project `CLAUDE.md`, `.claude/skills/**`,
`.claude/agents/*.md`, and `.claude/commands/*.md`. Codex-side outputs are generated runtime. No scheduled job performs this
conversion. After editing an allowlisted source, run the matching command and review the generated
result before finishing:

```bash
~/.claude/scripts/sync-to-codex.sh --apply                   # global ~/.claude/**
~/.claude/scripts/sync-to-codex.sh --project "$PWD" --apply  # project .claude/**
```

For a project, commit generated `.codex/**` and `AGENTS.md` changes with their Claude sources,
except host-local `.codex/.sync/**`. Global `~/.codex/**` is runtime state outside the
`~/.claude` repository: run the global command explicitly on every affected host and do not add
it to the Claude-source commit. If sync reports a conflict or validation error, stop and report
it.

## Scope and Judgment

- Project Knowledge is required infrastructure context. If it is absent, stop and ask the user to
  create or fill it before continuing.
- The user's request defines which changes are authorized. A request to inspect, review, or assess
  current infrastructure authorizes diagnosis and recommendations, not implementation.
- Existing architecture and Project Knowledge are the current contract, not proof that the setup
  is good. Report demonstrated defects, unnecessary complexity, unsafe behavior, operational
  risks, and worthwhile improvements instead of silently accepting them.
- Do not implement an improvement outside the user's request merely because it is beneficial.
  Explain the evidence, impact, and proposed direction, then obtain agreement before changing it.
- Discuss the situation with the user when material information is missing or contradictory, an
  action can affect production, users, data, secrets, or neighboring projects, the safe result is
  uncertain, the current setup appears wrong, or the intended response expands the request.
- Treat a rare or unagreed operational scenario as a user decision even when its correction looks
  local. Ask before adding or changing delivery, recovery, monitoring, isolation, persistent state,
  infrastructure entities, dependencies, architecture, or material complexity.
- Apply only the topic rules relevant to the request; these are conventions, not a required setup
  sequence.

## Project-Specific Ownership

- Concrete hosts, platforms, users, paths, ports, service names, deployment triggers, direct-access
  policy, agent or operations host, monitoring location, notification route, backup destinations,
  and emergency recovery facts belong in Project Knowledge's deployment owner.
- Keep those facts current through `documentation-writing` when an infrastructure change alters
  them. Do not copy private project facts into this global skill or another public methodology
  file.
- Project-specific decisions override the generic patterns here. If a documented choice is risky
  or no longer fits reality, report it and discuss a change rather than overriding it silently.

## Repository and Runtime Rules

- Do not introduce Docker, a server, a hook, or an environment merely because the skill covers it.
- Git pre-commit uses gitleaks for secret scanning and may add only fast staged-file lint or format
  checks. Full test suites and builds belong in CI. Test a secret-like fixture only in a disposable
  repository so it never enters the project's index, history, or reflog.
- When Docker is used, exclude secrets from the build context and image layers and give the final
  container only the privileges it needs.
- Keep secrets out of Git and command output. Local values belong in ignored `.env` or protected
  config files; CI values belong in its secret store; runtime-only values belong in a protected
  target-side file or secret store. Keep a value-free `.env.example` when configuration names need
  documenting.
- Give project-owned ephemeral resources such as logs, caches, obsolete images, deployment
  bundles, temporary builds, and CI artifacts a bounded retention or size policy. Backups need
  retention that preserves current recovery needs and a verified restore path. Do not invent an
  expiry for persistent application data or clean another project's resources.

## Topic Rules

For a persistent service or deployment assessment, apply
[deployment.md](references/deployment.md) — delivery model, shared-host placement, environments,
production safety, rollback, and runtime verification.

For downloadable builds, browser extensions, packages, or CLIs, apply
[release-artifacts.md](references/release-artifacts.md) — verified artifacts, retention, and the
manual Chrome Web Store boundary.

For health checks, timers, alerts, or monitoring assessment, apply
[monitoring-and-alerting.md](references/monitoring-and-alerting.md) — control-host placement,
incident behavior, notification routing, installation, and drills.

## Verification and Review

- Match implementation verification to the changed boundary: container, workflow, artifact,
  timer, recovery path, or user-facing service behavior. Do not replay unrelated checks.
- Use a fresh `infrastructure-reviewer` for an explicit review of current infrastructure or a
  change that materially affects production delivery, secrets, environment isolation, release
  publication, recovery, retention, monitoring, or shared-host boundaries. A trivial local or
  formatting-only change whose result is fully established by direct verification does not need a
  dedicated review. Supply the requested review boundary, relevant existing infrastructure,
  Project Knowledge, applicable topic references, and available runtime evidence.
- When a dedicated review is required, run no more than two review waves. Wave 1 reviews the
  requested current-infrastructure or completed-change boundary. After an authorized correction
  changes the reviewed result, re-verify the affected boundary, refresh durable Project Knowledge
  facts, and run wave 2 with a fresh `infrastructure-reviewer`. Stop after a clean wave or when no
  authorized correction changes the result. Include reviewers required by other active skills in
  these same waves instead of starting a separate wave sequence.
- Review findings are diagnoses, not a work queue. Check the evidence and exact correction. Apply
  only an authorized local correction to agreed normal operation. If the scenario is rare or
  unagreed, or the correction adds delivery, recovery, monitoring, isolation, persistent state,
  infrastructure entities, dependencies, architecture, or material complexity, reject it with a
  short reason or ask the user before editing. `user_decision_required: false` does not replace
  this check. Report unsupported or unrelated findings without acting on them.
- After wave 2, do not launch another reviewer automatically. If a remaining local correction is
  made inside the agreed change, verify its affected boundary directly and refresh durable Project
  Knowledge facts. Report any remaining risks or required user decisions.
