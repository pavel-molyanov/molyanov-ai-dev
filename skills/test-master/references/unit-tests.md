# Unit Testing Guide

Use a unit boundary when one unit owns the calculation, decision, validation, transformation, or
error behavior being protected.

## Preserve the Selected Boundary

- Exercise the meaningful unit behavior directly; do not replace it with configured mock values.
- Replace dependencies only outside that boundary. Control network, database, filesystem, time,
  or randomness when their real behavior is not the test subject.
- Keep a real temporary filesystem, in-memory database, framework hook, or collaborating component
  when the scenario depends on that behavior; then classify the test by the boundary it actually
  exercises rather than forcing it to remain a unit test.
- Assert required outgoing calls when the interaction itself is the observable contract. A call
  assertion that only repeats mock setup proves nothing about the unit.

If meaningful behavior depends on real hooks, context, lifecycle, or several components, select an
integration or E2E boundary instead.
