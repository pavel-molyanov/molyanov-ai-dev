# Smoke Testing Guide

**For:** Infrastructure setup, verifying basic project functionality

## Purpose

Smoke tests verify minimal system functionality - "is the system alive?"

**Not for:**
- Testing business logic (use unit tests)
- Testing API endpoints (use integration tests)
- Testing user flows (use E2E tests)

**For:**
- Verifying project setup works
- Ensuring test infrastructure is functional
- Providing CI/CD with basic health check
- Confirming dependencies are installed

---

## When to Write Smoke Tests

### During Infrastructure Setup (Step 7)
- Part of testing infrastructure setup
- Created once per project
- Verifies test framework configuration
- Checks environment is set up

### Add to CI Pipeline
- Run smoke tests first (before unit/integration/E2E)
- If smoke test fails → don't run other tests (fail fast)
- Saves CI time by catching infrastructure problems early

---

## What to Test

### ✅ Write smoke tests for:
- Test framework itself works (`expect(true).toBe(true)`)
- Environment variables accessible (`process.env.NODE_ENV`)
- Key modules/packages can be imported
- Database connection can be established (without querying)
- Server can start (without making requests)

### ❌ Don't write smoke tests for:
- Business logic (use unit tests)
- API endpoints (use integration tests)
- User workflows (use E2E tests)
- Data processing (use unit tests)

---

## Test Pyramid Position

```
        /\
       /E2E\        ← Few (3-5 tests)
      /------\
     /Integr.\      ← Some (all endpoints)
    /----------\
   /   Unit     \   ← Many (all logic)
  /--------------\
 /    Smoke      \  ← Minimal (1-2 tests)
/------------------\
```

**Position:** Foundation of the pyramid - smallest, fastest, most basic.

---

## Example Smoke Tests

### Node.js/TypeScript

**File:** `tests/smoke.test.ts`

```typescript
/**
 * Smoke tests - verify basic project setup
 */

describe('Project Setup - Smoke Test', () => {
  it('should pass basic smoke test', () => {
    // If this fails, something is fundamentally broken
    expect(true).toBe(true);
  });

  it('should have NODE_ENV configured', () => {
    // Verify environment is set up
    expect(process.env.NODE_ENV).toBeDefined();
  });

  it('should be able to import main module', () => {
    // Verify main application code can be imported
    expect(() => {
      require('../src/index');
    }).not.toThrow();
  });
});
```

### Python

**File:** `tests/test_smoke.py`

```python
"""
Smoke tests - verify basic project setup
"""

import os


def test_smoke():
    """Basic smoke test to verify pytest is working."""
    assert True


def test_environment_configured():
    """Verify environment variables can be accessed."""
    # This should pass even if ENVIRONMENT is not set
    # (allows test to pass in minimal CI environments)
    env = os.getenv('ENVIRONMENT', 'test')
    assert env is not None


def test_main_module_import():
    """Verify main application module can be imported."""
    try:
        import src.main  # Adjust based on your structure
        assert True
    except ImportError as e:
        assert False, f"Failed to import main module: {e}"
```

---

## Characteristics

### Speed
- **Target:** Milliseconds
- **Requirement:** <1 second total
- Fastest tests in the pyramid

### Scope
- **Minimal:** 1-2 tests are sufficient
- Don't test everything, just basics
- If more than 5 smoke tests → probably testing too much

### When They Run
- **First** in test suite (before all others)
- **Every CI run** (fail fast if infrastructure broken)
- **Locally** when setting up project

### What They Don't Do
- ❌ Don't test business logic
- ❌ Don't make database queries
- ❌ Don't make API calls
- ❌ Don't test user interactions

---

## CI/CD Integration

### Run Smoke Tests First

```yaml
# .github/workflows/ci.yml
jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - name: Run smoke tests
        run: npm test -- tests/smoke.test.ts

  unit-tests:
    needs: smoke-test  # Only run if smoke passes
    runs-on: ubuntu-latest
    steps:
      - name: Run unit tests
        run: npm test -- tests/unit/
```

### Fail Fast Strategy

If smoke test fails:
- Stop CI pipeline immediately
- Don't run slower tests
- Save CI time and costs
- Infrastructure problem is obvious

---

## Coverage Requirements

**Minimal:** 1-2 smoke tests are sufficient.

**Smoke tests should:**
- Run in <1 second total
- Always pass (if fail → infrastructure problem)
- Be first tests written in project
- Be separate from unit/integration/E2E tests

**Do NOT:**
- Write comprehensive tests (that's what unit/integration/E2E are for)
- Test edge cases (unit tests)
- Test API endpoints (integration tests)
- Test user journeys (E2E tests)

---

## Key Principles

1. **Minimal** - Only 1-2 tests, not comprehensive
2. **Fast** - Must run in milliseconds
3. **Infrastructure-focused** - Tests setup, not logic
4. **Always pass** - If smoke test fails, stop everything and fix setup
5. **Run first** - Before all other test types

---

## Common Mistakes

### ❌ Too Many Smoke Tests
```typescript
// Bad: Testing too much in smoke tests
describe('Smoke', () => {
  it('test database connection', ...);
  it('test API endpoint', ...);
  it('test user creation', ...);
  it('test authentication', ...);
  // ... 20 more tests
});
```

**Fix:** Keep minimal (1-2 tests). Move others to appropriate test type.

### ❌ Slow Smoke Tests
```typescript
// Bad: Smoke test that takes seconds
it('should connect to database', async () => {
  await db.connect();  // Slow!
  await db.query('SELECT 1');  // Not a smoke test!
});
```

**Fix:** Smoke tests shouldn't make real connections. Just test imports work.

### ❌ Business Logic in Smoke Tests
```typescript
// Bad: Testing business logic
it('should calculate discount correctly', () => {
  expect(calculateDiscount(100, 0.2)).toBe(80);
});
```

**Fix:** Move to unit tests.

---

## Templates

**Node.js:** See [templates/smoke.test.ts](../../infrastructure/templates/smoke.test.ts)

**Python:** See [templates/test_smoke.py](../../infrastructure/templates/test_smoke.py)

---

## Checklist

Before completing smoke test setup:

- [ ] 1-2 smoke tests created
- [ ] Tests verify test framework works
- [ ] Tests verify environment configured
- [ ] Tests verify main module imports
- [ ] Tests run in <1 second
- [ ] Tests always pass (if fail → fix infrastructure)
- [ ] Tests added to CI/CD as first job
- [ ] CI configured to fail fast if smoke tests fail

---

## Summary

Smoke tests provide:
- ✅ Fast infrastructure validation
- ✅ Fail-fast mechanism in CI
- ✅ Confidence that test framework works
- ✅ Early detection of setup problems

**Remember:** Smoke tests are minimal. If you're testing more than basic setup, you probably need unit/integration/E2E tests instead.
