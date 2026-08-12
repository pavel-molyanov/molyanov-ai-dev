# Integration Testing Guide

**For:** an implementation agent writing integration tests

## Table of Contents
- [Scenario Patterns](#scenario-patterns)
- [Test Structure](#test-structure)
- [What to Verify](#what-to-verify)
- [External Service Mocking](#external-service-mocking)

## Scenario Patterns

Common cross-component scenarios include:
- an API request produces the required response and persisted state;
- a transaction preserves its integrity on success or failure;
- a query implements filtering, aggregation, authorization, or another meaningful contract;
- a handler records an event or invokes an external integration with required data.

### External Service Integrations
Relevant third-party service contracts:
- Payment gateway integrations
- Email service (SendGrid, Mailgun, etc.)
- Cloud storage (S3, GCS, etc.)
- Webhook handlers
- External APIs (Stripe, Twilio, etc.)

## Test Structure

### Setup Phase
1. **Initialize a separate test database** - Run migrations; never use production or dev data
2. **Create minimal fixtures** - Set up only the users, records, and relationships this test needs
3. **Configure the test environment** - Set test API keys and URLs

### Test Phase
1. **Execute API call** - Make HTTP request to endpoint
2. **Verify response** - Check status code, response body
3. **Verify side effects** - Check database state, external calls

### Cleanup Phase
1. **Rollback or truncate** - Prefer transactions for fast per-test cleanup
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

## External Service Mocking

For external services (Stripe, SendGrid, etc.):
- Use test/sandbox mode if available
- Mock HTTP calls to external APIs
- Verify mocked calls were made with correct parameters
- Don't make real API calls (slow, costs money, unreliable)
