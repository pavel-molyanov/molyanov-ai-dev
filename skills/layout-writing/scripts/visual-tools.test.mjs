import test from "node:test";
import assert from "node:assert/strict";

import {
  assertMatchingDimensions,
  buildScrollPlan,
  findVisualDifferenceCandidates,
  parseExpectedFont,
  parseViewportList,
  platformFontMatches,
  safeFileStem,
  selectVisualDifferenceCandidates,
  VISUAL_DETAIL_BROAD_RATIO,
  VISUAL_DETAIL_CROP_SIZE,
  VISUAL_DETAIL_DEFAULT_THRESHOLD,
  VISUAL_DETAIL_IOU_THRESHOLD,
  VISUAL_DETAIL_LIMIT,
  VISUAL_DETAIL_TILE_SIZE,
} from "./visual-tools.mjs";

function createImage(width, height, color = [0, 0, 0, 255]) {
  const data = new Uint8ClampedArray(width * height * 4);
  for (let index = 0; index < data.length; index += 4) {
    data.set(color, index);
  }
  return data;
}

function paintRectangle(data, width, bounds, color) {
  for (let y = bounds.y; y < bounds.y + bounds.height; y += 1) {
    for (let x = bounds.x; x < bounds.x + bounds.width; x += 1) {
      data.set(color, (y * width + x) * 4);
    }
  }
}

test("parseViewportList uses the layout-writing baseline by default", () => {
  assert.deepEqual(parseViewportList(), [
    { width: 375, height: 812 },
    { width: 1440, height: 900 },
  ]);
});

test("parseViewportList accepts a compact comma-separated list", () => {
  assert.deepEqual(parseViewportList("393x852, 1600x1000"), [
    { width: 393, height: 852 },
    { width: 1600, height: 1000 },
  ]);
});

test("parseViewportList rejects malformed and unsafe viewport values", () => {
  for (const value of ["375", "0x900", "1440x-1", "wide", "10001x900"]) {
    assert.throws(() => parseViewportList(value), /viewport/i, value);
  }
});

test("safeFileStem creates stable screenshot names", () => {
  assert.equal(safeFileStem("Hero / Main: desktop"), "hero-main-desktop");
  assert.equal(safeFileStem("  "), "capture");
});

test("assertMatchingDimensions preserves exact comparison", () => {
  assert.doesNotThrow(() =>
    assertMatchingDimensions(
      { width: 1440, height: 900 },
      { width: 1440, height: 900 },
    ),
  );

  assert.throws(
    () =>
      assertMatchingDimensions(
        { width: 1600, height: 900 },
        { width: 1440, height: 900 },
      ),
    /same dimensions/i,
  );
});

test("buildScrollPlan covers the scope without jumps larger than the requested step", () => {
  assert.deepEqual(buildScrollPlan(100, 900, 300), {
    positions: [100, 400, 700, 900],
    complete: true,
  });

  const tall = buildScrollPlan(0, 100_000, 600, 100);
  assert.equal(tall.positions[0], 0);
  assert.equal(tall.positions.at(-1), 59_400);
  assert.equal(tall.positions.length, 100);
  assert.equal(tall.complete, false);
  assert.ok(
    tall.positions.every(
      (position, index) =>
        index === 0 || position - tall.positions[index - 1] <= 600,
    ),
  );
});

test("parseExpectedFont creates a compact exact-font requirement", () => {
  assert.deepEqual(parseExpectedFont("Inter Runtime|700|italic|h1|Inter"), {
    family: "Inter Runtime",
    weight: "700",
    style: "italic",
    selector: "h1",
    platformFamily: "Inter",
  });
  assert.deepEqual(parseExpectedFont("Inter|700|italic"), {
    family: "Inter",
    weight: "700",
    style: "italic",
  });
  assert.deepEqual(parseExpectedFont("Geologica"), {
    family: "Geologica",
    weight: "400",
    style: "normal",
  });
  assert.throws(() => parseExpectedFont("|700"), /font/i);
});

test("platformFontMatches distinguishes a real system family from fallback", () => {
  assert.equal(platformFontMatches("Arial", "Arial"), true);
  assert.equal(platformFontMatches("Arial", "ArialMT"), true);
  assert.equal(platformFontMatches("MissingFont", "Arial"), false);
});

test("findVisualDifferenceCandidates returns no candidates for identical pixels", () => {
  const referenceData = createImage(64, 64, [24, 48, 72, 255]);

  assert.deepEqual(
    findVisualDifferenceCandidates({
      referenceData,
      actualData: referenceData.slice(),
      width: 64,
      height: 64,
    }),
    {
      activePixelCount: 0,
      activeRatio: 0,
      broadDifference: false,
      candidates: [],
    },
  );
});

test("visual detail defaults preserve the approved native-pixel contract", () => {
  assert.equal(VISUAL_DETAIL_DEFAULT_THRESHOLD, 16);
  assert.equal(VISUAL_DETAIL_TILE_SIZE, 32);
  assert.equal(VISUAL_DETAIL_CROP_SIZE, 256);
  assert.equal(VISUAL_DETAIL_IOU_THRESHOLD, 0.25);
  assert.equal(VISUAL_DETAIL_LIMIT, 5);
  assert.equal(VISUAL_DETAIL_BROAD_RATIO, 0.5);
});

test("findVisualDifferenceCandidates ignores sub-threshold pixels and bounds a compact difference", () => {
  const width = 400;
  const height = 300;
  const referenceData = createImage(width, height);
  const actualData = createImage(width, height, [15, 15, 15, 255]);
  paintRectangle(
    actualData,
    width,
    { x: 8, y: 10, width: 10, height: 10 },
    [32, 32, 32, 255],
  );

  const result = findVisualDifferenceCandidates({
    referenceData,
    actualData,
    width,
    height,
  });

  assert.equal(result.activePixelCount, 100);
  assert.equal(result.broadDifference, false);
  assert.deepEqual(result.candidates, [
    { x: 0, y: 0, width: 256, height: 256 },
  ]);
});

test("findVisualDifferenceCandidates orders separated regions stably and suppresses overlapping seeds", () => {
  const width = 800;
  const height = 400;
  const referenceData = createImage(width, height);
  const actualData = referenceData.slice();
  paintRectangle(
    actualData,
    width,
    { x: 64, y: 64, width: 64, height: 64 },
    [64, 64, 64, 255],
  );
  paintRectangle(
    actualData,
    width,
    { x: 672, y: 256, width: 64, height: 64 },
    [64, 64, 64, 255],
  );

  const result = findVisualDifferenceCandidates({
    referenceData,
    actualData,
    width,
    height,
  });

  assert.equal(result.activePixelCount, 8_192);
  assert.deepEqual(result.candidates, [
    { x: 0, y: 0, width: 256, height: 256 },
    { x: 544, y: 144, width: 256, height: 256 },
  ]);
});

test("findVisualDifferenceCandidates ignores RGB hidden by full transparency", () => {
  const hidden = findVisualDifferenceCandidates({
    referenceData: Uint8ClampedArray.from([255, 0, 0, 0]),
    actualData: Uint8ClampedArray.from([0, 255, 0, 0]),
    width: 1,
    height: 1,
  });

  assert.equal(hidden.activePixelCount, 0);
});

test("findVisualDifferenceCandidates checks visibility on both black and white backgrounds", () => {
  const differsOnlyOnWhite = findVisualDifferenceCandidates({
    referenceData: Uint8ClampedArray.from([0, 0, 0, 0]),
    actualData: Uint8ClampedArray.from([0, 0, 0, 255]),
    width: 1,
    height: 1,
  });
  const differsOnlyOnBlack = findVisualDifferenceCandidates({
    referenceData: Uint8ClampedArray.from([255, 255, 255, 255]),
    actualData: Uint8ClampedArray.from([0, 0, 0, 0]),
    width: 1,
    height: 1,
  });

  assert.equal(differsOnlyOnWhite.activePixelCount, 1);
  assert.equal(differsOnlyOnBlack.activePixelCount, 1);
});

test("findVisualDifferenceCandidates uses a strict 16/255 default threshold", () => {
  const referenceData = Uint8ClampedArray.from([0, 0, 0, 0]);
  const atThreshold = findVisualDifferenceCandidates({
    referenceData,
    actualData: Uint8ClampedArray.from([0, 0, 0, 16]),
    width: 1,
    height: 1,
  });
  const aboveThreshold = findVisualDifferenceCandidates({
    referenceData,
    actualData: Uint8ClampedArray.from([0, 0, 0, 17]),
    width: 1,
    height: 1,
  });
  const raisedThreshold = findVisualDifferenceCandidates({
    referenceData,
    actualData: Uint8ClampedArray.from([0, 0, 0, 17]),
    width: 1,
    height: 1,
    threshold: 17,
  });

  assert.equal(atThreshold.activePixelCount, 0);
  assert.equal(aboveThreshold.activePixelCount, 1);
  assert.equal(raisedThreshold.activePixelCount, 0);
});

test("selectVisualDifferenceCandidates applies score, y, and x order before limiting to five", () => {
  const width = 2_048;
  const height = 640;
  const tileColumns = width / 32;
  const tileScores = new Float64Array(tileColumns * Math.ceil(height / 32));
  const setScore = (x, y, score) => {
    tileScores[(y / 32) * tileColumns + x / 32] = score;
  };
  setScore(0, 320, 100);
  setScore(320, 0, 80);
  setScore(640, 320, 80);
  setScore(960, 320, 80);
  setScore(1_280, 0, 70);
  setScore(1_600, 0, 60);

  const result = selectVisualDifferenceCandidates({
    tileScores,
    width,
    height,
    activePixelCount: 6,
  });

  assert.deepEqual(result.candidates, [
    { x: 0, y: 208, width: 256, height: 256 },
    { x: 208, y: 0, width: 256, height: 256 },
    { x: 528, y: 208, width: 256, height: 256 },
    { x: 848, y: 208, width: 256, height: 256 },
    { x: 1_168, y: 0, width: 256, height: 256 },
  ]);
});

test("selectVisualDifferenceCandidates suppresses IoU above 0.25 but keeps a region below it", () => {
  const width = 1_000;
  const height = 300;
  const tileColumns = Math.ceil(width / 32);
  const tileScores = new Float64Array(tileColumns * Math.ceil(height / 32));
  tileScores[8] = 100;
  tileScores[12] = 90;
  tileScores[13] = 80;

  const result = selectVisualDifferenceCandidates({
    tileScores,
    width,
    height,
    activePixelCount: 3,
  });

  assert.deepEqual(result.candidates, [
    { x: 144, y: 0, width: 256, height: 256 },
    { x: 304, y: 0, width: 256, height: 256 },
  ]);
});

test("findVisualDifferenceCandidates warns through data for a broad uniform difference", () => {
  const width = 100;
  const height = 100;
  const result = findVisualDifferenceCandidates({
    referenceData: createImage(width, height),
    actualData: createImage(width, height, [255, 255, 255, 255]),
    width,
    height,
  });

  assert.equal(result.activePixelCount, 10_000);
  assert.equal(result.activeRatio, 1);
  assert.equal(result.broadDifference, true);
});

test("selectVisualDifferenceCandidates marks broad difference at half of all pixels", () => {
  const below = selectVisualDifferenceCandidates({
    tileScores: [0],
    width: 10,
    height: 10,
    activePixelCount: 49,
  });
  const atBoundary = selectVisualDifferenceCandidates({
    tileScores: [0],
    width: 10,
    height: 10,
    activePixelCount: 50,
  });

  assert.equal(below.broadDifference, false);
  assert.equal(atBoundary.broadDifference, true);
});
