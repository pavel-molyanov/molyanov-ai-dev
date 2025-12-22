# Testing Strategy Overview

## Test Pyramid

```
        /\
       /E2E\        ← Few (top 3-5 critical flows)
      /------\
     /Integr.\      ← Some (all API endpoints + DB)
    /----------\
   /   Unit     \   ← Many (all business logic)
  /--------------\
```

## Test Types & Execution

### Unit Tests
- **When:** Written for every task with business logic
- **By whom:** code-developer subagent
- **Run:** After code is written, before returning to orchestrator
- **Coverage:** All business logic (calculations, validations, transformations)
- **Speed:** Milliseconds (fast, isolated)

### Integration Tests
- **When:** Defined in Tech Spec, executed as separate task at end of feature
- **By whom:** code-developer subagent (dedicated task)
- **Run:** After all feature tasks complete
- **Coverage:** All API endpoints, database operations, external integrations
- **Speed:** Seconds (requires real dependencies)

### E2E Tests
- **When:** Defined in Tech Spec for large features or critical flows
- **By whom:** code-developer subagent (when requested)
- **Run:** After deploy to dev, before manual testing
- **Coverage:** Top 3-5 critical user journeys
- **Speed:** Minutes (full system tests)

## When Tests Are Run (Workflow)

### During Task Development
1. code-developer writes code
2. code-developer writes unit tests immediately
3. code-developer runs unit tests
4. If tests fail → fix code/tests, repeat
5. Return to orchestrator with passing tests

### After Task Completion
1. orchestrator runs new tests (verification)
2. orchestrator runs all tests (regression check)
3. If regression fails → analyze and fix

### End of Feature
1. Execute integration tests task (if defined in Tech Spec)
2. Deploy to dev
3. Propose E2E tests (if large feature or critical flows)
4. Run manual testing

## Regression Testing

**Purpose:** Ensure new code doesn't break existing functionality

**Process when regression tests fail:**
1. **Analyze cause:**
   - Bug in new code → code-developer fixes
   - Test is outdated → update test for new behavior
   - Behavior changed intentionally → ask user, update tests, document change
2. **Re-run regression check**
3. **Proceed only when all tests pass**

## Coverage Requirements

### What Must Be Tested

**Unit Tests:**
- All functions with business logic
- All calculations and validations
- All data transformations
- All decision-making code
- Exception: Simple getters/setters, trivial changes (one-line text updates)

**Integration Tests:**
- All API endpoints (especially POST/PUT/DELETE)
- All database operations (create, update, delete)
- All external service integrations (payment, email, webhooks)

**E2E Tests:**
- Top 3-5 most critical user journeys
- Defined during User Spec phase
- Examples: authentication, payment flow, core business process

## Key Principles

1. **Write tests immediately** - Don't defer testing to later
2. **Keep tests fast** - Unit tests in milliseconds, optimized integration tests
3. **Isolate tests** - Mock external dependencies in unit tests
4. **One concern per test** - Each test validates one specific behavior
5. **Test behavior, not implementation** - Focus on what code does, not how
6. **Clear test names** - Describe what is being tested and expected outcome

## Tech Spec Requirements

When creating Tech Spec, agent must define:

```markdown
## Testing Requirements

**Integration Tests:** [Required/None]
- List of endpoints/integrations to test

**E2E Tests:** [Required/None]
- List of critical user journeys for E2E
```

If not needed, write "None". If needed, specify what must be tested.
