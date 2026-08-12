# Patterns & Conventions

Coding conventions, development workflow, and project-specific practices.

---

## Project-Specific Code Patterns

<!--
ADD PROJECT-SPECIFIC PATTERNS HERE:

1. Framework conventions (React hooks, Django patterns, FastAPI dependencies, etc.)
2. Domain naming (Order/Cart/Product vs Purchase/Basket/Item)
3. External integration patterns (Stripe webhooks, API retry logic, etc.)
4. Database patterns (transactions, query optimization, caching)

Only add patterns SPECIFIC to this project. Don't add generic advice.
Empty section is fine for simple projects.
-->

---

## Git Workflow

<!--
SCALING HINT: If this section grows beyond ~80 lines, extract to references/git-workflow.md.
-->

### Branch Structure

- **`main`** - Production-ready code (protected). Only merge from `dev` after full testing. Triggers production deployment.
- **`dev`** - Active development. All work happens here. Triggers staging deployment.

### Testing Requirements

- **On commit:** Run the smallest checks that cover the changed behavior. When there is no test
  subject, use the relevant build, lint, render, or other executable check.
- **On merge to dev:** Run the project's CI checks for the changed behavior.
- **On merge to main:** Run the project's required CI checks, including selected critical E2E flows when applicable.

### Security & Quality Gates

[Document the security and quality gates that are actually configured for this project.]

---

## Testing & Verification

<!--
SCALING HINT: If this section grows beyond ~60 lines, extract to references/testing.md.
This section stores proven verification approaches discovered during development.
Generic testing methodology lives in ~/.claude/skills/test-master/.
-->

### Test Infrastructure

[How to run tests: framework, runner, test DB setup, environment requirements.]

### Agent Verification Methods

[Proven methods for agent to verify features. Updated as new methods are discovered.]

<!-- Example:
### Telegram Bot
**Method:** Telegram MCP
**Setup:** Bot must be running, test user configured
**Discovered:** 2026-01-15, during messaging feature
-->

### User Verification Methods

[Methods that require user involvement.]

<!-- Example:
### Visual UI Check
**What to check:** Layout renders correctly on mobile
**How:** Open on phone, verify responsive layout
**Why agent can't:** No visual rendering capability
-->

---

## Business Rules

<!--
SCALING HINT: If this section grows beyond ~60 lines, extract to references/business-rules.md.
DELETE THIS SECTION if project has no complex domain logic (simple CRUD, CLI tool, utility).

Use for: multi-step workflows, state machines, calculation formulas, domain constraints.
-->

<!-- Example:
### Order Lifecycle
pending → paid → shipped → delivered
- Cancel: only if pending or paid
- Refund: full if pending, partial if paid, none after shipped

### Pricing
final_price = (subtotal - discount) * (1 + tax_rate) + shipping
- Discount applies BEFORE tax
- Free shipping if subtotal > $50
-->
