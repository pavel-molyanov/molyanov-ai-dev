# E2E Testing Guide

**For:** an implementation agent executing a user request or user-spec

## Table of Contents
- [Journey Patterns](#journey-patterns)
- [Full-Journey Structure](#full-journey-structure)
- [What to Verify](#what-to-verify)
- [Test Execution](#test-execution)
- [Tooling](#tooling)

## Journey Patterns

Examples of complete user-facing journeys:
- User registration → email verification → first login
- User login → create order → checkout → payment → confirmation
- Admin creates content → publishes → user views content
- User uploads file → processes → downloads result
- Integration: external service webhook → system processes → user notified

## Full-Journey Structure

Test complete flow from start to finish:
1. **Setup** - Clean database, create required data
2. **User actions** - Simulate real user interactions (UI or API)
3. **Verify results** - Check UI state, database, emails, side effects
4. **Cleanup** - Reset system to clean state

## What to Verify

### UI State
- Correct pages displayed
- Elements visible/hidden as expected
- Forms populated with correct data
- Error messages shown appropriately
- Success confirmations displayed

### Backend State
- Database records created/updated correctly
- Related records updated (associations)
- Background jobs triggered
- Cache invalidated/updated

### External Systems
- Emails sent to correct recipients
- Webhooks triggered to external services
- Files uploaded to storage
- Payment outcome and required outgoing interaction are correct

## Test Execution

### Where Tests Run
- Local or CI environment during implementation
- Isolated test database or other controlled state
- Sandbox modes or controlled test doubles for payments, email, and third-party APIs
- A deployed dev/staging environment only for a separate short smoke check when required

### Test Speed
- E2E tests are **slow** (minutes, not seconds)
- Full browser automation takes time

### When to Run
1. During implementation after the protected behavior exists
2. In CI before merge for the critical flows the project selects
3. Locally while diagnosing failures when practical

## Tooling

Default: Playwright. If the project already has an E2E tool, use it.

### Configuration
- Use headless mode for CI/CD (faster)
- Use headed mode for debugging (see what's happening)
- Set timeouts from the project's existing behavior and the operation under test
- Use semantic or `data-testid` selectors rather than CSS classes or exact visual positions
- Capture screenshots or videos on failure for debugging
