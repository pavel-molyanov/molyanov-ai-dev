# WordPress and PHP Theme Adapter

Apply this adapter only to WordPress or PHP theme work.

## Locate the Owning Layer

1. Read repository instructions and determine which theme, plugin, template, block, or builder actually renders the target.
2. Trace the template/partial, enqueue path, source stylesheet, compiled asset, and relevant script before editing.
3. Edit source files and run the documented build. Commit generated assets only when the project normally tracks them.
4. Respect template escaping, localization, semantic HTML, and WordPress APIs while keeping presentation logic out of business/data helpers.

## Preserve the Design System

- Inspect `theme.json`, CSS custom properties, font declarations, block styles, and nearby template parts.
- Prefer the target landing/page's scoped system when it intentionally differs from the broad theme system.
- Check selector specificity and cascade order before adding an override. Put a rule in the owning component/section whenever possible.
- Verify both authenticated/editor context and the public render only when the task affects both.

## Runtime and Visual Checks

- Use the documented local environment when available. If only a remote development environment exists, keep credentials in named environment variables and out of commands/reports.
- Rebuild assets, load the actual route, wait for fonts and images, and inspect PHP/runtime errors alongside the visual result.
- Check horizontal DOM geometry even when the theme uses `overflow-x: hidden` or `clip`; clipping can conceal a broken child.
