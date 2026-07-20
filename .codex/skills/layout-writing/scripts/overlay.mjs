#!/usr/bin/env node

import {
  accessSync,
  constants,
  lstatSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  rmSync,
} from "node:fs";
import { basename, extname, join, resolve } from "node:path";
import { parseArgs } from "node:util";

import {
  assertMatchingDimensions,
  loadPlaywright,
  selectVisualDifferenceCandidates,
  visiblePixelDelta,
  VISUAL_DETAIL_BROAD_RATIO,
  VISUAL_DETAIL_DEFAULT_THRESHOLD,
  VISUAL_DETAIL_LIMIT,
  VISUAL_DETAIL_TILE_SIZE,
} from "./visual-tools.mjs";

const BASELINE_OUTPUT_NAMES = ["overlay.png", "diff.png"];
const LEGACY_OUTPUT_NAMES = ["side.png"];
const DETAIL_OUTPUT_NAMES = [
  "details-overview.png",
  ...Array.from(
    { length: VISUAL_DETAIL_LIMIT },
    (_, index) => `details-candidate-${String(index + 1).padStart(2, "0")}.png`,
  ),
];
const PART_COUNT = 3;
const PART_OUTPUT_NAMES = Array.from({ length: PART_COUNT }, (_, index) => {
  const number = String(index + 1).padStart(2, "0");
  return [
    `part-${number}-reference.png`,
    `part-${number}-actual.png`,
    `part-${number}-difference.png`,
    `part-${number}-overlay.png`,
  ];
}).flat();
const OWNED_OUTPUT_NAMES = [
  ...BASELINE_OUTPUT_NAMES,
  ...LEGACY_OUTPUT_NAMES,
  ...DETAIL_OUTPUT_NAMES,
  ...PART_OUTPUT_NAMES,
];

function imageDataUrl(path) {
  const extension = extname(path).toLowerCase();
  const mime =
    extension === ".jpg" || extension === ".jpeg" ? "image/jpeg" : "image/png";
  return `data:${mime};base64,${readFileSync(path).toString("base64")}`;
}

function canonicalInputPath(path, label) {
  const absolutePath = resolve(path);
  try {
    return realpathSync(absolutePath);
  } catch (error) {
    throw new Error(
      `cannot resolve ${label} input ${absolutePath}: ${error.message}`,
    );
  }
}

function existingOutputStatus(path) {
  try {
    return lstatSync(path);
  } catch (error) {
    if (error.code === "ENOENT") return null;
    throw new Error(`cannot inspect owned output ${path}: ${error.message}`);
  }
}

function prepareOverlayOutput({ out, reference, actual }) {
  const requestedOutDir = resolve(out);
  try {
    mkdirSync(requestedOutDir, { recursive: true });
  } catch (error) {
    throw new Error(
      `cannot prepare output directory ${requestedOutDir}: ${error.message}`,
    );
  }

  let outDir;
  try {
    outDir = realpathSync(requestedOutDir);
    if (!lstatSync(outDir).isDirectory()) {
      throw new Error("path is not a directory");
    }
    accessSync(outDir, constants.W_OK);
  } catch (error) {
    throw new Error(
      `cannot use output directory ${requestedOutDir}: ${error.message}`,
    );
  }

  const inputs = [
    { label: "reference", path: canonicalInputPath(reference, "reference") },
    { label: "actual", path: canonicalInputPath(actual, "actual") },
  ];
  const ownedOutputs = OWNED_OUTPUT_NAMES.map((name) => ({
    name,
    path: join(outDir, name),
  }));

  for (const output of ownedOutputs) {
    if (existingOutputStatus(output.path)?.isSymbolicLink()) {
      throw new Error(
        `owned output ${output.name} is a symbolic link; refusing to overwrite it`,
      );
    }
  }
  for (const input of inputs) {
    const collision = ownedOutputs.find((output) => output.path === input.path);
    if (collision) {
      throw new Error(
        `${input.label} input collides with owned output ${basename(collision.path)}`,
      );
    }
  }

  for (const name of DETAIL_OUTPUT_NAMES) {
    const path = join(outDir, name);
    try {
      rmSync(path, { force: true });
    } catch (error) {
      throw new Error(
        `cannot remove stale detail output ${path}: ${error.message}`,
      );
    }
  }

  return {
    outDir,
    referencePath: inputs[0].path,
    actualPath: inputs[1].path,
  };
}

function clearOwnedOutputs(outDir) {
  for (const name of OWNED_OUTPUT_NAMES) {
    const path = join(outDir, name);
    try {
      rmSync(path, { force: true });
    } catch (error) {
      throw new Error(
        `cannot remove stale output ${path}: ${error.message}`,
      );
    }
  }
}

async function main() {
  const { values } = parseArgs({
    options: {
      reference: { type: "string" },
      actual: { type: "string" },
      out: { type: "string", default: "layout-evidence/overlay" },
      "project-root": { type: "string", default: process.cwd() },
      opacity: { type: "string", default: "0.5" },
      details: { type: "boolean", default: false },
      parts: { type: "string" },
      threshold: {
        type: "string",
        default: String(VISUAL_DETAIL_DEFAULT_THRESHOLD),
      },
    },
  });
  if (!values.reference || !values.actual) {
    throw new Error(
      "usage: overlay.mjs --reference <image> --actual <image> --project-root <repo> [--parts 3]",
    );
  }

  const opacity = Number(values.opacity);
  if (!Number.isFinite(opacity) || opacity < 0 || opacity > 1) {
    throw new Error("--opacity must be between 0 and 1");
  }
  const threshold = Number(values.threshold);
  if (!Number.isFinite(threshold) || threshold < 0 || threshold > 255) {
    throw new Error("--threshold must be between 0 and 255");
  }
  const parts = values.parts === undefined ? null : Number(values.parts);
  if (parts !== null && parts !== PART_COUNT) {
    throw new Error(`--parts supports exactly ${PART_COUNT} parts`);
  }
  if (parts !== null && values.details) {
    throw new Error("--parts and --details are separate modes");
  }

  const { outDir, referencePath, actualPath } = prepareOverlayOutput({
    out: values.out,
    reference: values.reference,
    actual: values.actual,
  });
  const playwright = loadPlaywright(values["project-root"]);
  const browser = await playwright.chromium.launch();

  try {
    const page = await browser.newPage({ deviceScaleFactor: 1 });
    await page.setContent(`
      <!doctype html>
      <style>html,body{margin:0;background:#111}canvas{display:block}</style>
      <img id="reference" hidden src="${imageDataUrl(referencePath)}">
      <img id="actual" hidden src="${imageDataUrl(actualPath)}">
      <canvas id="overlay"></canvas>
      <canvas id="diff"></canvas>
      <canvas id="side"></canvas>
      <canvas id="part"></canvas>
    `);
    await page.waitForFunction(() =>
      [...document.images].every(
        (image) => image.complete && image.naturalWidth > 0,
      ),
    );

    const dimensions = await page.evaluate(() => ({
      reference: {
        width: document.querySelector("#reference").naturalWidth,
        height: document.querySelector("#reference").naturalHeight,
      },
      actual: {
        width: document.querySelector("#actual").naturalWidth,
        height: document.querySelector("#actual").naturalHeight,
      },
    }));
    assertMatchingDimensions(dimensions.reference, dimensions.actual);
    if (parts !== null && dimensions.reference.height < parts) {
      throw new Error(
        `--parts ${parts} requires images at least ${parts}px high`,
      );
    }
    clearOwnedOutputs(outDir);

    const detailData = await page.evaluate(
      ({
        detailsEnabled,
        opacityValue,
        thresholdValue,
        tileSize,
        visibleDeltaFunction,
      }) => {
        const reference = document.querySelector("#reference");
        const actual = document.querySelector("#actual");
        const width = reference.naturalWidth;
        const height = reference.naturalHeight;
        const tileColumns = Math.ceil(width / tileSize);
        const tileScores = detailsEnabled
          ? new Array(tileColumns * Math.ceil(height / tileSize)).fill(0)
          : null;
        const calculateVisibleDelta = detailsEnabled
          ? globalThis.eval(`(${visibleDeltaFunction})`)
          : null;
        let activePixelCount = 0;

        const overlay = document.querySelector("#overlay");
        overlay.width = width;
        overlay.height = height;
        const overlayContext = overlay.getContext("2d");
        overlayContext.drawImage(actual, 0, 0);
        overlayContext.globalAlpha = opacityValue;
        overlayContext.drawImage(reference, 0, 0);
        overlayContext.globalAlpha = 1;

        const source = document.createElement("canvas");
        source.width = width;
        source.height = height;
        const sourceContext = source.getContext("2d");
        sourceContext.drawImage(reference, 0, 0);
        const referenceData = sourceContext.getImageData(
          0,
          0,
          width,
          height,
        ).data;
        sourceContext.clearRect(0, 0, width, height);
        sourceContext.drawImage(actual, 0, 0);
        const actualData = sourceContext.getImageData(0, 0, width, height).data;

        const diff = document.querySelector("#diff");
        diff.width = width;
        diff.height = height;
        const diffContext = diff.getContext("2d");
        const diffImage = diffContext.createImageData(width, height);
        for (let index = 0; index < referenceData.length; index += 4) {
          const red = Math.abs(referenceData[index] - actualData[index]);
          const green = Math.abs(
            referenceData[index + 1] - actualData[index + 1],
          );
          const blue = Math.abs(
            referenceData[index + 2] - actualData[index + 2],
          );
          const alpha = Math.abs(
            referenceData[index + 3] - actualData[index + 3],
          );
          const maximum = Math.max(red, green, blue, alpha);
          diffImage.data[index] = maximum;
          diffImage.data[index + 1] = 0;
          diffImage.data[index + 2] = 0;
          diffImage.data[index + 3] = 255;
          if (detailsEnabled) {
            const visibleDelta = calculateVisibleDelta(
              referenceData,
              actualData,
              index,
            );
            if (visibleDelta > thresholdValue) {
              activePixelCount += 1;
              const pixelIndex = index / 4;
              const x = pixelIndex % width;
              const y = Math.floor(pixelIndex / width);
              const tileIndex =
                Math.floor(y / tileSize) * tileColumns +
                Math.floor(x / tileSize);
              tileScores[tileIndex] += visibleDelta - thresholdValue;
            }
          }
        }
        diffContext.putImageData(diffImage, 0, 0);

        return detailsEnabled ? { activePixelCount, tileScores } : null;
      },
      {
        detailsEnabled: values.details,
        opacityValue: opacity,
        thresholdValue: threshold,
        tileSize: VISUAL_DETAIL_TILE_SIZE,
        visibleDeltaFunction: visiblePixelDelta.toString(),
      },
    );

    if (parts !== null) {
      for (let index = 0; index < parts; index += 1) {
        const number = String(index + 1).padStart(2, "0");
        for (const [source, suffix] of [
          ["reference", "reference"],
          ["actual", "actual"],
          ["diff", "difference"],
          ["overlay", "overlay"],
        ]) {
          await page.evaluate(
            ({ indexValue, partsValue, sourceId }) => {
              const sourceCanvas = document.querySelector(`#${sourceId}`);
              const sourceHeight =
                sourceCanvas.naturalHeight || sourceCanvas.height;
              const sourceWidth =
                sourceCanvas.naturalWidth || sourceCanvas.width;
              const startY = Math.floor(
                (indexValue * sourceHeight) / partsValue,
              );
              const endY = Math.floor(
                ((indexValue + 1) * sourceHeight) / partsValue,
              );
              const partCanvas = document.querySelector("#part");
              partCanvas.width = sourceWidth;
              partCanvas.height = endY - startY;
              partCanvas
                .getContext("2d")
                .drawImage(
                  sourceCanvas,
                  0,
                  startY,
                  sourceWidth,
                  partCanvas.height,
                  0,
                  0,
                  sourceWidth,
                  partCanvas.height,
                );
            },
            { indexValue: index, partsValue: parts, sourceId: source },
          );
          await page.locator("#part").screenshot({
            path: join(outDir, `part-${number}-${suffix}.png`),
          });
        }
      }
      console.log(
        `[overlay] wrote ${parts} separate reference, actual, difference, and overlay sets to ${outDir}`,
      );
      return;
    }

    for (const name of ["overlay", "diff"]) {
      await page
        .locator(`#${name}`)
        .screenshot({ path: join(outDir, `${name}.png`) });
    }
    console.log(`[overlay] wrote overlay and diff images to ${outDir}`);

    if (values.details) {
      const result = selectVisualDifferenceCandidates({
        ...detailData,
        width: dimensions.reference.width,
        height: dimensions.reference.height,
      });
      await page.evaluate((candidates) => {
        const overview = document.querySelector("#side");
        const source = document.querySelector("#overlay");
        overview.width = source.width;
        overview.height = source.height;
        const context = overview.getContext("2d");
        context.drawImage(source, 0, 0);
        context.font = "bold 16px sans-serif";
        context.textBaseline = "top";
        candidates.forEach((candidate, index) => {
          context.strokeStyle = "#ff2b2b";
          context.lineWidth = 2;
          context.strokeRect(
            candidate.x + 1,
            candidate.y + 1,
            Math.max(0, candidate.width - 2),
            Math.max(0, candidate.height - 2),
          );
          const label = String(index + 1);
          const labelWidth = context.measureText(label).width + 10;
          context.fillStyle = "#ff2b2b";
          context.fillRect(candidate.x + 1, candidate.y + 1, labelWidth, 24);
          context.fillStyle = "#fff";
          context.fillText(label, candidate.x + 6, candidate.y + 4);
        });
      }, result.candidates);
      await page
        .locator("#side")
        .screenshot({ path: join(outDir, "details-overview.png") });

      for (let index = 0; index < result.candidates.length; index += 1) {
        await page.evaluate((candidate) => {
          const sheet = document.querySelector("#side");
          const reference = document.querySelector("#reference");
          const actual = document.querySelector("#actual");
          const overlay = document.querySelector("#overlay");
          const diff = document.querySelector("#diff");
          sheet.width = candidate.width * 2;
          sheet.height = candidate.height * 2;
          const context = sheet.getContext("2d");
          context.imageSmoothingEnabled = false;
          const panels = [
            { source: reference, x: 0, y: 0, label: "reference" },
            { source: actual, x: candidate.width, y: 0, label: "actual" },
            { source: overlay, x: 0, y: candidate.height, label: "overlay" },
            {
              source: diff,
              x: candidate.width,
              y: candidate.height,
              label: "diff",
            },
          ];
          for (const panel of panels) {
            context.drawImage(
              panel.source,
              candidate.x,
              candidate.y,
              candidate.width,
              candidate.height,
              panel.x,
              panel.y,
              candidate.width,
              candidate.height,
            );
            context.font = "bold 14px sans-serif";
            context.textBaseline = "top";
            const labelWidth = context.measureText(panel.label).width + 12;
            context.fillStyle = "rgba(0,0,0,0.75)";
            context.fillRect(panel.x, panel.y, labelWidth, 22);
            context.fillStyle = "#fff";
            context.fillText(panel.label, panel.x + 6, panel.y + 3);
          }
        }, result.candidates[index]);
        const number = String(index + 1).padStart(2, "0");
        await page.locator("#side").screenshot({
          path: join(outDir, `details-candidate-${number}.png`),
        });
      }

      if (result.broadDifference) {
        console.warn(
          `[overlay] broad difference warning: ${(result.activeRatio * 100).toFixed(1)}% of pixels ` +
            `exceed ${threshold}/255 (warning at ${VISUAL_DETAIL_BROAD_RATIO * 100}%); ` +
            "inspect the full-size comparison as the source of truth",
        );
      }
      console.log(
        `[overlay] wrote details overview and ${result.candidates.length} candidate sheet(s) to ${outDir}`,
      );
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`[overlay] ${error.message}`);
  process.exitCode = 1;
});
