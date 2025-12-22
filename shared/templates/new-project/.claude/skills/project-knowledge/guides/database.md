# Database Context

## Purpose
This file describes database architecture for AI agents. Helps agents write correct queries and maintain data integrity.

---

## Database Type

**Database:** [Type - e.g., "PostgreSQL 15" / "MongoDB" / "Not applicable"]

**Why:** [One reason if applicable - e.g., "ACID transactions for financial data" / "Document flexibility for varied user data" / "This project uses no persistent storage - all data in memory"]

<!-- If using alternative storage (localStorage, file system), describe it here -->

---

## Main Tables/Collections

[List key tables/collections and their relationships - keep it brief]

**[table_name or CollectionName]**
- Purpose: [What this stores - e.g., "User accounts and profiles"]
- Key fields: [List 3-5 most important fields]
- Relationships: [Links to other tables - e.g., "users.id → orders.user_id"]

**[table_name or CollectionName]**
- Purpose: [What this stores]
- Key fields: [List 3-5 most important fields]
- Relationships: [Links to other tables]

<!-- Add all main tables. Skip junction/helper tables unless critical -->

---

## Key Constraints

[Important constraints that agents must respect]

- **Unique constraints:** [e.g., "users.email must be unique"]
- **Foreign keys:** [e.g., "orders.user_id → users.id (ON DELETE CASCADE)"]
- **Required fields:** [e.g., "users: email, password_hash are NOT NULL"]
- **Indexes:** [Only critical ones - e.g., "users.email (for login lookups)"]

<!-- Only list constraints that would cause errors if violated -->

---

## Migration Strategy

[How we handle schema changes]

**Tool:** [What we use - e.g., "Prisma Migrate" / "Alembic" / "Django migrations" / "Manual SQL scripts"]

**Process:** [Brief description - e.g., "Run `npm run migrate` before deploy. Migrations in /prisma/migrations folder. Never edit old migrations."]

<!-- If no formal migrations, describe approach: "Manual SQL - keep scripts in /db/migrations" -->

---

## Naming Conventions

[Only if different from standard conventions]

**Tables:** [e.g., "snake_case plural: users, order_items"]
**Columns:** [e.g., "snake_case: created_at, user_id"]
**Primary keys:** [e.g., "Always 'id' (UUID or serial)"]

<!-- If using standard conventions (PostgreSQL: snake_case, MongoDB: camelCase), just write "Standard [database] conventions" -->

---

## Sensitive Data

[Fields containing PII or secrets - important for security agents]

**PII fields:**
- [table.field - e.g., "users.email"]
- [table.field - e.g., "users.phone_number"]
- [table.field - e.g., "payment_methods.card_last4"]

**Security notes:** [Any encryption/hashing - e.g., "users.password_hash uses bcrypt. Stripe tokens stored, not raw card data."]

<!-- If no sensitive data, write "No PII stored" -->
