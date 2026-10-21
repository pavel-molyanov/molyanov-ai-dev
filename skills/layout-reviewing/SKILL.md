---
name: layout-reviewing
description: |
  Layout review criteria: fidelity to a source such as Figma or a screenshot, consistency with
  the project where no source exists, required viewport and state evidence, and visual defects in
  spacing, typography, color, assets, and responsive reflow. Use whenever an implemented web layout
  is reviewed or checked against its design or across screen widths. Implementing or fixing a
  layout uses layout-writing.
---

# Layout Reviewing

Judge the supplied implementation and prepared evidence. You may challenge the visual approach,
responsive behavior, or treatment of states and propose a stronger alternative within the supplied
scope. Do not replace an intentional source value with personal taste.

## Review Basis

- Where an exact source exists, it controls defined geometry, spacing, color, typography, crop,
  effects, layering, content placement, and responsive states.
- Where no source exists, use repository rules, the same component in other states, neighboring
  UI, tokens, and established components as the review standard.
- For a partial source, keep these responsibilities separate. General design conventions do not
  override values the source defines intentionally.

## Evidence Coverage

- A selected-area review covers the changed block, its nearest positioning context, applicable
  states, and every required width.
- A whole-page review requires an ordered source- or DOM-derived inventory and evidence for every
  listed block at every required width.
- Required widths include baseline `360`, `430`, `768`, and `1440` coverage, established source
  or user-screenshot viewports, and both sides of affected breakpoints.
- Missing evidence is a defect only when the review contract requires it and its absence prevents
  a defined block, state, or width from being checked. Identify that missing coverage precisely.

## Visual Criteria

Inspect each supplied width, block, and state for:

- alignment, container bounds, spacing, density, sizing, and responsive reflow;
- font family, weight, size, line height, wrapping, truncation, and text clipping;
- colors, opacity, borders, radii, shadows, backgrounds, and layer order;
- image or icon choice, aspect ratio, crop, position, and asset quality;
- horizontal overflow, unusable compression, disappearing content, and broken interaction states;
- consistency with project components and tokens where the source leaves a decision unspecified.

For exact-source comparisons, source and site blocks must have matching native dimensions. A diff
image localizes pixel differences but does not prove a defect by itself. Attribute residual text
differences to rasterization only after typography, wrapping, baselines, and bounds align.

Ground every mismatch, coverage gap, critique, or alternative in a precise code or image-region
location, observed evidence, the applicable source or project requirement, relevant width and
state, and visible impact. Explain why a proposed alternative is stronger for the reviewed layout.
Raster noise, taste, unsupported inference, and unrelated pre-existing layout issues are not
findings.
