# Exact Source Reproduction

Use this reference when a visual source defines all or part of the requested result. Source evidence controls every defined value; unusual color, spacing, size, density, crop, or composition is reproduced rather than corrected by general design taste.

## Establish the Comparable Block

1. Identify the exact source block and its owning viewport or parent frame. Use the owning viewport `WIDTHxHEIGHT` to render the page, while the exported source block and selected DOM capture use their separate matching block bounds.
2. Obtain both:
   - block data: structure, dimensions, text, colors, variables, components, comments, effects, constraints, and assets;
   - a separate PNG of that same block at `1x`, suitable for comparison with the site capture.
3. Record the source width and block dimensions. Before comparison, confirm that the PNG is from the intended node, uses `1x`, and matches the expected block size. Diagnose mismatches instead of resizing images.

## Figma

Use Figma MCP first when it is available:

1. Call `get_design_context` for the specific block or frame to obtain its complete design context. Use `get_metadata` only to locate the correct node in a large file; metadata does not replace the block context.
2. Obtain an image of the same node. Save the MCP-returned image at its original size when possible; otherwise use `get_screenshot`. When the available remote MCP supports a persistent export, `download_assets` may export that node as PNG at `1x`.
3. Treat generated code as evidence about structure and styling, then adapt it to the project's real stack and conventions. A referenced project component, component documentation, designer comment, or design variable is stronger evidence than an incidental raw value in generated code.
4. Use the exact Figma images and icons rather than redrawing them. Save the required file through the project's asset or data path; do not leave a temporary Figma URL in production code.

If MCP is unavailable, use the Figma API: `/nodes` for block data and `/images` with PNG at `1x` for the visual source. A manual export of the exact block at its original size is the final fallback. Keep credentials out of commands, logs, reports, and screenshots.

If the supplied link identifies only a whole file, request the needed frame or element. If a large block cannot be loaded, retry with a smaller matching block. `get_screenshot` supplies pixels, while `get_design_context` supplies design data; neither substitutes for the other.

## Other Exact Sources

### Claude Design

Prefer a Project HTML ZIP or standalone HTML because it preserves hierarchy, CSS clues, and assets. Use PDF or a stable rendered artifact when HTML is unavailable, and render the relevant block to a separate native-size image before comparison. Source code is evidence, not production code; adapt it to the target project while preserving authoritative visual values.

### Screenshot or Existing Page

Record the image dimensions, owning viewport, and device scale when known. If the owning viewport or device scale cannot be established safely, request it or label responsive mapping as approximate; do not treat the crop width as the browser viewport by default. Separate visible facts such as alignment, color, repeated gaps, crop, and relative geometry from unknown DOM structure, off-screen behavior, fonts, and breakpoints. Capture the corresponding site block inside the owning viewport.

## Inspect and Compare

Before coding, inspect the exact font family, weight, style, line height and wrapping; colors and opacity; container and element bounds; alignment, gaps, and padding; radii and shadows; images and crop; and layer order.

For each source width:

1. Export or crop the smallest stable source block that preserves the required positioning context.
2. Render at the owning source viewport and capture the corresponding DOM block at the source block's dimensions with `node scripts/capture.mjs --url <url> --project-root <repo> --viewports <explicit-WIDTHxHEIGHT-list> --selector <block> --out <new-child-path>` from the skill directory.
3. Run `node scripts/overlay.mjs --reference <source-block.png> --actual <site-block.png> --project-root <repo> --out <new-child-path>` on the two same-size images. Use a new non-existent child of the workflow's temporary evidence root for every capture and overlay invocation.
4. Open the source, site capture, `diff.png`, and optionally `overlay.png` as separate images.
5. Diagnose a size mismatch at the source node, DOM block, viewport, or crop boundary instead of resizing either image. Correct confirmed differences and repeat only this block and its affected widths.

Pixel differences identify where images differ; they do not decide whether the design or composition is correct. Attribute residual text differences to browser rasterization only after family, style, weight, glyphs, line endings, wrapping, baselines, line height, and text-block bounds align and the remaining difference is confined to glyph edges.

## Long Pages

Create the block checklist from the source, top to bottom:

- for Figma, use the major sections of the parent frame;
- for an existing page, map its major visual sections to DOM elements;
- for one long source image, divide it sequentially into ordinary block images without creating a contact sheet.

For every checklist item, locate the matching source region and DOM block, obtain a separate source image and site capture, compare the pair, correct confirmed differences, and mark the item checked. Page verification is complete only after every listed block was inspected at the chosen widths. A long whole-page image or collage does not replace block-by-block coverage.

Split a tall block by natural matching child blocks first. If none exist, capture it whole and run `overlay.mjs --parts 3`. Inspect all three sequential sets:

```text
part-01-reference.png
part-01-actual.png
part-01-difference.png
part-01-overlay.png
```

Repeat for parts 02 and 03. The parts are mechanical crops, not a quality score or an automatic selection of suspicious areas.
