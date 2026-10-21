#!/usr/bin/env node

import { mkdirSync, readFileSync, realpathSync } from "node:fs";
import { extname, join, resolve } from "node:path";
import { parseArgs } from "node:util";

import { assertMatchingDimensions, loadPlaywright } from "./visual-tools.mjs";

const PART_COUNT = 3;

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

function createOutputTarget(path) {
  const outDir = resolve(path);
  try {
    mkdirSync(outDir);
  } catch (error) {
    if (error.code === "EEXIST") {
      throw new Error(`output target already exists: ${outDir}`);
    }
    throw new Error(`cannot create output target ${outDir}: ${error.message}`);
  }
  return outDir;
}

async function main() {
  const { values } = parseArgs({
    options: {
      reference: { type: "string" },
      actual: { type: "string" },
      out: { type: "string" },
      "project-root": { type: "string", default: process.cwd() },
      opacity: { type: "string", default: "0.5" },
      parts: { type: "string" },
    },
  });
  if (!values.reference || !values.actual || !values.out) {
    throw new Error(
      "usage: overlay.mjs --reference <image> --actual <image> --project-root <repo> --out <new-path> [--parts 3]",
    );
  }

  const opacity = Number(values.opacity);
  if (!Number.isFinite(opacity) || opacity < 0 || opacity > 1) {
    throw new Error("--opacity must be between 0 and 1");
  }
  const parts = values.parts === undefined ? null : Number(values.parts);
  if (parts !== null && parts !== PART_COUNT) {
    throw new Error(`--parts supports exactly ${PART_COUNT} parts`);
  }

  const referencePath = canonicalInputPath(values.reference, "reference");
  const actualPath = canonicalInputPath(values.actual, "actual");
  const outDir = createOutputTarget(values.out);
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

    await page.evaluate((opacityValue) => {
      const reference = document.querySelector("#reference");
      const actual = document.querySelector("#actual");
      const width = reference.naturalWidth;
      const height = reference.naturalHeight;

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
      const referenceData = sourceContext.getImageData(0, 0, width, height).data;
      sourceContext.clearRect(0, 0, width, height);
      sourceContext.drawImage(actual, 0, 0);
      const actualData = sourceContext.getImageData(0, 0, width, height).data;

      const diff = document.querySelector("#diff");
      diff.width = width;
      diff.height = height;
      const diffContext = diff.getContext("2d");
      const diffImage = diffContext.createImageData(width, height);
      for (let index = 0; index < referenceData.length; index += 4) {
        const maximum = Math.max(
          Math.abs(referenceData[index] - actualData[index]),
          Math.abs(referenceData[index + 1] - actualData[index + 1]),
          Math.abs(referenceData[index + 2] - actualData[index + 2]),
          Math.abs(referenceData[index + 3] - actualData[index + 3]),
        );
        diffImage.data[index] = maximum;
        diffImage.data[index + 1] = 0;
        diffImage.data[index + 2] = 0;
        diffImage.data[index + 3] = 255;
      }
      diffContext.putImageData(diffImage, 0, 0);
    }, opacity);

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
              const sourceHeight = sourceCanvas.naturalHeight || sourceCanvas.height;
              const sourceWidth = sourceCanvas.naturalWidth || sourceCanvas.width;
              const startY = Math.floor((indexValue * sourceHeight) / partsValue);
              const endY = Math.floor(((indexValue + 1) * sourceHeight) / partsValue);
              const partCanvas = document.querySelector("#part");
              partCanvas.width = sourceWidth;
              partCanvas.height = endY - startY;
              partCanvas.getContext("2d").drawImage(
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
      await page.locator(`#${name}`).screenshot({
        path: join(outDir, `${name}.png`),
      });
    }
    console.log(`[overlay] wrote overlay and diff images to ${outDir}`);
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(`[overlay] ${error.message}`);
  process.exitCode = 1;
});
