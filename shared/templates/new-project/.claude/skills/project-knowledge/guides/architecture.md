# Architecture Context

## Purpose
This file provides technical architecture overview for AI agents. Helps agents understand HOW the system is built.

---

## Tech Stack

**Frontend:** [Framework/Library - e.g., "React 18 with Vite"]
- **Why:** [One reason - e.g., "Fast dev experience with HMR, widely supported"]

**Backend:** [Framework - e.g., "Express.js" / "FastAPI" / "None - static site"]
- **Why:** [One reason - e.g., "Minimal overhead for REST API, large ecosystem"]

**Database:** [Database type - e.g., "PostgreSQL" / "MongoDB" / "None"]
- **Why:** [One reason - e.g., "ACID transactions needed for payments" / "N/A"]

<!-- Add other stack components if needed: Mobile, Desktop, etc -->

---

## Project Structure

[Brief map of where things live - helps agents find relevant code quickly]

```
/
├── src/
│   ├── components/     [UI components]
│   ├── api/           [API routes/endpoints]
│   ├── utils/         [Helper functions]
│   ├── config/        [Configuration files]
│   └── types/         [TypeScript types/interfaces]
├── tests/             [Test files]
└── .claude/           [AI agent context]
```

[Adjust structure to match your project - keep it simple]

---

## Key Dependencies

[List ONLY critical packages that agents need to know about - not every dependency]

**Critical packages:**
- `[package-name]` - [Why we use it - e.g., "Authentication - handles JWT tokens"]
- `[package-name]` - [Why we use it - e.g., "Stripe SDK - payment processing"]
- `[package-name]` - [Why we use it - e.g., "Zod - runtime validation for API inputs"]

<!-- Add 3-5 most important dependencies. Skip obvious ones like React, Express basics -->

---

## External Integrations

[Third-party services/APIs this project connects to]

**[Service name - e.g., "Stripe"]**
- **Purpose:** [What we use it for - e.g., "Payment processing for subscriptions"]
- **Auth method:** [How we authenticate - e.g., "API key in STRIPE_SECRET_KEY env var"]
- **Docs:** [Link to relevant docs if needed]

**[Service name - e.g., "SendGrid"]**
- **Purpose:** [What we use it for - e.g., "Transactional emails"]
- **Auth method:** [How we authenticate - e.g., "API key in SENDGRID_API_KEY"]
- **Docs:** [Link to relevant docs if needed]

<!-- Add all external services. Include auth method so agents know how to make API calls -->

<!-- If no external integrations, write: "None - this project has no external API dependencies" -->

---

## Data Flow

[Describe in 2-4 sentences how data moves through the system. Focus on the main flow, not edge cases.]

<!-- Example: "User submits form → Frontend validates with Zod → POST to /api/users → Backend validates again → Save to PostgreSQL → Return user object → Update UI. Authentication uses JWT tokens stored in httpOnly cookies." -->
