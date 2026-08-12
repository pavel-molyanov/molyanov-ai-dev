---
name: test-master
description: |
  Guides test selection, authoring, and quality review at the smallest reliable boundary.

  Use when: "напиши тесты", "как тестировать", "проанализируй тесты", "проверь качество тестов", "ревью тестов", "тестовая стратегия"
---

# Test Master

## Decide What to Protect

Tests protect observable behavior or another explicit contract that must survive change. Trace
each selected scenario to the user request, user-spec, or changed project contract.

Freely editable copy, presentation-only markup or styles, constants that merely repeat their
source value, and framework behavior normally have no test subject. They become testable when an
explicit user, accessibility, legal, safety, protocol, or project requirement makes their
presence or semantics invariant. Test that contract at an observable boundary rather than
freezing implementation shape or exact wording.

## Choose the Smallest Reliable Boundary

Protect each distinct risk once at the smallest boundary that can reproduce it:

| Boundary | Use when the risk depends on |
|---|---|
| Unit | One unit's calculation, decision, validation, transformation, or error behavior |
| Integration | An API, database, filesystem, queue, service contract, or collaborating components |
| E2E | A critical user journey or behavior that needs the real application stack |
| Smoke | Successful startup, initialization, deployment, or minimal system integration |

Do not repeat the same risk at several levels for pyramid completeness. A characterization test
may pass before a refactor when its purpose is to prove existing behavior remains unchanged.

When authoring a selected type, apply its conditional guide:

- [unit-tests.md](references/unit-tests.md) — unit structure, dependency boundaries, and mocking;
- [integration-tests.md](references/integration-tests.md) — real component boundaries, fixtures,
  external services, and cleanup;
- [e2e-tests.md](references/e2e-tests.md) — journeys, environment, selectors, and execution;
- [smoke-tests.md](references/smoke-tests.md) — minimal startup and infrastructure coverage.

## Authoring Rules

- Test observable results, state, errors, or required outgoing interactions rather than private
  implementation shape.
- Cover the changed happy path, meaningful branches, failure paths, and specified edge cases
  without duplicating an already protected risk.
- Keep tests independent and deterministic with known state. Replace dependencies only outside
  the boundary the test is meant to exercise.
- Several mocks are a signal to inspect the boundary, not a defect by count. A test fails when
  mocks replace the meaningful decision or merely replay configured values.
- Use clear scenario names and minimal fixtures. Run the selected tests and separate unrelated
  baseline failures from regressions.

## Test Review

When meaningful test code changes, run a fresh `test-reviewer` in `full` mode after implementation.
For a user-requested review of existing tests, apply
[test-quality-review.md](references/test-quality-review.md) — demonstrated coverage gaps,
boundary problems, and ineffective tests.

Reviewer severity follows the concrete regression that can pass undetected, not the category or
appearance of the test problem. Naming preferences and optional improvements without concrete
impact are not findings.
