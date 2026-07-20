import test from "node:test";
import assert from "node:assert/strict";
import {
  access,
  lstat,
  mkdtemp,
  mkdir,
  readFile,
  readdir,
  rm,
  symlink,
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

function paethPredictor(left, above, upperLeft) {
  const prediction = left + above - upperLeft;
  const leftDistance = Math.abs(prediction - left);
  const aboveDistance = Math.abs(prediction - above);
  const upperLeftDistance = Math.abs(prediction - upperLeft);
  if (leftDistance <= aboveDistance && leftDistance <= upperLeftDistance)
    return left;
  return aboveDistance <= upperLeftDistance ? above : upperLeft;
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
      assert.equal(data[8], 8, "expected an 8-bit PNG");
      assert.ok(
        data[9] === 2 || data[9] === 6,
        `unsupported PNG color type ${data[9]}`,
      );
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
    const filter = raw[rawOffset];
    rawOffset += 1;
    const rowOffset = y * stride;
    for (let x = 0; x < stride; x += 1) {
      const encoded = raw[rawOffset + x];
      const left =
        x >= bytesPerPixel ? pixels[rowOffset + x - bytesPerPixel] : 0;
      const above = y > 0 ? pixels[rowOffset + x - stride] : 0;
      const upperLeft =
        y > 0 && x >= bytesPerPixel
          ? pixels[rowOffset + x - stride - bytesPerPixel]
          : 0;
      const predictor = [
        0,
        left,
        above,
        Math.floor((left + above) / 2),
        paethPredictor(left, above, upperLeft),
      ][filter];
      assert.notEqual(predictor, undefined, `unsupported PNG filter ${filter}`);
      pixels[rowOffset + x] = (encoded + predictor) & 0xff;
    }
    rawOffset += stride;
  }

  return {
    width,
    height,
    pixelAt(x, y) {
      const index = (y * width + x) * bytesPerPixel;
      return [
        pixels[index],
        pixels[index + 1],
        pixels[index + 2],
        bytesPerPixel === 4 ? pixels[index + 3] : 255,
      ];
    },
  };
}

function run(command, args) {
  return new Promise((resolve) => {
    const child = spawn(command, args, { stdio: ["ignore", "pipe", "pipe"] });
    let output = "";
    child.stdout.on("data", (chunk) => (output += chunk));
    child.stderr.on("data", (chunk) => (output += chunk));
    child.on("close", (exitCode) => resolve({ exitCode, output }));
  });
}

function runOverlay(args) {
  return run(process.execPath, [
    new URL("./overlay.mjs", import.meta.url).pathname,
    ...args,
  ]);
}

test("overlay CLI accepts only the supported three-part mode", async () => {
  const result = await runOverlay([
    "--reference",
    "reference.png",
    "--actual",
    "actual.png",
    "--parts",
    "2",
  ]);

  assert.notEqual(result.exitCode, 0, result.output);
  assert.match(result.output, /--parts supports exactly 3 parts/i);
});

test("overlay CLI rejects a stale detail used as an input before cleanup", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const outDir = join(temporaryRoot, "out");
  const staleInput = join(outDir, "details-overview.png");
  const actualPath = join(temporaryRoot, "actual.png");
  const staleContents = createPng(1, 1, () => [10, 20, 30, 255]);
  try {
    await mkdir(outDir);
    await writeFile(staleInput, staleContents);
    await writeFile(
      actualPath,
      createPng(1, 1, () => [30, 20, 10, 255]),
    );

    const result = await runOverlay([
      "--reference",
      staleInput,
      "--actual",
      actualPath,
      "--project-root",
      join(temporaryRoot, "missing-project"),
      "--out",
      outDir,
    ]);

    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(result.output, /input.*collides.*details-overview\.png/i);
    assert.deepEqual(await readFile(staleInput), staleContents);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test("overlay CLI resolves symlinked inputs and output directories for collisions", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const realOutDir = join(temporaryRoot, "real-out");
  const outAlias = join(temporaryRoot, "out-alias");
  const ownedOutput = join(realOutDir, "overlay.png");
  const inputAlias = join(temporaryRoot, "actual-alias.png");
  const referencePath = join(temporaryRoot, "reference.png");
  try {
    await mkdir(realOutDir);
    await writeFile(
      ownedOutput,
      createPng(1, 1, () => [1, 2, 3, 255]),
    );
    await writeFile(
      referencePath,
      createPng(1, 1, () => [3, 2, 1, 255]),
    );
    await symlink(realOutDir, outAlias, "dir");
    await symlink(ownedOutput, inputAlias, "file");

    const result = await runOverlay([
      "--reference",
      referencePath,
      "--actual",
      inputAlias,
      "--project-root",
      join(temporaryRoot, "missing-project"),
      "--out",
      outAlias,
    ]);

    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(result.output, /input.*collides.*overlay\.png/i);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test("overlay CLI rejects an existing owned output symlink without following it", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const outDir = join(temporaryRoot, "out");
  const targetPath = join(temporaryRoot, "target.png");
  const symlinkPath = join(outDir, "details-candidate-05.png");
  const referencePath = join(temporaryRoot, "reference.png");
  const actualPath = join(temporaryRoot, "actual.png");
  const targetContents = createPng(1, 1, () => [4, 5, 6, 255]);
  try {
    await mkdir(outDir);
    await writeFile(targetPath, targetContents);
    await symlink(targetPath, symlinkPath, "file");
    await writeFile(
      referencePath,
      createPng(1, 1, () => [0, 0, 0, 255]),
    );
    await writeFile(
      actualPath,
      createPng(1, 1, () => [1, 1, 1, 255]),
    );

    const result = await runOverlay([
      "--reference",
      referencePath,
      "--actual",
      actualPath,
      "--project-root",
      join(temporaryRoot, "missing-project"),
      "--out",
      outDir,
    ]);

    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(
      result.output,
      /owned output.*details-candidate-05\.png.*symbolic link/i,
    );
    assert.equal((await lstat(symlinkPath)).isSymbolicLink(), true);
    assert.deepEqual(await readFile(targetPath), targetContents);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test("overlay CLI prepares the output directory before Chromium launch", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
  const projectRoot = join(temporaryRoot, "project");
  const playwrightRoot = join(projectRoot, "node_modules", "playwright");
  const launchMarker = join(temporaryRoot, "chromium-launched");
  const blockedOutPath = join(temporaryRoot, "blocked-out");
  const referencePath = join(temporaryRoot, "reference.png");
  const actualPath = join(temporaryRoot, "actual.png");
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
        `  throw new Error("launch should not run");\n` +
        `} };\n`,
    );
    await writeFile(blockedOutPath, "not a directory");
    await writeFile(
      referencePath,
      createPng(1, 1, () => [0, 0, 0, 255]),
    );
    await writeFile(
      actualPath,
      createPng(1, 1, () => [1, 1, 1, 255]),
    );

    const result = await runOverlay([
      "--reference",
      referencePath,
      "--actual",
      actualPath,
      "--project-root",
      projectRoot,
      "--out",
      blockedOutPath,
    ]);

    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(result.output, /output directory/i);
    await assert.rejects(access(launchMarker));
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test(
  "overlay CLI preserves baseline outputs when a prepared run fails before screenshots",
  {
    skip: playwrightProjectRoot
      ? false
      : "set LAYOUT_WRITING_TEST_PROJECT_ROOT to a Playwright project",
  },
  async () => {
    const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
    const outDir = join(temporaryRoot, "out");
    const referencePath = join(temporaryRoot, "reference.png");
    const actualPath = join(temporaryRoot, "actual.png");
    const baselineSentinels = new Map([
      ["overlay.png", Buffer.from("overlay-sentinel")],
      ["diff.png", Buffer.from("diff-sentinel")],
    ]);
    const staleDetailNames = [
      "details-overview.png",
      "details-candidate-01.png",
      "details-candidate-02.png",
      "details-candidate-03.png",
      "details-candidate-04.png",
      "details-candidate-05.png",
    ];
    try {
      await mkdir(outDir);
      await writeFile(
        referencePath,
        createPng(32, 16, () => [0, 0, 0, 255]),
      );
      await writeFile(
        actualPath,
        createPng(16, 16, () => [0, 0, 0, 255]),
      );
      for (const [name, sentinel] of baselineSentinels) {
        await writeFile(join(outDir, name), sentinel);
      }
      for (const name of staleDetailNames) {
        await writeFile(join(outDir, name), `stale-${name}`);
      }

      const result = await runOverlay([
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        outDir,
      ]);

      assert.notEqual(result.exitCode, 0, result.output);
      assert.match(result.output, /same dimensions/i);
      for (const [name, sentinel] of baselineSentinels) {
        assert.deepEqual(await readFile(join(outDir, name)), sentinel);
      }
      for (const name of staleDetailNames) {
        await assert.rejects(access(join(outDir, name)));
      }
    } finally {
      await rm(temporaryRoot, { recursive: true, force: true });
    }
  },
);

test(
  "overlay CLI details smoke writes a native overview and candidate sheets",
  {
    skip: playwrightProjectRoot
      ? false
      : "set LAYOUT_WRITING_TEST_PROJECT_ROOT to a Playwright project",
  },
  async () => {
    const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
    const referencePath = join(temporaryRoot, "reference.png");
    const actualPath = join(temporaryRoot, "actual.png");
    const defaultOutDir = join(temporaryRoot, "default");
    const detailsOutDir = join(temporaryRoot, "details");
    const broadOutDir = join(temporaryRoot, "broad");
    try {
      await writeFile(
        referencePath,
        createPng(64, 64, () => [0, 0, 0, 255]),
      );
      await writeFile(
        actualPath,
        createPng(64, 64, (x, y) =>
          x >= 16 && x < 32 && y >= 16 && y < 32
            ? [255, 255, 255, 255]
            : [0, 0, 0, 255],
        ),
      );

      const baselineResult = await run(process.execPath, [
        new URL("./overlay.mjs", import.meta.url).pathname,
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        defaultOutDir,
      ]);
      const detailsResult = await run(process.execPath, [
        new URL("./overlay.mjs", import.meta.url).pathname,
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        detailsOutDir,
        "--details",
        "--threshold",
        "16",
      ]);

      assert.equal(baselineResult.exitCode, 0, baselineResult.output);
      assert.equal(detailsResult.exitCode, 0, detailsResult.output);
      assert.deepEqual((await readdir(defaultOutDir)).sort(), [
        "diff.png",
        "overlay.png",
      ]);
      for (const name of ["overlay.png", "diff.png"]) {
        assert.deepEqual(
          await readFile(join(defaultOutDir, name)),
          await readFile(join(detailsOutDir, name)),
        );
      }
      for (const name of [
        "overlay.png",
        "diff.png",
        "details-overview.png",
        "details-candidate-01.png",
      ]) {
        await access(join(detailsOutDir, name));
      }

      const overview = decodePng(
        await readFile(join(detailsOutDir, "details-overview.png")),
      );
      assert.deepEqual(
        { width: overview.width, height: overview.height },
        { width: 64, height: 64 },
      );
      assert.deepEqual(overview.pixelAt(1, 40).slice(0, 3), [255, 43, 43]);

      const sheet = decodePng(
        await readFile(join(detailsOutDir, "details-candidate-01.png")),
      );
      assert.deepEqual(
        { width: sheet.width, height: sheet.height },
        { width: 128, height: 128 },
      );
      assert.deepEqual(sheet.pixelAt(20, 28).slice(0, 3), [0, 0, 0]);
      assert.deepEqual(sheet.pixelAt(84, 28).slice(0, 3), [255, 255, 255]);
      assert.ok(
        sheet.pixelAt(20, 92)[0] >= 120 && sheet.pixelAt(20, 92)[0] <= 135,
      );
      assert.deepEqual(sheet.pixelAt(84, 92).slice(0, 3), [255, 0, 0]);

      await writeFile(
        actualPath,
        createPng(64, 64, () => [255, 255, 255, 255]),
      );
      const broadResult = await run(process.execPath, [
        new URL("./overlay.mjs", import.meta.url).pathname,
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        broadOutDir,
        "--details",
      ]);
      assert.equal(broadResult.exitCode, 0, broadResult.output);
      assert.match(broadResult.output, /broad difference warning/i);
    } finally {
      await rm(temporaryRoot, { recursive: true, force: true });
    }
  },
);

test(
  "overlay CLI removes stale detail files across five, one, and zero candidate reruns",
  {
    skip: playwrightProjectRoot
      ? false
      : "set LAYOUT_WRITING_TEST_PROJECT_ROOT to a Playwright project",
  },
  async () => {
    const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
    const referencePath = join(temporaryRoot, "reference.png");
    const actualPath = join(temporaryRoot, "actual.png");
    const outDir = join(temporaryRoot, "rerun");
    const width = 1_536;
    const height = 64;
    const commonArgs = [
      "--reference",
      referencePath,
      "--actual",
      actualPath,
      "--project-root",
      playwrightProjectRoot,
      "--out",
      outDir,
    ];
    const expectedBaseline = ["diff.png", "overlay.png"];
    try {
      await writeFile(
        referencePath,
        createPng(width, height, () => [0, 0, 0, 255]),
      );
      await writeFile(
        actualPath,
        createPng(width, height, (x, y) =>
          [0, 320, 640, 960, 1_280].some(
            (start) => x >= start && x < start + 32 && y < 32,
          )
            ? [255, 255, 255, 255]
            : [0, 0, 0, 255],
        ),
      );

      const fiveResult = await runOverlay([...commonArgs, "--details"]);
      assert.equal(fiveResult.exitCode, 0, fiveResult.output);
      assert.deepEqual((await readdir(outDir)).sort(), [
        "details-candidate-01.png",
        "details-candidate-02.png",
        "details-candidate-03.png",
        "details-candidate-04.png",
        "details-candidate-05.png",
        "details-overview.png",
        ...expectedBaseline,
      ]);

      await writeFile(
        actualPath,
        createPng(width, height, (x, y) =>
          x < 32 && y < 32 ? [255, 255, 255, 255] : [0, 0, 0, 255],
        ),
      );
      const oneResult = await runOverlay([...commonArgs, "--details"]);
      assert.equal(oneResult.exitCode, 0, oneResult.output);
      assert.deepEqual((await readdir(outDir)).sort(), [
        "details-candidate-01.png",
        "details-overview.png",
        ...expectedBaseline,
      ]);

      await writeFile(
        actualPath,
        createPng(width, height, () => [0, 0, 0, 255]),
      );
      const zeroResult = await runOverlay(commonArgs);
      assert.equal(zeroResult.exitCode, 0, zeroResult.output);
      assert.deepEqual((await readdir(outDir)).sort(), expectedBaseline);
    } finally {
      await rm(temporaryRoot, { recursive: true, force: true });
    }
  },
);

test(
  "overlay CLI parts mode writes three separate sequential comparison sets",
  {
    skip: playwrightProjectRoot
      ? false
      : "set LAYOUT_WRITING_TEST_PROJECT_ROOT to a Playwright project",
  },
  async () => {
    const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-overlay-test-"));
    const referencePath = join(temporaryRoot, "reference.png");
    const actualPath = join(temporaryRoot, "actual.png");
    const outDir = join(temporaryRoot, "parts");
    try {
      await writeFile(
        referencePath,
        createPng(12, 10, (x, y) => [x, y, 0, 255]),
      );
      await writeFile(
        actualPath,
        createPng(12, 10, (x, y) => [x, y, y >= 3 && y < 6 ? 255 : 0, 255]),
      );

      const result = await runOverlay([
        "--reference",
        referencePath,
        "--actual",
        actualPath,
        "--project-root",
        playwrightProjectRoot,
        "--out",
        outDir,
        "--parts",
        "3",
      ]);

      assert.equal(result.exitCode, 0, result.output);
      assert.deepEqual(
        (await readdir(outDir)).sort(),
        ["01", "02", "03"]
          .flatMap((number) =>
            ["actual", "difference", "overlay", "reference"].map(
              (kind) => `part-${number}-${kind}.png`,
            ),
          )
          .sort(),
      );

      const expectedHeights = [3, 3, 4];
      for (let index = 0; index < expectedHeights.length; index += 1) {
        const number = String(index + 1).padStart(2, "0");
        for (const kind of ["reference", "actual", "difference", "overlay"]) {
          const image = decodePng(
            await readFile(join(outDir, `part-${number}-${kind}.png`)),
          );
          assert.deepEqual(
            { width: image.width, height: image.height },
            { width: 12, height: expectedHeights[index] },
          );
        }
      }

      const firstDifference = decodePng(
        await readFile(join(outDir, "part-01-difference.png")),
      );
      const secondDifference = decodePng(
        await readFile(join(outDir, "part-02-difference.png")),
      );
      assert.deepEqual(firstDifference.pixelAt(0, 0).slice(0, 3), [0, 0, 0]);
      assert.deepEqual(secondDifference.pixelAt(0, 0).slice(0, 3), [255, 0, 0]);
    } finally {
      await rm(temporaryRoot, { recursive: true, force: true });
    }
  },
);
