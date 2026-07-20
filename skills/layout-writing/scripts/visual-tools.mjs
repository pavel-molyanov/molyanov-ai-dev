import { createRequire } from "node:module";
import { resolve } from "node:path";

const DEFAULT_VIEWPORTS = "375x812,1440x900";
const MAX_VIEWPORT_EDGE = 10_000;

export const VISUAL_DETAIL_DEFAULT_THRESHOLD = 16;
export const VISUAL_DETAIL_TILE_SIZE = 32;
export const VISUAL_DETAIL_CROP_SIZE = 256;
export const VISUAL_DETAIL_IOU_THRESHOLD = 0.25;
export const VISUAL_DETAIL_LIMIT = 5;
export const VISUAL_DETAIL_BROAD_RATIO = 0.5;

export function parseViewportList(value = DEFAULT_VIEWPORTS) {
  const entries = String(value)
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean);

  if (entries.length === 0) {
    throw new Error("viewport list is empty");
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

export function visiblePixelDelta(referenceData, actualData, index) {
  const referenceAlpha = referenceData[index + 3];
  const actualAlpha = actualData[index + 3];
  let maximum = 0;

  for (let channel = 0; channel < 3; channel += 1) {
    const referenceChannel = referenceData[index + channel];
    const actualChannel = actualData[index + channel];
    const blackDelta =
      Math.abs(
        referenceChannel * referenceAlpha - actualChannel * actualAlpha,
      ) / 255;
    const whiteDelta =
      Math.abs(
        referenceChannel * referenceAlpha +
          255 * (255 - referenceAlpha) -
          (actualChannel * actualAlpha + 255 * (255 - actualAlpha)),
      ) / 255;
    maximum = Math.max(maximum, blackDelta, whiteDelta);
  }

  return maximum;
}

function intersectionOverUnion(first, second) {
  const intersectionWidth = Math.max(
    0,
    Math.min(first.x + first.width, second.x + second.width) -
      Math.max(first.x, second.x),
  );
  const intersectionHeight = Math.max(
    0,
    Math.min(first.y + first.height, second.y + second.height) -
      Math.max(first.y, second.y),
  );
  const intersectionArea = intersectionWidth * intersectionHeight;
  if (intersectionArea === 0) return 0;
  return (
    intersectionArea /
    (first.width * first.height +
      second.width * second.height -
      intersectionArea)
  );
}

export function selectVisualDifferenceCandidates({
  tileScores,
  width,
  height,
  activePixelCount,
  tileSize = VISUAL_DETAIL_TILE_SIZE,
  cropSize = VISUAL_DETAIL_CROP_SIZE,
  iouThreshold = VISUAL_DETAIL_IOU_THRESHOLD,
  limit = VISUAL_DETAIL_LIMIT,
}) {
  const tileColumns = Math.ceil(width / tileSize);
  const expectedTileCount = tileColumns * Math.ceil(height / tileSize);
  if (tileScores.length !== expectedTileCount) {
    throw new Error(`expected ${expectedTileCount} visual detail tile scores`);
  }

  const scoredTiles = [];
  for (let tileIndex = 0; tileIndex < tileScores.length; tileIndex += 1) {
    const score = tileScores[tileIndex];
    if (score <= 0) continue;
    scoredTiles.push({
      score,
      x: (tileIndex % tileColumns) * tileSize,
      y: Math.floor(tileIndex / tileColumns) * tileSize,
    });
  }
  scoredTiles.sort(
    (first, second) =>
      second.score - first.score || first.y - second.y || first.x - second.x,
  );

  const candidates = [];
  const candidateWidth = Math.min(cropSize, width);
  const candidateHeight = Math.min(cropSize, height);
  for (const tile of scoredTiles) {
    const seedX = tile.x + Math.floor(Math.min(tileSize, width - tile.x) / 2);
    const seedY = tile.y + Math.floor(Math.min(tileSize, height - tile.y) / 2);
    const candidate = {
      x: Math.max(
        0,
        Math.min(
          width - candidateWidth,
          Math.floor(seedX - candidateWidth / 2),
        ),
      ),
      y: Math.max(
        0,
        Math.min(
          height - candidateHeight,
          Math.floor(seedY - candidateHeight / 2),
        ),
      ),
      width: candidateWidth,
      height: candidateHeight,
    };
    if (
      candidates.some(
        (selected) => intersectionOverUnion(candidate, selected) > iouThreshold,
      )
    ) {
      continue;
    }
    candidates.push(candidate);
    if (candidates.length === limit) break;
  }

  const activeRatio = activePixelCount / (width * height);
  return {
    activePixelCount,
    activeRatio,
    broadDifference: activeRatio >= VISUAL_DETAIL_BROAD_RATIO,
    candidates,
  };
}

export function findVisualDifferenceCandidates({
  referenceData,
  actualData,
  width,
  height,
  threshold = VISUAL_DETAIL_DEFAULT_THRESHOLD,
}) {
  if (
    !Number.isInteger(width) ||
    !Number.isInteger(height) ||
    width < 1 ||
    height < 1
  ) {
    throw new Error("visual detail dimensions must be positive integers");
  }
  const expectedDataLength = width * height * 4;
  if (
    referenceData.length !== expectedDataLength ||
    actualData.length !== expectedDataLength
  ) {
    throw new Error(
      `visual detail pixel data must contain ${expectedDataLength} values`,
    );
  }
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 255) {
    throw new Error("visual detail threshold must be between 0 and 255");
  }

  const tileColumns = Math.ceil(width / VISUAL_DETAIL_TILE_SIZE);
  const tileScores = new Float64Array(
    tileColumns * Math.ceil(height / VISUAL_DETAIL_TILE_SIZE),
  );
  let activePixelCount = 0;
  for (let index = 0; index < referenceData.length; index += 4) {
    const delta = visiblePixelDelta(referenceData, actualData, index);
    if (delta <= threshold) continue;
    activePixelCount += 1;
    const pixelIndex = index / 4;
    const x = pixelIndex % width;
    const y = Math.floor(pixelIndex / width);
    const tileIndex =
      Math.floor(y / VISUAL_DETAIL_TILE_SIZE) * tileColumns +
      Math.floor(x / VISUAL_DETAIL_TILE_SIZE);
    tileScores[tileIndex] += delta - threshold;
  }

  return selectVisualDifferenceCandidates({
    tileScores,
    width,
    height,
    activePixelCount,
  });
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
