import test from "node:test";
import assert from "node:assert/strict";
import {
  access,
  mkdtemp,
  mkdir,
  readFile,
  readdir,
  rm,
  writeFile,
} from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";
import { deflateSync, inflateSync } from "node:zlib";

const playwrightProjectRoot = process.env.LAYOUT_WRITING_TEST_PROJECT_ROOT;

function crc32(buffer) {
  let crc = 0xffffffff;
  for (const byte of buffer) {
    crc ^= byte;
    for (let bit = 0; bit < 8; bit += 1) {
      crc = (crc >>> 1) ^ (crc & 1 ? 0xedb88320 : 0);
    }
  }
  return (crc ^ 0xffffffff) >>> 0;
}

function pngChunk(type, data) {
  const typeBuffer = Buffer.from(type);
  const length = Buffer.alloc(4);
  length.writeUInt32BE(data.length);
  const checksum = Buffer.alloc(4);
  checksum.writeUInt32BE(crc32(Buffer.concat([typeBuffer, data])));
  return Buffer.concat([length, typeBuffer, data, checksum]);
}

function createPng(width, height, pixelAt) {
  const header = Buffer.alloc(13);
  header.writeUInt32BE(width, 0);
  header.writeUInt32BE(height, 4);
  header.set([8, 6, 0, 0, 0], 8);
  const rows = [];
  for (let y = 0; y < height; y += 1) {
    const row = Buffer.alloc(1 + width * 4);
    for (let x = 0; x < width; x += 1) row.set(pixelAt(x, y), 1 + x * 4);
    rows.push(row);
  }
  return Buffer.concat([
    Buffer.from("89504e470d0a1a0a", "hex"),
    pngChunk("IHDR", header),
    pngChunk("IDAT", deflateSync(Buffer.concat(rows))),
    pngChunk("IEND", Buffer.alloc(0)),
  ]);
}

function decodePng(buffer) {
  let offset = 8;
  let width;
  let height;
  let bytesPerPixel;
  const compressedParts = [];
  while (offset < buffer.length) {
    const length = buffer.readUInt32BE(offset);
    const type = buffer.toString("ascii", offset + 4, offset + 8);
    const data = buffer.subarray(offset + 8, offset + 8 + length);
    if (type === "IHDR") {
      width = data.readUInt32BE(0);
      height = data.readUInt32BE(4);
      bytesPerPixel = data[9] === 6 ? 4 : 3;
    } else if (type === "IDAT") {
      compressedParts.push(data);
    }
    offset += length + 12;
  }
  const raw = inflateSync(Buffer.concat(compressedParts));
  const stride = width * bytesPerPixel;
  const pixels = Buffer.alloc(stride * height);
  let rawOffset = 0;
  for (let y = 0; y < height; y += 1) {
    const filter = raw[rawOffset++];
    const rowOffset = y * stride;
    for (let x = 0; x < stride; x += 1) {
      const encoded = raw[rawOffset + x];
      const left = x >= bytesPerPixel ? pixels[rowOffset + x - bytesPerPixel] : 0;
      const above = y > 0 ? pixels[rowOffset + x - stride] : 0;
      const upperLeft =
        y > 0 && x >= bytesPerPixel
          ? pixels[rowOffset + x - stride - bytesPerPixel]
          : 0;
      const prediction = left + above - upperLeft;
      const paeth =
        Math.abs(prediction - left) <= Math.abs(prediction - above) &&
        Math.abs(prediction - left) <= Math.abs(prediction - upperLeft)
          ? left
          : Math.abs(prediction - above) <= Math.abs(prediction - upperLeft)
            ? above
            : upperLeft;
      const predictor = [0, left, above, Math.floor((left + above) / 2), paeth][filter];
      pixels[rowOffset + x] = (encoded + predictor) & 0xff;
    }
    rawOffset += stride;
  }
  return { width, height };
}

function runOverlay(args) {
  return new Promise((resolve) => {
    const child = spawn(
      process.execPath,
      [new URL("./overlay.mjs", import.meta.url).pathname, ...args],
      { stdio: ["ignore", "pipe", "pipe"] },
    );
    let output = "";
    child.stdout.on("data", (chunk) => (output += chunk));
    child.stderr.on("data", (chunk) => (output += chunk));
    child.on("close", (exitCode) => resolve({ exitCode, output }));
  });
}

test("overlay CLI requires an explicit output target", async () => {
  const result = await runOverlay([
    "--reference",
    "reference.png",
    "--actual",
    "actual.png",
  ]);
  assert.notEqual(result.exitCode, 0, result.output);
  assert.match(result.output, /--out <new-path>/i);
});

test("overlay CLI accepts only the supported three-part mode", async () => {
  const result = await runOverlay([
    "--reference",
    "reference.png",
    "--actual",
    "actual.png",
    "--out",
    "unused-output",
    "--parts",
    "2",
  ]);
  assert.notEqual(result.exitCode, 0, result.output);
  assert.match(result.output, /--parts supports exactly 3 parts/i);
});

test("overlay CLI rejects an existing output target without modifying it", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const outDir = join(temporaryRoot, "out");
  const sentinelPath = join(outDir, "sentinel.txt");
  const referencePath = join(temporaryRoot, "reference.png");
  const actualPath = join(temporaryRoot, "actual.png");
  try {
    await mkdir(outDir);
    await writeFile(sentinelPath, "keep");
    await writeFile(referencePath, createPng(1, 1, () => [0, 0, 0, 255]));
    await writeFile(actualPath, createPng(1, 1, () => [1, 1, 1, 255]));
    const result = await runOverlay([
      "--reference",
      referencePath,
      "--actual",
      actualPath,
      "--out",
      outDir,
    ]);
    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(result.output, /output target already exists/i);
    assert.equal(await readFile(sentinelPath, "utf8"), "keep");
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test("overlay CLI atomically creates a fresh output target before launching Playwright", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const outDir = join(temporaryRoot, "fresh-out");
  const referencePath = join(temporaryRoot, "reference.png");
  const actualPath = join(temporaryRoot, "actual.png");
  const projectRoot = join(temporaryRoot, "project");
  const playwrightRoot = join(projectRoot, "node_modules", "playwright");
  const launchMarker = join(temporaryRoot, "launch-marker");
  try {
    await mkdir(playwrightRoot, { recursive: true });
    await writeFile(join(projectRoot, "package.json"), "{}");
    await writeFile(
      join(playwrightRoot, "package.json"),
      JSON.stringify({ main: "index.cjs" }),
    );
    await writeFile(
      join(playwrightRoot, "index.cjs"),
      `const fs = require("node:fs");\n` +
        `exports.chromium = { launch: async () => {\n` +
        `  fs.writeFileSync(${JSON.stringify(launchMarker)}, "launched");\n` +
        `  throw new Error("expected launch failure");\n` +
        `} };\n`,
    );
    await writeFile(referencePath, createPng(1, 1, () => [0, 0, 0, 255]));
    await writeFile(actualPath, createPng(1, 1, () => [1, 1, 1, 255]));
    const result = await runOverlay([
      "--reference",
      referencePath,
      "--actual",
      actualPath,
      "--project-root",
      projectRoot,
      "--out",
      outDir,
    ]);
    assert.notEqual(result.exitCode, 0, result.output);
    assert.equal(await readFile(launchMarker, "utf8"), "launched");
    await access(outDir);
    assert.deepEqual(await readdir(outDir), []);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test(
  "overlay CLI writes baseline and three-part evidence to separate fresh targets",
  {
    skip: playwrightProjectRoot
      ? false
      : "set LAYOUT_WRITING_TEST_PROJECT_ROOT to a Playwright project",
  },
  async () => {
    const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
    const referencePath = join(temporaryRoot, "reference.png");
    const actualPath = join(temporaryRoot, "actual.png");
    const baselineOut = join(temporaryRoot, "baseline");
    const partsOut = join(temporaryRoot, "parts");
    try {
      await writeFile(referencePath, createPng(12, 10, (x, y) => [x, y, 0, 255]));
      await writeFile(
        actualPath,
        createPng(12, 10, (x, y) => [x, y, y >= 3 && y < 6 ? 255 : 0, 255]),
      );

      const baseline = await runOverlay([
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        baselineOut,
      ]);
      assert.equal(baseline.exitCode, 0, baseline.output);
      assert.deepEqual((await readdir(baselineOut)).sort(), ["diff.png", "overlay.png"]);

      const parts = await runOverlay([
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        partsOut,
        "--parts",
        "3",
      ]);
      assert.equal(parts.exitCode, 0, parts.output);
      assert.equal((await readdir(partsOut)).length, 12);
      const expectedHeights = [3, 3, 4];
      for (let index = 0; index < expectedHeights.length; index += 1) {
        const number = String(index + 1).padStart(2, "0");
        const image = decodePng(await readFile(join(partsOut, `part-${number}-actual.png`)));
        assert.deepEqual(image, { width: 12, height: expectedHeights[index] });
      }
    } finally {
      await rm(temporaryRoot, { recursive: true, force: true });
    }
  },
);
