# Architecture

## Purpose
Technical architecture overview for AI agents. Helps agents understand HOW the system is built.

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

[Replace this placeholder with the actual agreed project structure. List only directories and
entry points that help agents navigate this project, with a short project-specific purpose for
each. For an existing project, derive the map from current files. For a new project, use the
approved architecture and framework conventions. Remove this instruction after filling it.]

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

<!-- If no external integrations, write: "None - no external API dependencies" -->

---

## Data Flow

[Describe in 2-4 sentences how data moves through the system. Focus on the main flow, not edge cases.]

<!-- Example: "User submits form → Frontend validates with Zod → POST to /api/users → Backend validates again → Save to PostgreSQL → Return user object → Update UI." -->

---

## Data Model

<!--
This section describes database/storage architecture.
SCALING HINT: If this section grows beyond ~80 lines, extract to a separate references/database.md and link from here.
-->

**Database:** [Type - e.g., "PostgreSQL 15" / "MongoDB" / "Not applicable"]

### Main Tables/Collections

[List key tables/collections and their relationships - keep it brief]

**[table_name or CollectionName]**
- Purpose: [What this stores - e.g., "User accounts and profiles"]
- Key fields: [List 3-5 most important fields]
- Relationships: [Links to other tables - e.g., "users.id → orders.user_id"]

<!-- Add main tables. Skip junction/helper tables unless critical -->

### Key Constraints

[Only constraints that would cause errors if violated]

- **Unique constraints:** [e.g., "users.email must be unique"]
- **Foreign keys:** [e.g., "orders.user_id → users.id (ON DELETE CASCADE)"]
- **Required fields:** [e.g., "users: email, password_hash are NOT NULL"]

### Migration Strategy

**Tool:** [e.g., "Prisma Migrate" / "Alembic" / "Django migrations" / "Manual SQL scripts"]

**Process:** [Brief - e.g., "Run `npm run migrate` before deploy. Migrations in /prisma/migrations/. Never edit old migrations."]

### Sensitive Data

[Fields containing PII or secrets - important for security]

**PII fields:**
- [table.field - e.g., "users.email"]
- [table.field - e.g., "users.phone_number"]

<!-- If no sensitive data, write "No PII stored" -->
<!-- If using alternative storage (localStorage, file system, Chrome Storage API), describe it here instead of tables -->
