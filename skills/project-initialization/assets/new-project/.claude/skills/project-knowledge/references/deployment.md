# Deployment & Operations

## Purpose
Deployment process, infrastructure, and production operations for AI agents.

---

## Deployment Platform

**Platform:** [Where it deploys - e.g., "Vercel" / "Railway" / "AWS EC2" / "VPS"]

**Type:** [e.g., "Serverless" / "Container (Docker)" / "Static hosting" / "Browser extension"]

**Why this platform:** [One reason - e.g., "Free tier covers our needs" / "Need full server control"]

---

## Access Information

<!-- Keep only fields that apply. -->

**Host:** [Production hostname or address, if the project has a server runtime]

**User:** [Deployment/operations user]

**Port:** [Only when non-default]

**SSH alias:** [Configured alias, if any]

**Service/container name:** [Exact project-specific name]

**Runtime/project path:** [Exact target path or local workspace path]

**Log location:** [Platform view, file path, or log stream]

**Credentials location:** [e.g., "GitHub Actions secrets" / "1Password vault"]

---

## Operating Model

**Routine delivery:** [Repository CI/CD workflow or other project-specific repeatable path. State
clearly when the project is local-only or has no deployment.]

**Direct target operations:** [Allowed uses such as inspection, initial bootstrap,
troubleshooting, and bounded one-off work. State what must not become an undocumented parallel
routine delivery path.]

**Agent/operations host:** [Persistent host where project agents normally run and operational
checks are managed, or "Not applicable"]

**Environment strategy:** [Why development/staging is separate, or why a private single-owner
project intentionally uses one environment]

**Production authorization:** [User approval or protected workflow gate required before a
production-affecting action]

---

## Environment Variables

**See:** [.env.example](../../../../.env.example) in project root

[List all required environment variables with their purpose - NO VALUES]

<!-- Keep .env.example updated. Comment each variable's purpose in that file. -->

---

## Deployment Triggers

**Production:** [e.g., "Auto-deploy on push to `main` after tests pass"]

**Staging:** [e.g., "Auto-deploy on push to `dev`"]

**Preview:** [e.g., "Auto-deploy for every PR" / "Not configured"]

**Manual repeat:** [GitHub Actions `workflow_dispatch` workflow name, if supported]

---

## Required Manual Release Steps

[Keep only project-specific actions that cannot be automated or recovered from workflow/config.
If none, write "Not applicable" and rely on the Operating Model above for the actual delivery
path.]

- [ ] [Project-specific manual action and why it cannot be automated]

---

## Emergency Recovery

**When to use:** [Broken production or unavailable CI/CD path; not routine deployment]

**Rollback/last-known-good:** [Project-specific artifact, release, or platform action]

**Restart target:** [Service/container/process name and the project-specific action, if needed]

**Data recovery:** [Migration rollback or restore reference, if applicable]

**Non-standard command:** [Only when the action cannot be reconstructed from project config;
otherwise link to the workflow or operations file]

**Verification after recovery:** [Project-specific smoke check, monitoring URL, or expected signal]

---

## Environments

**Production:** [URL] - Deploys from `main` branch

**Staging:** [URL] - Deploys from `dev` branch

<!-- If single environment, only list Production -->

---

## Monitoring & Observability

<!--
SCALING HINT: If this section grows beyond ~80 lines, extract to references/monitoring.md.
If no monitoring configured, write: "Logs output to stdout only. No error tracking configured."
-->

**Control location:** [Agent/operations host, another independent monitoring location, or "None"]

**Notification route:** [Route name and runtime mapping location without tokens or raw recipient
IDs, or "None"]

### Logging

**Where:** [e.g., "stdout (Docker logs)" / "CloudWatch" / "Local files"]
**Format:** [e.g., "JSON structured" / "Plain text" / "Default framework logging"]

### Error Tracking

**Tool:** [e.g., "Sentry" / "Rollbar" / "None"]
**Config:** [e.g., "SENTRY_DSN in .env" / "Not configured"]

### Health Checks (optional)

<!-- Keep only when the project has a server health surface or explicitly requires one. -->

**Endpoint:** [e.g., "GET /health" / "None"]
**Checks:** [e.g., "DB connectivity, external API status" / "N/A"]

<!-- Optional sections below — delete if not applicable -->

### Metrics

**Analytics:** [e.g., "Google Analytics" / "Vercel Analytics" / "None"]
**Key metrics:** [e.g., "API response time, error rate" / "N/A"]

### Alerts

**Tool:** [e.g., "Sentry email alerts" / "PagerDuty" / "None"]
**Rules:** [e.g., "Error rate > 5%" / "N/A"]
