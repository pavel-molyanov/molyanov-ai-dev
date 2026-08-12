---
name: layout-writing
description: |
  Reproduces and adjusts web layouts from Figma, Claude Design exports, screenshots, or an existing project style with high visual fidelity and proportional verification.
  Use when: "сверстай по Figma", "поправь вёрстку", "подвинь блок", "перенеси из Claude Design", "сделай адаптив", "добавь в том же стиле", "implement layout", "match Figma", "fix responsive layout".
  Use alongside code-writing for mixed layout and business-logic tasks; use code-writing alone for logic-only work. Blank-slate visual design is outside this skill.
---

# Layout Writing

Deliver a layout that matches its exact source where one exists, fills only genuinely unspecified
decisions from project evidence, and works at relevant widths in the existing codebase.

## Scope and Source

1. Read repository guidance, the affected component and styles, tokens, fonts, images, nearby
   components, and the relevant run or build command.
2. Classify the scope:
   - `selected area` — verify the changed element, component, or section with its nearest context;
   - `whole page` — build an ordered inventory of every major visual block from source metadata,
     node IDs, a DOM outline, or complete source-image segments, then verify every item.
3. With an exact source, apply [reproduce.md](references/reproduce.md) — source acquisition,
   native-size evidence, and comparison. Without an exact source, apply
   [design-decisions.md](references/design-decisions.md) — project-first decisions for unspecified
   values. For a partial source, apply each reference only to the area it governs.
4. Ask only for blockers that project or source evidence cannot resolve: the relevant frame when
   a Figma link names only a file, substitution of a required missing font or asset, or expansion
   beyond the requested scope.

Treat a new requirement, state, edge case, or improvement discovered during implementation or
review as a proposal, not authorization. If it changes the agreed presentation, behavior, scope,
approach, or material complexity, explain it and get the user's decision first. Correct
autonomously only a local mismatch inside the already agreed presentation.

`layout-writing` owns markup structure, styles, responsive behavior, typography, asset placement,
and visual verification. `code-writing` owns data flow, state, APIs, validation, and business
behavior; use both for mixed work.

## Implement and Capture Evidence

1. Reuse suitable project components, tokens, primitives, fonts, images, and the asset pipeline.
   Implement the smallest change that satisfies the request; exact-source values override general
   design taste, while unspecified decisions follow project evidence.
2. Build a deduplicated viewport list for `capture.mjs` and pass it explicitly with `--viewports`:
   - `360`, `430`, `768`, and `1440` widths for baseline responsive coverage;
   - every established exact-source or user-screenshot viewport;
   - widths immediately before and after affected CSS breakpoints.
   Use the owning source height when known; otherwise choose one stable representative height and
   reuse it across captures and reruns.
3. Before capturing, create one temporary evidence root outside the repository. Give every
   capture or overlay invocation a new child `--out` path because the scripts reject existing
   targets and prior evidence must remain unchanged.
4. At every chosen width, render the selected area or every whole-page inventory block with its
   nearest relevant context and affected states. Apply the native-size comparison procedure from
   `reproduce.md` wherever an exact source exists; otherwise inspect composition, wrapping,
   clipping, crop, states, and horizontal overflow.
5. Correct confirmed mismatches and repeat only affected blocks and widths with new output paths.
   Run the smallest project check that proves the changed route still compiles or renders.

## Review and Hand Off

Run no more than two review waves. After every implementation, run wave 1 with one fresh
`layout-reviewer` without a model override. Pass the request, scope, changed files, applicable
repository instructions and project-pattern evidence, source mode and responsibility boundary,
all checked widths, site images for every checked block and state, source and difference images
where applicable, and the complete inventory and evidence set for a whole page or segmented tall
block. Include reviewers required by other active skills in these same waves instead of starting a
separate wave sequence.

Evaluate every finding by its source or project requirement, evidence, width and state conditions,
and visible impact. Before changing the layout, evaluate the specific intended correction, not only
the finding. Apply it automatically only when that exact correction is authorized by the user
request or approved plan. A valid finding does not authorize additional work. If the correction
has no clear authorization anchor or expands the agreed work, show the user the finding and proposed
correction, then wait before editing. After an authorized correction changes the reviewed result,
recapture affected evidence and run wave 2 with a fresh `layout-reviewer`. Stop after a clean wave
or when no authorized correction changes the result.

After wave 2, do not launch another reviewer automatically. Correct remaining local mismatches
inside the agreed presentation, recapture and inspect the affected widths and states, and report
any remaining findings or required user decisions.

Hand off with the change summary, checks run, widths and blocks actually verified, finding
dispositions, and known evidence limitations.
