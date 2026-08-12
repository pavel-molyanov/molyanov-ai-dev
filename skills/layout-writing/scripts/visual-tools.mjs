import { createRequire } from "node:module";
import { resolve } from "node:path";

const MAX_VIEWPORT_EDGE = 10_000;

export function parseViewportList(value) {
  if (value === undefined || value === null) {
    throw new Error("viewport list is required; expected WIDTHxHEIGHT");
  }

  const entries = String(value)
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);

  if (entries.length === 0) {
    throw new Error("viewport list is required; expected WIDTHxHEIGHT");
  }

  return entries.map((entry) => {
    const match = /^(\d+)x(\d+)$/i.exec(entry);
    if (!match) {
      throw new Error(`invalid viewport "${entry}"; expected WIDTHxHEIGHT`);
    }
    const width = Number(match[1]);
    const height = Number(match[2]);
    if (
      width < 1 ||
      height < 1 ||
      width > MAX_VIEWPORT_EDGE ||
      height > MAX_VIEWPORT_EDGE
    ) {
      throw new Error(
        `invalid viewport "${entry}"; edges must be 1-${MAX_VIEWPORT_EDGE}px`,
      );
    }
    return { width, height };
  });
}

export function safeFileStem(value) {
  const stem = String(value)
    .normalize("NFKD")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
  return stem || "capture";
}

export function assertMatchingDimensions(reference, actual) {
  if (reference.width !== actual.width || reference.height !== actual.height) {
    throw new Error(
      `reference and actual must have the same dimensions; got ` +
        `${reference.width}x${reference.height} and ${actual.width}x${actual.height}`,
    );
  }
}

export function buildScrollPlan(
  start,
  end,
  preferredStep,
  maximumPositions = 120,
) {
  if (![start, end, preferredStep, maximumPositions].every(Number.isFinite)) {
    throw new Error("scroll position inputs must be finite numbers");
  }
  if (preferredStep <= 0 || maximumPositions < 2 || end < start) {
    throw new Error("invalid scroll position range");
  }

  const positions = [];
  for (
    let position = start;
    position < end && positions.length < maximumPositions;
    position += preferredStep
  ) {
    positions.push(Math.round(position));
  }
  const complete = positions.length < maximumPositions;
  if (complete) positions.push(Math.round(end));
  return { positions: [...new Set(positions)], complete };
}

export function platformFontMatches(expectedFamily, renderedFamily) {
  const normalize = (family) =>
    String(family)
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "");
  const expected = normalize(expectedFamily);
  const rendered = normalize(renderedFamily);
  if (!expected || !rendered) return false;
  if (expected === rendered) return true;
  const aliasGroups = [
    ["arial", "arialmt"],
    ["timesnewroman", "timesnewromanpsmt"],
    ["couriernew", "couriernewpsmt"],
  ];
  return aliasGroups.some(
    (group) => group.includes(expected) && group.includes(rendered),
  );
}

export function parseExpectedFont(value) {
  const [
    rawFamily,
    rawWeight = "400",
    rawStyle = "normal",
    rawSelector,
    rawPlatformFamily,
  ] = String(value)
    .split("|")
    .map((part) => part.trim());
  if (!rawFamily) throw new Error("expected font family is required");
  if (!/^(normal|bold|[1-9]00)$/.test(rawWeight)) {
    throw new Error(`invalid expected font weight: ${rawWeight}`);
  }
  if (!/^(normal|italic|oblique)$/.test(rawStyle)) {
    throw new Error(`invalid expected font style: ${rawStyle}`);
  }
  return {
    family: rawFamily,
    weight: rawWeight,
    style: rawStyle,
    ...(rawSelector ? { selector: rawSelector } : {}),
    ...(rawPlatformFamily ? { platformFamily: rawPlatformFamily } : {}),
  };
}

export function loadPlaywright(projectRoot) {
  const root = resolve(projectRoot);
  const requireFromProject = createRequire(resolve(root, "package.json"));
  try {
    return requireFromProject("playwright");
  } catch (error) {
    throw new Error(
      `Playwright is not available from ${root}. Install it in the target project ` +
        `and run its browser install command. Cause: ${error.message}`,
    );
  }
}
