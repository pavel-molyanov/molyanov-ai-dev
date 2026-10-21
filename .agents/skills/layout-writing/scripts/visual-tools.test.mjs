import test from "node:test";
import assert from "node:assert/strict";

import {
  assertMatchingDimensions,
  buildScrollPlan,
  parseExpectedFont,
  parseViewportList,
  platformFontMatches,
  safeFileStem,
} from "./visual-tools.mjs";

test("parseViewportList rejects missing or empty viewport input", () => {
  for (const value of [undefined, null, "", "   ", ","]) {
    assert.throws(
      () => parseViewportList(value),
      /viewport list is required/i,
      String(value),
    );
  }
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
