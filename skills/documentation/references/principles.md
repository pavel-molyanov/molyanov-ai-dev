# Documentation Quality Principles

This file defines what makes good project documentation and provides criteria for auditing documentation quality.

## Core Principle: Concise and Project-Specific

Documentation should be **concise** and contain **only project-specific information**. Assume the reader is an experienced developer who knows common frameworks and patterns. Focus on what makes THIS project unique.

**Exception:** `patterns.md` has a special structure - it contains both:
- **Universal Patterns** section (from template `~/.claude/shared/templates/new-project/.claude/skills/project-knowledge/guides/patterns.md`) - contains common best practices shared across all projects. This content is intentional and should NOT be removed.
- **Project-Specific Patterns** section - custom patterns for this specific project

---

## What NOT to Write

### ❌ Obvious Information

**Don't document things everyone knows:**
- "npm install installs dependencies"
- "git commit creates a commit"
- "React is a UI library"
- "TypeScript adds types to JavaScript"

**Why:** Claude Code and developers already know this. It wastes context and dilutes important information.

**Audit check:** Remove any sentences that explain basic commands or common knowledge.

### ❌ Code Examples in Documentation

**Don't copy-paste code into documentation:**
- ❌ Showing how to import a library
- ❌ Demonstrating basic function usage
- ❌ Example API calls with dummy data
- ❌ Configuration file contents

**Why:**
- Code in docs gets outdated quickly
- Duplicates information from source code
- Bloats context window
- Makes docs harder to maintain

**Instead:** Reference actual code files with line numbers
- ✅ "See authentication logic in [src/auth/jwt.ts:45-67](src/auth/jwt.ts#L45-L67)"
- ✅ "Token generation in [auth/tokens.ts](src/auth/tokens.ts)"
- ✅ "Database schema in [prisma/schema.prisma](prisma/schema.prisma)"

**Audit check:** Find code blocks and replace with file references.

### ❌ Generic Framework/Library Explanations

**Don't explain how frameworks work:**
- ❌ "Express is a web framework that handles HTTP requests..."
- ❌ "React components can use hooks like useState and useEffect..."
- ❌ "PostgreSQL is a relational database..."

**Why:** This is generic knowledge, not project-specific.

**Instead:** Explain WHY you chose it and HOW you use it
- ✅ "Express chosen for middleware flexibility. See auth middleware in [middleware/auth.ts](src/middleware/auth.ts)"
- ✅ "PostgreSQL for ACID compliance required by financial transactions"

**Exception - patterns.md Universal Patterns:**
- ✅ The Universal Patterns section in `patterns.md` contains generic best practices (naming conventions, code organization, security, etc.)
- ✅ This content is from the project template and is intentionally generic - it ensures consistent code quality across all projects
- ✅ DO NOT flag Universal Patterns as "generic content to be removed"
- ❌ Only audit the Project-Specific Patterns section for generic content

**Audit check:** Remove framework/library explanations unless they explain project-specific decisions. Exception: Universal Patterns section in patterns.md should be preserved.

### ❌ Duplication Between Files

**Don't repeat information across multiple files:**
- Tech stack mentioned in both architecture.md and patterns.md
- Environment variables listed in both deployment.md and database.md
- Same integration described in multiple places

**Why:** Creates maintenance burden and inconsistency risk.

**Instead:** Put information in ONE place and cross-reference
- ✅ "See deployment.md for environment variables"
- ✅ "Tech stack defined in architecture.md"

**Audit check:** Find duplicate information and consolidate or cross-reference.

### ❌ Function-Specific Implementation Details

**Don't document how individual functions work in project docs:**
- ❌ "The calculateDiscount function takes a price and percentage, then multiplies..."
- ❌ "getUserById first checks cache, then queries database..."

**Why:** This level of detail belongs in code comments near the function, not in project documentation.

**Instead:**
- Document general patterns in documentation
- Document specific functions in code comments
- Reference files, not individual functions (unless architecturally significant)

**Audit check:** Move function-specific details to code comment recommendations.

---

## What TO Write

### ✅ Project-Specific Decisions

**Document WHY decisions were made:**
- Why this tech stack over alternatives
- Why this architecture pattern
- Trade-offs considered
- Project-specific constraints

**Examples:**
- "Next.js chosen for SSR requirements (SEO-critical content)"
- "PostgreSQL over MongoDB because we need ACID transactions for payments"
- "Monorepo structure for code sharing between web and mobile apps"

### ✅ Architectural Decisions and Trade-offs

**Document non-obvious design choices:**
- System architecture rationale
- Performance trade-offs
- Security considerations
- Scalability decisions

**Examples:**
- "Caching layer added to reduce database load (10k+ concurrent users expected)"
- "Microservices avoided to reduce operational complexity (small team)"

### ✅ Domain-Specific Information

**Document business logic and domain concepts:**
- Domain terminology and glossary
- Business rules unique to project
- Workflow and process descriptions
- Compliance requirements

**Examples:**
- "Invoice 'finalization' means it cannot be edited and payment is due"
- "User roles: Admin (full access), Manager (read + approve), Viewer (read-only)"

### ✅ Integration Points

**Document external dependencies:**
- Third-party APIs and how they're used
- External services (Stripe, Auth0, etc.)
- Integration architecture
- Authentication mechanisms

**Examples:**
- "Stripe integration for payments. Webhook handling in [api/webhooks/stripe.ts](src/api/webhooks/stripe.ts)"
- "Auth0 for SSO. Configuration in [auth/auth0.config.ts](src/auth/auth0.config.ts)"

### ✅ File References Instead of Code

**Point to code, don't duplicate it:**
- Link to specific files
- Link to specific line ranges when helpful
- Reference directories for related code
- Use markdown links for IDE clickability

**Format:**
- `[filename.ts](path/to/filename.ts)` - entire file
- `[filename.ts:42](path/to/filename.ts#L42)` - specific line
- `[filename.ts:42-51](path/to/filename.ts#L42-L51)` - line range
- `[src/utils/](src/utils/)` - directory

---

## Code Comments as Documentation

Code comments are PART of documentation strategy. Use them for function-specific details that don't belong in project docs.

### When to Write Code Comments

**Complex business logic:**
```typescript
/**
 * Calculate shipping cost with regional pricing.
 *
 * IMPORTANT: Pricing varies by region due to carrier contracts:
 * - US: USPS rates with 15% discount
 * - EU: DHL rates, VAT included
 * - Asia: FedEx rates, customs duties NOT included
 *
 * See pricing tables in database.shipping_rates
 */
function calculateShipping(order: Order): number {
  // ...
}
```

**Non-obvious architectural decisions:**
```typescript
/**
 * Cache user permissions for 5 minutes to reduce database load.
 *
 * Why 5 minutes: Balance between performance and permission updates.
 * Shorter cache caused DB overload during peak hours.
 * Longer cache delayed permission revocations (security risk).
 *
 * Cache invalidation: Manual invalidation on permission changes
 * via invalidateUserPermissions() in auth service.
 */
const PERMISSION_CACHE_TTL = 5 * 60 * 1000;
```

**Important constraints or limitations:**
```typescript
/**
 * LIMITATION: This function does NOT handle paginated results.
 * API returns max 100 items per request.
 *
 * For large datasets, use fetchAllItemsPaginated() instead.
 * See documentation in [docs/api-pagination.md](docs/api-pagination.md)
 */
function fetchItems(query: string): Promise<Item[]> {
  // ...
}
```

**Edge cases and gotchas:**
```typescript
/**
 * GOTCHA: Date comparison uses UTC timestamps, not local time.
 *
 * This caused bugs in #123 where timezone differences resulted
 * in off-by-one-day errors for international users.
 *
 * Always use toISOString() before comparing dates.
 */
function isDateBefore(date1: Date, date2: Date): boolean {
  return date1.toISOString() < date2.toISOString();
}
```

**Security-sensitive areas:**
```typescript
/**
 * SECURITY: Input sanitization for XSS prevention.
 *
 * This function removes ALL HTML tags and escapes special characters.
 * Used for user-generated content displayed in admin panel.
 *
 * DO NOT use for rich text fields (use sanitizeRichText instead).
 */
function sanitizeUserInput(input: string): string {
  // ...
}
```

### When NOT to Write Code Comments

**Obvious code (self-documenting):**
```typescript
// ❌ BAD: Comment repeats what code says
// Get user by ID
function getUserById(id: string) {
  return db.users.findOne({ id });
}

// ✅ GOOD: No comment needed, code is clear
function getUserById(id: string) {
  return db.users.findOne({ id });
}
```

**Every single function:**
```typescript
// ❌ BAD: Commenting every simple function
/**
 * Add two numbers together
 * @param a First number
 * @param b Second number
 * @returns Sum of a and b
 */
function add(a: number, b: number): number {
  return a + b;
}

// ✅ GOOD: No comment for trivial functions
function add(a: number, b: number): number {
  return a + b;
}
```

**Repeating type information:**
```typescript
// ❌ BAD: Comment repeats TypeScript types
/**
 * @param userId The user ID (string)
 * @param options Options object
 * @returns Promise of User object
 */
function getUser(userId: string, options: Options): Promise<User> {
  // ...
}

// ✅ GOOD: Types are already clear from TypeScript
function getUser(userId: string, options: Options): Promise<User> {
  // ...
}
```

### Code Comment Quality Guidelines

**Explain WHY, not WHAT:**
- ❌ "This function calls the API" (WHAT)
- ✅ "API call retries 3x because of intermittent network issues in production" (WHY)

**Keep comments up-to-date:**
- Update comments when code changes
- Remove outdated comments immediately
- Outdated comments are worse than no comments

**Be specific and actionable:**
- ❌ "Be careful with this function"
- ✅ "This function modifies input array in-place. Clone before calling if original needed."

**Use JSDoc/TSDoc for API documentation:**
- Use proper JSDoc format for public APIs
- Include `@param`, `@returns`, `@throws` where helpful
- Keep private/internal functions comment-free unless complex

---

## Quality Indicators

### Good Documentation Checklist

- ✅ Concise and focused (no bloat)
- ✅ Project-specific information only
- ✅ Links to code instead of copying code
- ✅ Consistent terminology across files
- ✅ Up-to-date with current codebase
- ✅ No placeholder text (e.g., `[Project Name]`)
- ✅ No duplication between files
- ✅ References external docs for frameworks/libraries
- ✅ Explains WHY, not just WHAT

### Bad Documentation Indicators

- ❌ Long and bloated (>5KB per file without good reason)
- ❌ Generic framework explanations
- ❌ Code examples duplicating source
- ❌ Outdated information
- ❌ Obvious things Claude already knows
- ❌ Placeholder or template text still present
- ❌ Inconsistent terminology
- ❌ Function-level details (belongs in code comments)

---

## Audit Criteria

When auditing documentation, check for:

### 1. Code Examples
- Find all code blocks (````)
- Replace with file references (code examples not allowed in documentation)

### 2. Obvious Content
- Look for explanations of basic commands
- Find generic framework/library descriptions
- Remove unless project-specific context added
- **Exception:** Universal Patterns section in patterns.md is intentionally generic and should be preserved

### 3. Bloat
- Check file sizes (>3-5KB might indicate bloat)
- Find overly detailed sections
- Condense or remove unnecessary details

### 4. Duplication
- Compare similar information across files
- Find repeated tech stack mentions, environment variables, etc.
- Consolidate or cross-reference

### 5. Placeholder Text
- Search for `[`, `TODO`, `TBD`, `...`
- Fill in or remove placeholder content

### 6. Function-Specific Details
- Find documentation about individual functions
- Suggest moving to code comments
- Keep only architecturally significant functions

### 7. Consistency
- Check if same items have different names
- Verify version numbers match across files
- Standardize terminology

### 8. Outdated Information
- Compare with current codebase
- Check if mentioned files/functions still exist
- Verify tech stack versions are current
- Remove or update outdated content

---

## When in Doubt

Use these decision rules:

**Can it fit in existing files?**
- → Don't create a new file

**Is it obvious?**
- → Don't document it

**Is it code?**
- → Link to code, don't copy

**Is it generic framework knowledge?**
- → Don't document, Claude knows it

**Is it complex business logic about a specific function?**
- → Use code comments, not documentation

**Is it an important architectural decision?**
- → Document it concisely with rationale
