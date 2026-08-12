---
name: code-writing
description: |
  Guides code implementation through proportional context reading, focused changes, verification, and fresh reviews.
  Use whenever code needs to be written — from a short ad-hoc edit to a full user-spec.

  Use when: "напиши код", "закодь", "реализуй", "write code", "implement"

  Do NOT use for pure layout from Figma, Claude Design, screenshots, or an existing visual
  style ("сверстай", "подвинь блок", responsive) — use layout-writing instead.
  Direct mixed layout + business-logic work uses both layout-writing and code-writing.

  For creating a user-spec → user-spec-planning skill.
---

# Code Writing

## Understand the Change

1. Extract the requested behavior and what done means from the request or user-spec. Resolve
   ambiguity from repository evidence; ask only when a substantive choice changes the result or
   scope.
2. Read repository instructions, affected code, its usages, and only the project documentation
   needed to change it safely. A localized edit needs local context; cross-cutting work needs its
   contracts, architecture, and relevant patterns.
3. For non-trivial work, read every source file that will change, find affected contracts and
   reusable code, and establish the smallest useful baseline check. Inspect generated, lock,
   snapshot, or other mechanical artifacts through their generator, relevant diff, and
   deterministic validation rather than an unhelpful full read.
4. Discuss the approach before editing only when evidence exposes a substantive fork, risk, or
   scope decision. Otherwise choose the smallest safe implementation that follows project or
   framework conventions.
5. Treat a new idea, risk, edge case, or opportunity discovered during implementation or review
   as a proposal, not authorization. A rare or unagreed scenario is a user decision even when its
   correction looks local. Correct autonomously only an authorized local defect in agreed normal
   behavior; ask before adding behavior, state, entities, contracts, dependencies, architecture,
   or material complexity.

## Implement and Verify

1. Implement only the requested behavior. Reuse existing capabilities before adding abstractions
   or dependencies. Do not add speculative validation, fallbacks, configuration, optimization,
   or future flexibility without a current requirement or realistic project condition.
2. Validate untrusted input at its boundary, keep secrets out of source, preserve useful error
   information, and handle failures where the program can recover or add context.
3. Let straightforward code explain itself. Comment only when code cannot communicate the reason
   for a business rule, safety invariant, external constraint, compatibility workaround,
   deliberate tradeoff, or required ordering.
4. When the change can alter observable behavior, apply `test-master` to select and run the
   protecting tests. If it has no test subject, state that instead of creating artificial
   assertions.
5. Run the smallest supported lint, format, type, build, render, and user-requested checks that
   cover the change. Use a project-wide command only when it is the available entrypoint or the
   change is cross-cutting. Separate unrelated baseline failures from regressions.

## Run Fresh Reviews

Run no more than two review waves. One wave launches the complete reviewer set selected for the
implementation in parallel against the same revision. Use that same complete set in both waves.
Include reviewers required by other active skills in these same waves instead of starting a
separate wave sequence.

After every completed implementation, include a fresh `code-reviewer` without a model override.
Its review scope matches the change: a localized edit gets focused connected context; a broad
change gets all affected contracts and architecture.

Also launch in parallel when applicable:

- `security-auditor` when a security boundary changed or the user requested a security review.

`test-master` owns the additional `test-reviewer` invocation when meaningful test code changed.
Include that reviewer in every wave for this implementation.

Give each reviewer the user request or user-spec, applicable repository instructions, validation
evidence, every touched source file with relevant callers and dependencies, deleted or renamed
file evidence, and generator/diff/validation evidence for mechanical artifacts.

Review findings are diagnoses, not a work queue. Check the evidence and exact correction. Apply
only an authorized local correction to agreed normal behavior. If the scenario is rare or
unagreed, or the correction adds behavior, state, entities, contracts, dependencies, architecture,
or material complexity, reject it with a short reason or ask the user before editing.
`user_decision_required: false` does not replace this check. Reject unsupported findings with
evidence and report unrelated findings without expanding the task.

After wave 1, correct only authorized local defects in agreed normal behavior that do not require a
user decision, then rerun affected direct checks. If those corrections changed the reviewed result,
launch wave 2 with the same complete reviewer set. Stop after a clean wave or when no authorized
correction changes the result.

After wave 2, do not launch another reviewer automatically. Correct remaining local defects only
in agreed normal behavior and only when they do not require a user decision, rerun the applicable
direct checks, and hand off any remaining findings or required decisions about scope, behavior,
approach, or material complexity. Briefly explain rejected rare findings in the handoff.
