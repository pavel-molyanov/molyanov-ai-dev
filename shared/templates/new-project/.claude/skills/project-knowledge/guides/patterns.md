# Code Patterns & Best Practices

This file defines coding standards for generating high-quality code. Use these patterns consistently across the project.

---

## Universal Patterns

### Naming Conventions
- **Functions/Methods**: Use verbs (`createUser`, `fetchData`, `validateEmail`)
- **Variables**: Use descriptive nouns (`userData`, `totalPrice`, `isActive`)
- **Constants**: Use UPPER_SNAKE_CASE (`API_KEY`, `MAX_RETRIES`)
- **Files**: Follow language convention (kebab-case for JS/TS, snake_case for Python)
- **Classes**: PascalCase (`UserService`, `PaymentProcessor`)
- Avoid abbreviations unless universally known (`id`, `url` are OK; `usr`, `calc` are NOT)

### Code Organization
- **One file = one responsibility** (UserService in one file, PaymentService in another)
- **Functions should be small**: < 50 lines; if larger, break into smaller functions
- **Limit nesting**: Maximum 3 levels deep; use early returns to reduce nesting
- **Group related code**: Put imports together, constants together, functions by feature
- **Dependency direction**: High-level modules should not depend on low-level details

### Dependency Management
- **Verify imports exist before using**: Read source files to confirm exports match expected usage
- **Check function signatures**: Ensure function/method signatures match how you're calling them
- **Use Context7 for library docs**: Get up-to-date API documentation for correct usage patterns
- **Prefer well-maintained packages**: Check npm/PyPI activity, security advisories, last update date
- **Pin major versions**: Use `^` (caret) for npm to allow patch updates, avoid breaking changes

### Separation of Concerns
Always extract from code into separate files:
- **Configuration**: `.env` file (API keys, URLs, timeouts, feature flags)
- **User-facing messages**: Separate file (`messages/`, `locales/`) for easy updates/translations
- **LLM Prompts**: Separate file (`prompts/`) for easy testing and improvement
- **Business logic**: Keep separate from framework code (routes, controllers)

### Security
- **NEVER hardcode secrets**: Use environment variables (`.env`) for all sensitive data
- **Always validate input**: Check types, formats, ranges before processing
- **Sanitize user data**: Before database operations, API calls, or displaying
- **Add to .gitignore**: `.env`, `*.key`, `credentials.json`, `secrets/`
- **Create .env.example**: With empty/dummy values for documentation

### Validation
- **Validate at API boundaries**: Check input in controllers, API routes, function entry points
- **Use schema validation libraries**: Zod, Yup, io-ts for runtime type checking and validation
- **Validate on BOTH frontend AND backend**: Defense in depth - never trust client-side validation alone
- **Sanitize before database operations**: Prevent SQL injection, NoSQL injection attacks
- **Fail fast with clear errors**: Return specific validation errors to help users fix input

### Error Handling
- **Always use try-catch**: For any operation that can fail (API calls, DB operations, file I/O)
- **Log with context**: Include user_id, action, resource_id, error message, stack trace
- **Don't swallow errors**: Always re-throw after logging (unless explicitly handling)
- **Fail fast**: Validate inputs early; throw errors immediately when invalid
- **User-friendly errors**: Show generic message to users, log details internally

### Logging
- **Use structured logging format**: JSON with consistent fields for easy parsing and searching
- **Include context in every log**: userId, action, resourceId, timestamp, error message
- **NEVER log sensitive data**: passwords, API keys, tokens, PII, credit card numbers
- **Use appropriate log levels**:
  - `debug`: Development-only details (verbose, disabled in production)
  - `info`: Key operations completed (user login, order created)
  - `warn`: Recoverable issues (retry succeeded, deprecated API used)
  - `error`: Failures requiring attention (API call failed, database error)
- **Log errors with stack traces**: Helps debug production issues quickly

### Testing
- **Test public APIs**: Focus on what users/other modules call, not internal implementation
- **Mock external services**: API calls, database, file system, time-dependent code
- **One test = one scenario**: Test happy path, error cases, edge cases separately
- **Descriptive test names**: `test_user_creation_fails_when_email_invalid` not `test_user_1`
- **Keep tests fast**: Unit tests < 100ms, integration tests < 1s

### Performance
- **Avoid N+1 queries**: Use batch operations, eager loading, or caching instead of loops with queries
- **Cache expensive computations**: Use memoization for functions, Redis for shared state across requests
- **Be mindful of bundle size**: Check impact of new dependencies on frontend load time
- **Prevent memory leaks**: Clean up event listeners, timers, intervals, subscriptions in cleanup functions
- **Use pagination for large datasets**: Don't load all records at once, implement cursor or offset pagination
- **Profile before optimizing**: Measure actual performance bottlenecks before making changes (don't guess)

### Code Quality
- **Write meaningful comments** (in English):
  - Focus on "why" and "what for" rather than obvious "what"
  - For complex logic, "what it does" is also valuable
  - **When to write comments:**
    - Complex business logic (explain WHY decisions were made)
    - Non-obvious architectural decisions or trade-offs
    - Important constraints, limitations, or gotchas
    - Edge cases that aren't immediately clear
    - Security-sensitive areas (sanitization, validation, auth)
  - **When NOT to write comments:**
    - Obvious code that's self-documenting
    - Every single function (only complex or public APIs)
    - Repeating TypeScript type information
  - **Format:** JSDoc/TSDoc for public APIs, inline comments for complex logic
  - When updating code → update comments too
- **DRY principle**: Extract repeated code into functions/modules
- **Readable > clever**: Clear code is better than short but cryptic code
- **Consistent formatting**: Use project's linter/formatter settings
- **No magic numbers**: Extract to named constants (`MAX_UPLOAD_SIZE` not `5242880`)

---

## Project-Specific Patterns

<!--
ADD PROJECT-SPECIFIC PATTERNS HERE:

1. Framework conventions (if using React/Django/FastAPI/etc):
   - Component structure, hooks usage, state management patterns

2. Domain naming (if specific terminology matters):
   - E-commerce: Order/Cart/Product vs Purchase/Basket/Item
   - Keep naming consistent with domain language

3. External integrations (if using Stripe/SendGrid/AWS/etc):
   - API usage patterns, webhook handling, error retry logic

4. Database patterns (if using SQL/NoSQL):
   - Transaction rules, migration strategy, query optimization

5. Team conventions (if relevant):
   - PR approval process, commit message format, testing requirements

Only add patterns that are SPECIFIC to this project. Don't add generic advice.
-->

