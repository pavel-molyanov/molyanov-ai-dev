# Reproduction Modes

Read only the section matching the strongest source available. Direct source measurements outrank visual guesses.

When typography is visible, compare line endings, wraps, baselines, line height, and text-block bounds. Attribute a residual to rasterization only after those metrics align and the remaining difference is confined to glyph edges.

## Figma

1. Identify the exact file key, target node IDs, and their authoritative parent desktop/mobile viewport frames. Record two coordinate systems separately: the parent frame width used to render the route, and the target node bounds relative to that parent.
2. Use Figma REST data when credentials are available:
   - Read a token from the configured environment; keep it out of commands, logs, reports, and screenshots.
   - Query `/v1/files/{file_key}/nodes?ids={node_ids}` for hierarchy, bounds, text, fills, effects, constraints, and component references.
   - Query `/v1/images/{file_key}?ids={node_ids}&format=png&scale=1` for a visual reference at the frame's native dimensions.
   - If REST access is unavailable, use an accessible viewer/export only when it preserves the node and native dimensions. Otherwise request a node PNG/PDF/HTML export or access, and label the result approximate until exact measurements exist.
3. Inspect fonts, exact colors/opacity, container and element bounds, alignment, gaps, padding, radius, shadows, images, crop mode, and layer order before coding. Record the source-family → runtime CSS-family → rendered family mapping from the actual asset/framework declaration and browser evidence, then prove that family/style/weight rendered before judging text wraps; repeat with a narrow text selector for each combination that materially affects wrapping. Treat unexpected glyph fallback as incomplete evidence; explicitly allow only an intended emoji/icon fallback. Fallback or unverifiable faces use the unavailable-font decision from the main skill.
4. Treat the parent frame width as authoritative for responsive rendering. A 30–40k-pixel Figma frame height is content height, not browser viewport height. Use a supplied prototype viewport height when known; otherwise use and record the project's stable browser baseline. If undefined viewport height changes `vh`, sticky, or fixed behavior in scope, ask the user before calling it exact.
5. Export the smallest stable enclosing frame that preserves the target's positioning context. Render the route at the parent frame width and capture that same enclosing context. If an element-only crop is unavoidable, also compare its DOM bounds relative to the agreed parent.
6. Create an exact comparison for every supplied authoritative viewport, normally desktop and mobile. If dimensions differ, first find the wrong parent viewport, context bounds, content height, or source node.
7. For a very tall page-scope task, split the requested and touched scope into native-size section frames or contiguous slices and overlay each one, then use a full-page screenshot as an overview. An isolated section needs complete coverage only of that section and no full-page overview. A monolithic overlay is not required when the authoritative source cannot be exported at native size.

## Claude Design Export

Use the richest export the user can provide:

1. Prefer a Project HTML ZIP or standalone HTML because it preserves assets, hierarchy, and CSS clues.
2. Use PDF as a visual reference when HTML is unavailable. Render the relevant page/region to an image before overlay comparison.
3. Use an artifact link only when it exposes enough code or a stable render to inspect.
4. Treat PowerPoint as a last-resort visual source.

Exported code is evidence, not automatically production code. Adapt its structure to the target project's components, tokens, assets, responsive system, and accessibility conventions. Preserve exact visual values where the export is authoritative; discuss conflicts with the user.

## Screenshots

1. Record the screenshot's pixel dimensions and likely viewport/device scale. Ask for the matching viewport when it cannot be inferred safely.
2. Separate visible facts from approximations. Exact facts include color samples, alignment lines, repeated gaps, crop, and relative geometry. Hidden DOM structure, off-screen behavior, breakpoints, and font metadata may be unknown.
3. Reproduce the visible target at the screenshot width and compare side by side or with an overlay. Label unsupported responsive behavior as an approximation.
