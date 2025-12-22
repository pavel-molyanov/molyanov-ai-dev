# Documentation Examples: Good vs Bad

This file provides concrete examples of good vs bad documentation to illustrate quality principles.

---

## Example 1: Tech Stack Documentation

### ❌ BAD (bloated, obvious, generic)

```markdown
## Tech Stack

### Next.js
Next.js is a React framework for building web applications. It was created by Vercel and provides many powerful features out of the box.

Key features of Next.js include:
- **Server-side rendering (SSR)**: Renders pages on the server for better SEO
- **Static site generation (SSG)**: Pre-renders pages at build time
- **API routes**: Built-in API endpoint support
- **Image optimization**: Automatic image optimization
- **File-based routing**: Pages are created by adding files to the pages/ directory

To install Next.js, run:
```bash
npm install next react react-dom
```

To create a new page, simply create a file in the `pages/` directory:
```typescript
// pages/about.tsx
export default function About() {
  return <div>About Page</div>
}
```

### React
React is a JavaScript library for building user interfaces. It was created by Facebook and is maintained by Meta and a community of developers.

### TypeScript
TypeScript is a typed superset of JavaScript that compiles to plain JavaScript...
```

**Problems:**
- Explains what Next.js is (generic knowledge)
- Lists obvious Next.js features
- Shows installation commands (obvious)
- Includes code examples (should reference actual code)
- Repeats for every tech (React, TypeScript, etc.)
- ~300 words of bloat

### ✅ GOOD (concise, project-specific, focused)

```markdown
## Tech Stack

- **Next.js 14.0.4** - Chosen for SSR (SEO-critical product pages) and API routes
- **React 18** - UI framework
- **TypeScript** - Type safety for large codebase (10+ developers)
- **Prisma** - ORM for type-safe database access

See package structure in [src/](src/) and configuration in [next.config.js](next.config.js).

**Key integration:** Next.js API routes handle authentication middleware (see [middleware.ts:15-45](src/middleware.ts#L15-L45))
```

**Why it's good:**
- Versions specified
- WHY chosen (project-specific reasons)
- No generic explanations
- References actual code
- ~60 words, all meaningful

---

## Example 2: Authentication Documentation

### ❌ BAD (code examples, obvious)

```markdown
## Authentication

We use JWT (JSON Web Tokens) for authentication. JWT is a compact, URL-safe means of representing claims to be transferred between two parties.

### How JWT Works
1. User logs in with credentials
2. Server validates credentials
3. Server generates a JWT token
4. Client stores token
5. Client sends token with each request

### Creating a Token

Here's how we create JWT tokens:

```typescript
import jwt from 'jsonwebtoken';

const token = jwt.sign(
  { userId: user.id, email: user.email },
  process.env.JWT_SECRET,
  { expiresIn: '7d' }
);
```

### Verifying a Token

To verify a token:

```typescript
import jwt from 'jsonwebtoken';

try {
  const decoded = jwt.verify(token, process.env.JWT_SECRET);
  console.log('User ID:', decoded.userId);
} catch (error) {
  console.log('Invalid token');
}
```

### Environment Variables

You need to set the following environment variables:
- `JWT_SECRET` - Secret key for signing tokens
```

**Problems:**
- Explains what JWT is (generic)
- Shows how JWT works (obvious)
- Includes code examples (should reference actual files)
- Shows obvious environment variable usage
- ~200 words of bloat

### ✅ GOOD (concise, file references)

```markdown
## Authentication

JWT tokens with 7-day expiry. Token generation and verification in [src/auth/jwt.ts](src/auth/jwt.ts).

**Security considerations:**
- Tokens include only userId (not email or sensitive data)
- Refresh token rotation implemented (see [auth/refresh.ts:34-56](src/auth/refresh.ts#L34-L56))
- Token blacklist for logout (Redis-based, TTL matches token expiry)

**Environment variables:** `JWT_SECRET` (required), `REFRESH_TOKEN_SECRET` (required)

See deployment.md for environment variable setup.
```

**Why it's good:**
- States what, not how (how is in code)
- Project-specific security decisions
- References actual implementation files
- Minimal environment variable info (details in deployment.md)
- ~60 words, all valuable

---

## Example 3: Database Schema

### ❌ BAD (full schema dump, code duplication)

```markdown
## Database Schema

### Users Table

```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  first_name VARCHAR(100),
  last_name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

Fields:
- `id`: Unique identifier for the user (UUID)
- `email`: User's email address (required, must be unique)
- `password_hash`: Hashed password using bcrypt
- `first_name`: User's first name (optional)
- `last_name`: User's last name (optional)
- `created_at`: Timestamp when user was created
- `updated_at`: Timestamp when user was last updated

### Orders Table

```sql
CREATE TABLE orders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  total_amount DECIMAL(10, 2) NOT NULL,
  status VARCHAR(50) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

Fields:
- `id`: Unique identifier for the order
- `user_id`: Foreign key to users table
- `total_amount`: Total order amount in dollars
- `status`: Order status (pending, completed, cancelled)
- `created_at`: Timestamp when order was created

[... continues for 10 more tables ...]
```

**Problems:**
- Full SQL schema (duplicates migration files)
- Explains every field (obvious from schema)
- Massive bloat (~2000 words for full schema)
- Will become outdated quickly
- No project-specific insights

### ✅ GOOD (overview, references, insights)

```markdown
## Database

PostgreSQL 15 with Prisma ORM. Schema in [prisma/schema.prisma](prisma/schema.prisma).

**Key entities:**
- **Users** - Authentication and profile data
- **Orders** - Purchase history with payment status
- **Products** - Inventory with pricing and availability
- **Reviews** - User reviews (soft delete for moderation)

**Important relationships:**
- Orders → Users (CASCADE delete for GDPR compliance)
- Reviews → Users (RESTRICT delete - preserve reviews of deleted users)
- OrderItems → Products (RESTRICT delete - maintain historical data)

**Migration strategy:** Prisma migrations. Run `npx prisma migrate dev` locally. Production migrations automated via CI/CD. See [.github/workflows/deploy.yml:45-52](.github/workflows/deploy.yml#L45-L52).

**Sensitive data:** Password hashes (bcrypt), payment tokens (encrypted at rest). See patterns.md for security practices.
```

**Why it's good:**
- High-level overview (details in schema file)
- Project-specific relationship decisions (WHY cascade/restrict)
- Migration process explained
- References actual files
- ~120 words vs ~2000 words

---

## Example 4: API Integration

### ❌ BAD (tutorial-style, code examples)

```markdown
## Stripe Integration

Stripe is a payment processing platform. We use it to handle credit card payments.

### Setup

First, install the Stripe SDK:
```bash
npm install stripe
```

Then, initialize Stripe in your code:
```typescript
import Stripe from 'stripe';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY, {
  apiVersion: '2023-10-16',
});
```

### Creating a Payment Intent

To create a payment intent:
```typescript
const paymentIntent = await stripe.paymentIntents.create({
  amount: 2000, // $20.00
  currency: 'usd',
  payment_method_types: ['card'],
});
```

### Webhook Handling

Stripe sends webhooks for payment events. Here's how to handle them:

```typescript
app.post('/webhook', async (req, res) => {
  const sig = req.headers['stripe-signature'];

  try {
    const event = stripe.webhooks.constructEvent(
      req.body,
      sig,
      process.env.STRIPE_WEBHOOK_SECRET
    );

    if (event.type === 'payment_intent.succeeded') {
      // Handle successful payment
    }
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
});
```
```

**Problems:**
- Installation commands (obvious)
- Generic Stripe usage (tutorial content)
- Code examples (should reference actual code)
- No project-specific context
- ~200 words of bloat

### ✅ GOOD (project-specific, focused)

```markdown
## Stripe Integration

Stripe for payment processing. API version 2023-10-16 (pinned for stability).

**Implementation:**
- Payment intents in [api/payments/create.ts](src/api/payments/create.ts)
- Webhook handling in [api/webhooks/stripe.ts](src/api/webhooks/stripe.ts)
- Subscription management in [services/subscriptions.ts](src/services/subscriptions.ts)

**Project-specific setup:**
- Multi-currency support (USD, EUR, GBP)
- Payment retry logic (3 attempts with exponential backoff)
- Webhook signature verification required (see security in patterns.md)

**Environment variables:** `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET` (see deployment.md)

**Important:** Stripe test mode in development, live mode in production. Mode determined by API key prefix.
```

**Why it's good:**
- References implementation files
- Project-specific details (multi-currency, retry logic)
- Security considerations
- No code examples (code is in referenced files)
- ~100 words, all project-specific

---

## Example 5: Code Comments

### ❌ BAD (obvious, repeats code)

```typescript
// Get user by ID
function getUserById(id: string) {
  return db.users.findOne({ id });
}

// Calculate the total
function calculateTotal(items: Item[]) {
  // Initialize sum to 0
  let sum = 0;

  // Loop through items
  for (const item of items) {
    // Add price to sum
    sum += item.price;
  }

  // Return the sum
  return sum;
}

// Validate email address
function validateEmail(email: string): boolean {
  // Use regex to check if email is valid
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
```

**Problems:**
- Comments repeat what code says
- No value added
- Obvious operations explained
- Clutters code

### ✅ GOOD (explains WHY, non-obvious details)

```typescript
// No comment needed - function name is self-explanatory
function getUserById(id: string) {
  return db.users.findOne({ id });
}

// No comment needed - logic is obvious
function calculateTotal(items: Item[]) {
  return items.reduce((sum, item) => sum + item.price, 0);
}

/**
 * Basic email validation for user signup.
 *
 * LIMITATION: This does NOT verify email deliverability, only format.
 * Real verification happens via email confirmation link.
 *
 * This regex intentionally allows some invalid formats (e.g., consecutive dots)
 * to reduce false negatives. Better to send confirmation email to invalid
 * address than block valid user from signing up.
 */
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Calculate shipping cost with regional pricing.
 *
 * IMPORTANT: Pricing varies by region due to carrier contracts:
 * - US: USPS rates with 15% corporate discount
 * - EU: DHL rates, includes VAT
 * - Asia: FedEx rates, customs duties NOT included (customer pays)
 *
 * Historical note: Changed from flat-rate to regional in Q2 2024
 * due to 30% increase in international shipping costs.
 *
 * See pricing tables in database.shipping_rates
 */
function calculateShipping(destination: string, weight: number): number {
  const region = getRegion(destination);
  const rate = SHIPPING_RATES[region];

  // Weight in kg, rates in $/kg
  return weight * rate.perKg + rate.baseCharge;
}
```

**Why it's good:**
- Simple functions have no comments (self-documenting)
- Complex function explains WHY and important considerations
- Documents limitations and gotchas
- Provides business context (regional pricing differences)
- Explains non-obvious decisions

---

## Example 6: Deployment Documentation

### ❌ BAD (includes secrets, tutorial-style)

```markdown
## Deployment

### Vercel Setup

1. Go to vercel.com
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables:
   - `DATABASE_URL=postgresql://user:password@db.example.com:5432/mydb`
   - `JWT_SECRET=my-super-secret-key-12345`
   - `STRIPE_SECRET_KEY=sk_live_abc123def456`
5. Click "Deploy"

### SSH Access

SSH into the server:
```bash
ssh admin@123.456.789.0
Password: MySecretPassword123
```

### Manual Deployment

If automatic deployment fails:
```bash
git pull origin main
npm install
npm run build
pm2 restart app
```
```

**Problems:**
- ❌ Actual secrets in documentation
- ❌ Passwords visible
- ❌ Tutorial-style instructions
- ❌ IP addresses and credentials exposed
- **SECURITY RISK**

### ✅ GOOD (no secrets, focused)

```markdown
## Deployment

Vercel (production), automatic deployment from `main` branch.

**Environment variables:**
- `DATABASE_URL` - PostgreSQL connection string (required)
- `JWT_SECRET` - Token signing key (required, min 32 chars)
- `STRIPE_SECRET_KEY` - Stripe API key (required, use test key for staging)
- `REDIS_URL` - Cache connection (optional, falls back to memory cache)

See `.env.example` for local development setup. Production secrets in Vercel dashboard (Settings → Environment Variables).

**Deployment flow:**
1. Merge to `main` → Vercel auto-deploys
2. Database migrations run automatically ([deploy.yml:45-52](.github/workflows/deploy.yml#L45-L52))
3. Health check at `/api/health` must pass before traffic switches

**Rollback:** Vercel dashboard → Deployments → Select previous deployment → Promote. Database rollback requires manual migration reversal.

**SSH access:** Not applicable (Vercel serverless). Logs in Vercel dashboard.
```

**Why it's good:**
- Environment variable NAMES only (no values)
- References where to set secrets securely
- Deployment process explained
- No actual credentials
- Project-specific rollback procedure

---

## Example 7: patterns.md Structure

### ❌ BAD (removes Universal Patterns, duplicates in other files)

**In patterns.md:**
```markdown
## Patterns

### Framework-Specific Patterns
- Use React hooks for state management
- Components should be in PascalCase
- Use TypeScript strict mode

### Database Patterns
- Use Prisma migrations
- Always use transactions for multi-step operations
```

**In architecture.md:**
```markdown
## Coding Standards

All code should follow these rules:
- Functions should be small (< 50 lines)
- Use descriptive variable names
- Always validate user input
- Use try-catch for error handling
- Never hardcode secrets
- Write tests for all features
```

**Problems:**
- ❌ Removed Universal Patterns section (lost common best practices)
- ❌ Duplicated generic coding standards in architecture.md
- ❌ Generic advice spread across multiple files
- ❌ No single source of truth for code quality standards

### ✅ GOOD (preserves Universal Patterns, project-specific additions)

**In patterns.md:**
```markdown
## Universal Patterns

### Naming Conventions
- **Functions/Methods**: Use verbs (`createUser`, `fetchData`)
- **Variables**: Use descriptive nouns (`userData`, `totalPrice`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_KEY`, `MAX_RETRIES`)
[... full Universal Patterns section from template ...]

## Project-Specific Patterns

### React Component Patterns
- Custom hooks prefix: `use` (e.g., `useAuth`, `usePayments`)
- Component files include `.test.tsx` alongside in same directory
- Props interfaces suffix: `Props` (e.g., `UserCardProps`)
- See [UserCard.tsx](src/components/UserCard.tsx) for reference implementation

### Database Transaction Rules
- All payment operations require Prisma transaction (see [payments.service.ts:45-78](src/services/payments.service.ts#L45-L78))
- Timeout: 5 seconds (balance between data consistency and user experience)
- Retry policy: No automatic retry for transactions (idempotency concerns)
```

**In architecture.md:**
```markdown
## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety for large codebase
- **Prisma** - ORM for type-safe database access

See patterns.md for coding standards and conventions.
```

**Why it's good:**
- ✅ Universal Patterns preserved (template content intact)
- ✅ Project-Specific Patterns add value (React hooks naming, transaction rules)
- ✅ architecture.md references patterns.md instead of duplicating
- ✅ Single source of truth for code quality (patterns.md)
- ✅ File references instead of code examples

---

## Key Takeaways

### Bad Documentation:
- Explains what frameworks/libraries are
- Includes code examples
- Shows installation/setup commands
- Repeats obvious information
- Tutorial-style content
- Contains actual secrets

### Good Documentation:
- Explains WHY choices were made
- References actual code files
- Project-specific decisions and trade-offs
- Concise and focused
- No secrets (names only, values elsewhere)
- Assumes reader is experienced developer

### Rule of Thumb:
If you can find it in official framework docs → Don't document it
If it's specific to THIS project → Document it concisely
If it's code → Reference the file, don't copy it
If it's about a specific function → Use code comments, not docs

### Special Exception - patterns.md:
✅ Universal Patterns section is intentional generic content from template
✅ This section ensures consistent code quality across all projects
❌ DO NOT remove Universal Patterns during documentation audit
✅ Only add project-specific patterns to Project-Specific Patterns section
