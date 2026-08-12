---
name: code-reviewing
description: |
  Reviews code against the user request, project conventions, cross-file contracts, and applicable quality risks.
  Use when: "проверь код", "code review", "ревью кода", "review this code", "check code quality"
---

# Code Reviewing

Function length, nesting, broad types, hardcoded values, repeated resource construction, or
multiple mocks are signals to investigate; they are not defects by themselves.

## Contents

- [Always Review](#always-review)
- [Review When Applicable](#review-when-applicable)

## Always Review

### Requirements and Correctness

- Trace the changed behavior to the user request or user-spec.
- Check happy paths, specified edge cases, failures, and state changes that the change owns.
- Identify behavior that was added accidentally or requested behavior that is missing.
- Separate new regressions from unrelated pre-existing problems.

### Scope, Necessity, and Simplicity

- Trace each added behavior, validation, fallback, branch, state, abstraction, dependency, and
  configuration option to a current requirement, project contract, or realistic condition in
  the present codebase.
- Report unrequested machinery only when it expands behavior or creates concrete maintenance,
  correctness, performance, or testing cost. Fewer lines are not automatically simpler; compare
  responsibilities, states, branches, dependencies, and concepts the solution introduces.
- Check whether the project already has a direct capability that satisfies the requirement. An
  abstraction used once is acceptable when it expresses a real boundary; it is a problem when it
  adds indirection or generality without a current use.
- Evaluate the chosen algorithm against realistic input size and project constraints. Report
  avoidable complexity only when an existing project capability or direct requirement proves it
  unnecessary and the current choice has a demonstrable consequence; do not prescribe a
  replacement, speculative optimization, or wholesale redesign.
- Treat handling for extremely unlikely cases as a defect only when no requirement or realistic
  path justifies it and the extra handling materially complicates the normal path.

### Cross-File Contracts

- Read every touched source file in full and the callers, dependencies, schemas, or interfaces
  on which the change relies. For deleted or renamed files, inspect the supplied change status
  and diff. For generated, lock, snapshot, or other mechanical artifacts, inspect the supplied
  diff, generator, and deterministic validation instead of consuming the whole artifact
  without benefit.
- Verify imports, names, argument order, return values, types, lifecycle assumptions, and error
  contracts against their definitions.
- Report a mismatch only when it can break behavior, compilation, loading, or a documented
  contract.

## Review When Applicable

### Architecture and Maintainability

Apply when the change alters responsibilities, dependencies, public interfaces, or repeated
logic.

- Prefer established project architecture over generic pattern preferences.
- Check cohesion, dependency direction, circular dependencies, duplicated responsibility, and
  abstractions that add indirection without solving a current problem.
- Treat size and nesting as readability signals. Report them only when they hide behavior,
  make a branch unsafe to change, or prevent useful testing.
- Treat duplicated knowledge or responsibility as a finding only when the copies must change
  together and a demonstrated divergence risk exists.
- Treat a hardcoded value as a problem when its meaning is unclear, it is repeated as policy,
  or it should vary by environment; a local obvious value needs no constant ceremony.

### Comments and Documentation

- Straightforward code should explain itself through structure and naming.
- A comment is useful when code cannot express why a non-obvious decision exists: a business
  rule, safety invariant, external constraint, compatibility workaround, deliberate tradeoff,
  or required ordering.
- The comment should explain the reason and what must remain true. A comment that merely
  narrates the next statement is noise and should be removed or replaced by clearer code.
- Report a missing comment only when future maintainers could reasonably remove or "simplify"
  an important constraint because its reason is not recoverable from code or project docs.

### Failure Handling and Observability

Apply when the change introduces a failure boundary, external operation, recovery path, or
operationally important state transition.

- Errors should be handled where the program can recover, translate them into a stable contract,
  or add information that is not already available.
- Preserve the original cause when propagating a failure. Do not require a local `try/catch`
  that only logs and rethrows; that commonly duplicates logs without improving recovery.
- Check empty catches, lost causes, misleading fallbacks, partial writes, and cleanup on failure.
- Follow the project's logging policy. Require a log when its absence creates a real diagnostic
  gap, not at every function that calls an API or database.
- Log only the minimum operational context needed. Keep secrets, credentials, sensitive
  payloads, emails, phone numbers, and unnecessary user identifiers out of logs.

### Types and Data Contracts

Apply to typed code, parsing, serialization, schemas, nullable data, or external input.

- Check that types describe runtime possibilities and that narrowing or assertions are justified.
- Validate untrusted input at the boundary where it enters the trusted system.
- Use parameterized queries and context-appropriate encoding at the destination; generic
  "sanitize everything" rules can corrupt valid data without preventing the relevant attack.
- Check migrations, defaults, compatibility, and partial-data behavior when data shape changes.

### Security

Apply when authentication, authorization, untrusted input, secrets, sensitive data, file paths,
database queries, rendering, or external requests changed.

- Verify authorization at the operation that needs protection, not only in the UI.
- Check injection, path traversal, XSS, CSRF, SSRF, secret exposure, unsafe deserialization, and
  privilege escalation as applicable to the changed boundary.
- Confirm sensitive configuration stays outside source and ignored secret files remain ignored.

### Performance and Resources

Apply when the change touches a hot path, loop over unbounded data, rendering frequency, query
shape, concurrency, or a heavy resource.

- Look for N+1 work, unbounded loads, repeated initialization, leaked handles, missing cleanup,
  and concurrency that can corrupt state or exceed external limits.
- Multiple resource instances may be correct for tenant, configuration, process, worker, or test
  isolation. Report them only when lifecycle and measured cost show harmful duplication.
- Report only the concrete bottleneck or unbounded resource risk.

### Dependencies

Apply when a dependency or its version changes.

- Check necessity, existing alternatives, manifest/lockfile consistency, imported API contracts,
  bundle or runtime impact, and compatibility with the project.
- Use repository evidence or supplied tool results for vulnerabilities, maintenance status, and
  licensing. If external evidence is unavailable, state that it was not verified rather than
  guessing.

### Tests

Apply when behavior or tests changed.

- Tests should protect the changed behavior at the smallest reliable boundary.
- Look for missing meaningful branches, failures, validation, transformations, and specified
  edge cases.
- Do not require tests for freely editable UX copy, presentation-only markup or styles, or
  mechanical changes with no observable contract to protect. Content, configuration, markup,
  styles, and accessors remain testable when they implement an explicit user, accessibility,
  protocol, or project contract.
- A mock is a problem when the test verifies its own setup or replaces all meaningful behavior,
  not when an arbitrary count is reached.
- Checking a call is valid when the interaction itself is the observable contract, such as
  publishing an event or sending a command with required arguments.
