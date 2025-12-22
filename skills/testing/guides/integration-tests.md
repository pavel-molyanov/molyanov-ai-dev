# Integration Testing Guide

**For:** code-developer subagent executing Integration Tests task

## When Integration Tests Are Written

- Defined in Tech Spec (Testing Requirements section)
- Created as separate task at end of feature
- Executed after all feature tasks are completed
- Before deploy to dev environment

## What to Test

### API Endpoints
All HTTP endpoints created/modified in this feature:
- POST requests (create operations)
- PUT/PATCH requests (update operations)
- DELETE requests (delete operations)
- GET requests with complex logic or filtering
- Authentication/authorization on protected endpoints

### Database Operations
All database interactions:
- Record creation (INSERT queries)
- Record updates (UPDATE queries)
- Record deletion (DELETE queries)
- Complex queries (JOIN, aggregation)
- Data integrity constraints
- Transaction handling

### External Service Integrations
All third-party service calls:
- Payment gateway integrations
- Email service (SendGrid, Mailgun, etc.)
- Cloud storage (S3, GCS, etc.)
- Webhook handlers
- External APIs (Stripe, Twilio, etc.)

## Test Structure

### Setup Phase
1. **Initialize test database** - Clean state for each test
2. **Create fixtures** - Set up test data (users, records, etc.)
3. **Configure test environment** - Set test API keys, URLs

### Test Phase
1. **Execute API call** - Make HTTP request to endpoint
2. **Verify response** - Check status code, response body
3. **Verify side effects** - Check database state, external calls

### Cleanup Phase
1. **Rollback or truncate** - Clean database after test
2. **Reset mocks** - Clear any mocked external services
3. **Close connections** - Clean up resources

## What to Verify

### API Response
- Correct HTTP status code (200, 201, 400, 404, etc.)
- Response body structure matches expected format
- Response data contains correct values
- Error messages are clear and actionable

### Database State
- Records created/updated/deleted as expected
- Related records updated (foreign keys, associations)
- Constraints enforced (unique, not null, etc.)
- No orphaned or corrupted data

### System Behavior
- Emails sent (check email queue or mock)
- Files uploaded (check storage or mock)
- Events triggered (webhooks, background jobs)
- Logs written correctly

## Coverage Requirements

Test **all endpoints and integrations** defined in Tech Spec:
- Every API endpoint in the feature
- Every database operation (create/update/delete)
- Every external service call

**Exception:** Read-only GET endpoints with trivial logic may be skipped if covered by E2E tests.

## Key Principles

1. **Real dependencies** - Use test database, not mocks (unlike unit tests)
2. **Isolated tests** - Each test runs independently
3. **Clean state** - Always start with known database state
4. **Fast cleanup** - Rollback transactions or truncate tables
5. **Mock external services** - Don't make real calls to payment/email (use test mode or mocks)
6. **Verify side effects** - Don't just check response, verify database and system state

## Test Database

### Setup
- Use separate test database (never production or dev database)
- Run migrations to set up schema
- Optionally seed with minimal required data

### Per-test
- Create fixtures for test data
- Execute test
- Rollback transaction OR truncate tables

### Best practices
- Use transactions for fast cleanup (rollback after each test)
- Avoid shared state between tests
- Keep fixture data minimal (only what's needed for test)

## External Service Mocking

For external services (Stripe, SendGrid, etc.):
- Use test/sandbox mode if available
- Mock HTTP calls to external APIs
- Verify mocked calls were made with correct parameters
- Don't make real API calls (slow, costs money, unreliable)

## Checklist Before Completion

- ✅ All endpoints from Tech Spec are tested
- ✅ All database operations are verified
- ✅ All external integrations are tested (mocked)
- ✅ All tests pass
- ✅ Tests run in reasonable time (seconds, not minutes)
- ✅ Test database cleanup works correctly
