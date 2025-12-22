---
name: testing
description: |
  Testing strategy: smoke, unit, integration, E2E. When to write which tests.

  AUTOMATIC TRIGGER - Invoke when user says ANY of:
  "напиши тесты", "проанализируй тесты"

  Do NOT use for: writing specific test code (answer directly), running tests (answer directly)
---

# Testing Strategy Skill

## Overview

This skill provides comprehensive guidance on testing in AI-First development methodology. It covers all test types from smoke tests to E2E tests, when to write them, and how to execute them effectively.

**Test Pyramid:**
```
        /\
       /E2E\        ← Few (3-5 critical flows)
      /------\
     /Integr.\      ← Some (all endpoints + DB)
    /----------\
   /   Unit     \   ← Many (all business logic)
  /--------------\
 /    Smoke      \  ← Minimal (1-2 basic tests)
/------------------\
```

**Use this skill when:**
- Planning testing strategy for a feature
- Writing tests during task development
- Deciding which test type to use
- Setting up testing infrastructure
- Creating Tech Spec testing requirements

---

## When to Use Each Test Type

### Smoke Tests
**Purpose:** Verify basic project setup works.

**Use for:**
- Testing framework is configured
- Environment variables accessible
- Basic imports work
- Infrastructure is functional

**Written:** During infrastructure setup (once per project)

**Details:** [guides/smoke-tests.md](guides/smoke-tests.md)

---

### Unit Tests
**Purpose:** Test business logic in isolation.

**Use for:**
- Functions with calculations, validations, transformations
- Decision-making logic (if/else, switch)
- Data processing and formatting
- Error handling logic

**Written:** By code-developer during each task (immediately after code)

**Skip for:** Simple getters/setters, one-line changes, trivial updates

**Details:** [guides/unit-tests.md](guides/unit-tests.md)

---

### Integration Tests
**Purpose:** Test API endpoints, database, and external services.

**Use for:**
- All API endpoints (POST/PUT/DELETE especially)
- Database operations (create/update/delete)
- External service integrations (payments, email, webhooks)

**Written:** As separate task at end of feature (if defined in Tech Spec)

**Details:** [guides/integration-tests.md](guides/integration-tests.md)

---

### E2E Tests
**Purpose:** Test critical user journeys end-to-end.

**Use for:**
- Top 3-5 most critical user flows
- Large features (>5 tasks)
- Critical business processes (auth, payment, core features)

**Written:** After deploy to dev, before manual testing (if proposed/requested)

**Details:** [guides/e2e-tests.md](guides/e2e-tests.md)

---

## Testing Workflow

### During Task Development

1. **code-developer** implements functionality
2. **code-developer** writes unit tests immediately
3. **code-developer** runs tests
4. If tests fail → fix and repeat
5. Return to orchestrator with passing tests

**Key:** Tests written in same session as code, not deferred.

### After Task Completion

1. **orchestrator** runs new tests (verification)
2. **orchestrator** runs all tests (regression check)
3. If regression fails → analyze and fix
4. Proceed to next task

### End of Feature

1. Execute integration tests task (if in Tech Spec)
2. Deploy to dev environment
3. Propose E2E tests (if appropriate)
4. Run E2E tests (if approved)
5. Manual testing

---

## Decision Framework

### Should I write unit tests for this?

**YES if:**
- Function has business logic
- Function makes decisions
- Function transforms data
- Function handles errors
- Task specifies testing

**NO if:**
- Simple getter/setter
- One-line text change
- Trivial config update
- No code written (research/docs)

### Should I write integration tests?

**YES if:**
- Tech Spec specifies integration tests
- Feature has API endpoints
- Feature interacts with database
- Feature calls external services

**NO if:**
- Tech Spec says "None"
- Feature is purely client-side
- Already covered by E2E tests

### Should I write E2E tests?

**YES if:**
- Feature has >5 tasks
- Feature touches critical flows
- Feature has breaking changes
- User explicitly requests
- Tech Spec specifies E2E tests

**NO if:**
- Small feature (<3 tasks)
- Non-critical functionality
- Well covered by unit + integration tests
- Time/cost constraints

---

## Test Coverage Guidelines

### What Must Be Tested

**Unit Tests (all tasks):**
- All business logic functions
- All calculations and validations
- All data transformations
- All decision-making code
- Exception: Simple getters, one-line changes

**Integration Tests (end of feature):**
- All API endpoints (POST/PUT/DELETE priority)
- All database operations
- All external service integrations

**E2E Tests (critical features only):**
- Top 3-5 critical user journeys
- Defined during User Spec phase
- Examples: auth, payment, core business process

---

## Tech Spec Requirements

When creating Tech Spec, agent must define testing needs:

```markdown
## Testing Requirements

**Integration Tests:** [Required/None]
- List endpoints/integrations to test
- OR: None (if not applicable)

**E2E Tests:** [Required/None]
- List critical user journeys for E2E
- OR: None (if small feature)
```

If not needed, write "None". If needed, specify what to test.

---

## Key Testing Principles

1. **Write tests immediately** - Don't defer to later
2. **Test behavior, not implementation** - Focus on what, not how
3. **Keep tests fast** - Unit: milliseconds, Integration: seconds, E2E: minutes
4. **Isolate tests** - Mock external dependencies in unit tests
5. **One concern per test** - Each test validates one thing
6. **Clear test names** - Describe what's tested and expected outcome
7. **Independent tests** - Tests don't depend on each other
8. **Clean state** - Always start with known database state

---

## Regression Testing

**Purpose:** Ensure new code doesn't break existing functionality.

**Process when regression tests fail:**
1. **Analyze cause:**
   - Bug in new code → code-developer fixes
   - Test is outdated → update test
   - Behavior changed intentionally → ask user, update tests, document

2. **Re-run regression check**

3. **Proceed only when all pass**

---

## Test Execution Timeline

```
Task Start
    ↓
Write Code
    ↓
Write Unit Tests ← Immediate
    ↓
Run Unit Tests
    ↓
Task Complete
    ↓
Run Regression Tests
    ↓
[Next Task...]
    ↓
Feature Complete
    ↓
Run Integration Tests ← Separate task
    ↓
Deploy to Dev
    ↓
Run E2E Tests ← If applicable
    ↓
Manual Testing
    ↓
Deploy to Production
```

---

## Mocking Strategy

### Unit Tests
- **Mock:** Database, API calls, file system, time
- **Why:** Fast, isolated, deterministic
- **How:** Use framework mocking (jest.mock, unittest.mock)

### Integration Tests
- **Real:** Database (test DB), file system
- **Mock:** External services (payments, email)
- **Why:** Test real interactions, avoid external costs/delays

### E2E Tests
- **Real:** Everything (use test/sandbox mode for external services)
- **Why:** Test complete real-world scenario

---

## Bundled Resources

**Guides (detailed procedures):**
- [overview.md](guides/overview.md) - Test pyramid and strategy overview
- [smoke-tests.md](guides/smoke-tests.md) - Infrastructure smoke testing
- [unit-tests.md](guides/unit-tests.md) - Unit testing guide for code-developer
- [integration-tests.md](guides/integration-tests.md) - API and database testing
- [e2e-tests.md](guides/e2e-tests.md) - End-to-end user journey testing

**References (examples and patterns):**
- [testing-examples.md](references/testing-examples.md) - Code examples for common scenarios

---

## Common Questions

**Q: Do I need tests for this one-line change?**
A: No, if it's trivial (text update, simple config). Yes if it affects logic.

**Q: When should I propose E2E tests?**
A: For large features (>5 tasks) or critical flows, after deploying to dev.

**Q: Can I defer writing unit tests?**
A: No. Write tests immediately after code in the same session.

**Q: How many E2E tests should I write?**
A: Only 3-5 tests for the most critical user journeys, not everything.

**Q: Do integration tests replace unit tests?**
A: No. Unit tests test logic in isolation. Integration tests test real interactions.

---

## Related Skills

- **infrastructure** - For setting up testing infrastructure
- **command-manager** - For creating test-related commands

---

## Summary

This skill ensures:
- ✅ Appropriate test coverage at all levels
- ✅ Tests written at the right time
- ✅ Fast feedback loops (unit tests)
- ✅ Confidence in integrations
- ✅ Critical flows validated end-to-end
- ✅ Regression protection

**Remember:** More tests ≠ better. Right tests at right time = better.
