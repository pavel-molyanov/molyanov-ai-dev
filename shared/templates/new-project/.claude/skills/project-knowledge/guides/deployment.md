# Deployment Context

## Purpose
This file describes deployment process and infrastructure for AI agents. Helps agents understand deployment requirements and constraints.

---

## Deployment Platform

**Platform:** [Where it deploys - e.g., "Vercel" / "Railway" / "AWS EC2" / "Chrome Web Store" / "VPS"]

**Type:** [e.g., "Serverless" / "Container (Docker)" / "Static hosting" / "Browser extension"]

**Why this platform:** [One reason - e.g., "Free tier covers our needs" / "Direct GitHub integration" / "Need full server control"]

---

## Access Information

[How to access the deployment infrastructure]

**SSH Access:**
- Production: `ssh user@server-ip` [e.g., `ssh root@123.45.67.89` or `ssh deploy@prod.example.com`]
- Staging: `ssh user@staging-ip` (if applicable)

> If not configured, agent will request: server address, username, and port (default 22).

**Credentials location:** [Where deployment secrets are stored - e.g., "GitHub Actions secrets" / "1Password vault 'Production Servers'"]

---

## Environment Variables

**See:** [.env.example](../../.env.example) in project root

[List all required environment variables with their purpose - NO VALUES]

<!-- Keep .env.example file updated with all variables. Comment each variable's purpose in that file. -->

---

## Deployment Triggers

**Production:** [e.g., "Auto-deploy on push to `main` after tests pass" / "Manual deploy via button"]

**Staging:** [e.g., "Auto-deploy on push to `dev`" / "Not configured"]

**Preview:** [e.g., "Auto-deploy for every PR" / "Not configured"]

---

## Pre-Deploy Checklist

[Only list critical manual steps - if fully automated, write "Fully automated via CI"]

- [ ] [e.g., "Run `npm run migrate:prod` if schema changed"]
- [ ] [e.g., "Verify env vars set in platform dashboard"]

---

## Rollback Procedure

[How to undo a bad deployment]

**Platform rollback:** [e.g., "Vercel: Use 'Redeploy' on previous deployment in dashboard" / "Railway: Click 'Rollback' on previous deploy" / "VPS: `git checkout <previous-commit> && npm run deploy`"]

**Manual steps if needed:** [e.g., "If DB migration broke: Manually run rollback SQL from /migrations/rollbacks/"]

**Approximate time:** [e.g., "~2 minutes" / "~10 minutes with DB rollback"]

---

## Environments

**Production:** [URL - e.g., "https://app.example.com"] - Deploys from `main` branch

**Staging:** [URL - e.g., "https://staging.example.com"] - Deploys from `dev` branch

<!-- If single environment, only list Production -->
