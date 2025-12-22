# Monitoring Context

## Purpose
This file describes logging, error tracking, and metrics setup for AI agents. Helps agents understand observability and debugging infrastructure.

---

## Logging

**Where logs are stored:** [e.g., "stdout (Docker logs)" / "CloudWatch Logs" / "Local files in /logs/" / "None - no logging configured"]

**Log format:** [e.g., "JSON structured logs" / "Plain text" / "Default framework logging (console.log, print)"]

**Log retention:** [e.g., "7 days" / "30 days" / "No retention policy"]

<!-- If using structured logging, specify log fields: timestamp, level, message, userId, requestId, etc. -->

---

## Error Tracking

**Tool:** [e.g., "Sentry" / "Rollbar" / "None"]

**Configuration status:** [e.g., "Configured - SENTRY_DSN in .env" / "Not configured yet" / "Not needed"]

**What's tracked:** [e.g., "Unhandled exceptions, API errors" / "N/A"]

<!-- If using error tracking, mention:
- DSN/API key location (.env variable name)
- Which environments are tracked (production only / staging + production)
- Sample rate or filtering rules if configured
-->

---

## Metrics (Optional)

**Analytics:** [e.g., "Google Analytics (GA4)" / "Vercel Analytics" / "None"]

**Performance tracking:** [e.g., "Response time tracked in Vercel dashboard" / "Custom metrics with Prometheus" / "Not tracked"]

**Key metrics monitored:** [e.g., "API response time, error rate, user signups" / "N/A"]

<!-- Only include if you actively monitor metrics. Skip this section if no metrics collection. -->

---

## Health Checks (Optional)

**Endpoint:** [e.g., "GET /health" / "GET /api/healthz" / "None"]

**What it checks:** [e.g., "Database connectivity, external API status" / "Just returns 200 OK" / "N/A"]

**Used by:** [e.g., "Docker health check, load balancer" / "Manual monitoring" / "N/A"]

<!-- Only include if you have health check endpoints for monitoring or orchestration tools -->

---

## Alerts (Optional)

**Alert tool:** [e.g., "PagerDuty" / "Email alerts from Sentry" / "None"]

**Alert rules:** [e.g., "Error rate > 5%, API down" / "N/A"]

**Who gets alerted:** [e.g., "dev@example.com" / "Slack #alerts channel" / "N/A"]

<!-- Only include if you have active alerting configured -->

---

<!--
If no monitoring infrastructure exists, you can simplify this file to:

"No monitoring configured - logs output to stdout only. Consider adding Sentry for error tracking in production."

or delete optional sections above and keep only Logging + Error Tracking.
-->
