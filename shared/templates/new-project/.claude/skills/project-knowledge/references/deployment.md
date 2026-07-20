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

**SSH Access:**
- Production: `ssh user@server-ip` [e.g., `ssh user@server.example.com`]
- Staging: [if applicable]

> If not configured, agent will request: server address, username, and port.

**Credentials location:** [e.g., "GitHub Actions secrets" / "1Password vault"]

---

## Environment Variables

**See:** [.env.example](../../.env.example) in project root

[List all required environment variables with their purpose - NO VALUES]

<!-- Keep .env.example updated. Comment each variable's purpose in that file. -->

---

## Deployment Triggers

**Production:** [e.g., "Auto-deploy on push to `main` after tests pass"]

**Staging:** [e.g., "Auto-deploy on push to `dev`"]

**Preview:** [e.g., "Auto-deploy for every PR" / "Not configured"]

---

## Pre-Deploy Checklist

[Only critical manual steps - if fully automated, write "Fully automated via CI"]

- [ ] [e.g., "Run `npm run migrate:prod` if schema changed"]
- [ ] [e.g., "Verify env vars set in platform dashboard"]

---

## Rollback Procedure

**Platform rollback:** [e.g., "Vercel: 'Redeploy' on previous deployment" / "VPS: `git checkout <prev-commit>`"]

**Manual steps if needed:** [e.g., "If DB migration broke: run rollback SQL from /migrations/rollbacks/"]

**Approximate time:** [e.g., "~2 minutes" / "~10 minutes with DB rollback"]

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

### Logging

**Where:** [e.g., "stdout (Docker logs)" / "CloudWatch" / "Local files"]
**Format:** [e.g., "JSON structured" / "Plain text" / "Default framework logging"]

### Error Tracking

**Tool:** [e.g., "Sentry" / "Rollbar" / "None"]
**Config:** [e.g., "SENTRY_DSN in .env" / "Not configured"]

### Health Checks

**Endpoint:** [e.g., "GET /health" / "None"]
**Checks:** [e.g., "DB connectivity, external API status" / "N/A"]

<!-- Optional sections below — delete if not applicable -->

### Metrics

**Analytics:** [e.g., "Google Analytics" / "Vercel Analytics" / "None"]
**Key metrics:** [e.g., "API response time, error rate" / "N/A"]

### Alerts

**Tool:** [e.g., "Sentry email alerts" / "PagerDuty" / "None"]
**Rules:** [e.g., "Error rate > 5%" / "N/A"]
