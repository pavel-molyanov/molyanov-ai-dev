# Unit Testing Guide

**For:** code-developer subagent working on a task

## When to Write Unit Tests

Write unit tests **when justified**:

### ✅ Write tests for:
- Functions with business logic (calculations, validations, transformations)
- Functions that make decisions (if/else, switch, conditions)
- Data processing and formatting
- Error handling logic
- Edge cases and boundary conditions

### ❌ Skip tests for:
- Simple getters/setters without logic
- One-line text changes or UI copy updates
- Trivial configuration changes
- Tasks without code (research, documentation, GitHub issues)

**Rule of thumb:** If the function transforms data or makes a decision → test it.

## Development Flow

1. **Read the task** - Understand requirements and acceptance criteria
2. **Write the code** - Implement the functionality
3. **Write tests immediately** - Don't defer, write in the same session
4. **Run tests** - Verify they pass
5. **If tests fail** - Fix code or tests, repeat step 4
6. **Return to orchestrator** - Only when all tests pass

## What to Test

### Test the task requirements
All functionality described in the task must be covered:
- Main happy path (expected behavior)
- Edge cases mentioned in task
- Error handling specified in task
- Validation rules from task

### Test business logic
- Input validation (valid/invalid inputs)
- Calculations (correct results, edge values)
- Transformations (data format changes)
- Conditional logic (all branches)
- Error conditions (exceptions, failures)

## How to Organize Tests

### Structure: Arrange → Act → Assert

1. **Arrange** - Set up test data and preconditions
2. **Act** - Execute the function being tested
3. **Assert** - Verify the result matches expectations

### One test = one concern
- Each test validates one specific behavior
- Don't test multiple unrelated things in one test
- Makes failures easier to diagnose

### Clear test names
Name tests to describe what they test:
- `test_calculate_total_with_discount`
- `test_validate_email_rejects_invalid_format`
- `test_parse_date_handles_null_input`

## Mocking Dependencies

### What to mock
- Database calls
- API requests to external services
- File system operations
- Time/dates (for consistent tests)
- Random number generators

### Why mock
- Tests run fast (milliseconds)
- Tests are isolated (no external dependencies)
- Tests are reliable (no network/DB failures)
- Tests are repeatable (same result every time)

### How to mock
Use mocking libraries appropriate to your tech stack:
- Mock external service responses
- Mock database query results
- Inject mocked dependencies into functions

## Key Rules

1. **Fast execution** - Unit tests must run in milliseconds
2. **Isolated** - No real database, API, or file system access
3. **Deterministic** - Same input → same output, always
4. **Independent** - Tests don't depend on each other
5. **Single assertion** - One test = one thing to verify
6. **Immediate** - Write tests right after code, not later

## Coverage Check

Before returning to orchestrator, verify:
- ✅ All business logic from task is tested
- ✅ All tests pass
- ✅ No skipped or commented-out tests
- ✅ Edge cases are covered
- ✅ Error handling is tested
