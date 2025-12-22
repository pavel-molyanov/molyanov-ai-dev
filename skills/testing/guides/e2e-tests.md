# E2E Testing Guide

**For:** code-developer subagent when E2E tests are requested

## When E2E Tests Are Written

### Defined in Tech Spec
- Testing Requirements section specifies E2E needs
- Lists critical user journeys to test

### Agent Proposes E2E Tests
Agent should propose E2E tests when:
- Feature has **>5 tasks** (large, complex feature)
- Feature touches **critical user flows** (auth, payment, core business logic)
- Feature has **breaking changes** in API or UI
- User explicitly requests E2E tests

**When to propose:** After deploy to dev, before manual testing (new step in workflow)

## What to Test

### Top 3-5 Critical User Journeys
**Not everything** - only the most important flows:

**Examples:**
- User registration → email verification → first login
- User login → create order → checkout → payment → confirmation
- Admin creates content → publishes → user views content
- User uploads file → processes → downloads result
- Integration: external service webhook → system processes → user notified

### How to Identify Critical Flows
Defined during User Spec phase:
- What must work for business to function?
- What would cause major problems if broken?
- What do users do most frequently?

## Test Structure

### Full User Journey
Test complete flow from start to finish:
1. **Setup** - Clean database, create required data
2. **User actions** - Simulate real user interactions (UI or API)
3. **Verify results** - Check UI state, database, emails, side effects
4. **Cleanup** - Reset system to clean state

### E2E Test Phases

**Phase 1: Authentication**
- User registration/login
- Session creation
- Access to protected resources

**Phase 2: Core Actions**
- Main user actions (create, update, delete)
- Form submissions
- Navigation between pages

**Phase 3: Business Logic**
- Data processing
- Calculations
- Integrations with external services

**Phase 4: Verification**
- Success messages shown
- Data persisted correctly
- Emails/notifications sent
- UI updates reflect changes

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
- Payment processed (test mode)

## Test Execution

### Where Tests Run
- **Dev environment** - After deploy to dev
- Real database (separate test DB)
- Real integrations (test/sandbox mode)

### Test Speed
- E2E tests are **slow** (minutes, not seconds)
- Full browser automation takes time
- Only test critical paths, not every edge case

### When to Run
1. After deploy to dev
2. Before manual testing (saves time on manual checks)
3. Before merge to main (required for critical features)
4. Optionally on CI/CD for critical flows

## Tooling

### Choose Framework Based on Tech Stack

**Web Apps:**
- Playwright (recommended, modern, fast)
- Cypress (good for React/Vue)
- Selenium (older, more complex)

**API-First Apps:**
- Postman/Newman (API testing)
- REST Assured (Java)
- SuperTest (Node.js)

**Mobile Apps:**
- Appium (cross-platform)
- Detox (React Native)
- XCTest/Espresso (native)

### Configuration
- Use headless mode for CI/CD (faster)
- Use headed mode for debugging (see what's happening)
- Set reasonable timeouts (30s for slow operations)
- Take screenshots on failure (debugging)

## Key Principles

1. **Few tests, critical flows** - Only top 3-5 journeys, not every scenario
2. **Test behavior, not UI details** - Don't test exact button position, test functionality
3. **Resilient selectors** - Use data-testid or semantic selectors, not CSS classes
4. **Realistic scenarios** - Simulate real user behavior, not edge cases
5. **Independent tests** - Each test can run alone, no dependencies between tests
6. **Clean state** - Reset database/system between tests

## Coverage Guidelines

### ✅ Write E2E for:
- Complete user registration flow
- Payment/checkout process
- Critical business workflows (order creation, document processing)
- Authentication and authorization flows

### ❌ Don't write E2E for:
- Edge cases (covered by unit tests)
- Error handling (covered by integration tests)
- Every form field validation (covered by unit tests)
- Admin features rarely used (manual testing sufficient)

## Checklist Before Completion

- ✅ Top 3-5 critical flows identified (from Tech Spec or User Spec)
- ✅ Each flow tests complete user journey (start to finish)
- ✅ All tests pass on dev environment
- ✅ Tests verify UI, database, and external systems
- ✅ Tests are independent (can run in any order)
- ✅ Tests have proper cleanup (reset state)
- ✅ Screenshots/videos captured on failure (for debugging)

