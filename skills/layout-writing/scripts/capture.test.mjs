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

function runCapture(args) {
  return new Promise((resolve) => {
    const child = spawn(
      process.execPath,
      [new URL("./capture.mjs", import.meta.url).pathname, ...args],
      { stdio: ["ignore", "pipe", "pipe"] },
    );
    let output = "";
    child.stdout.on("data", (chunk) => (output += chunk));
    child.stderr.on("data", (chunk) => (output += chunk));
    child.on("close", (exitCode) => resolve({ exitCode, output }));
  });
}

test("capture CLI requires an explicit output target", async () => {
  const result = await runCapture([
    "--url",
    "data:text/html,<main>test</main>",
    "--viewports",
    "375x812",
  ]);
  assert.notEqual(result.exitCode, 0, result.output);
  assert.match(result.output, /--out <new-path>/i);
});

test("capture CLI requires explicit viewports", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-capture-test-"));
  try {
    const result = await runCapture([
      "--url",
      "data:text/html,<main>test</main>",
      "--out",
      join(temporaryRoot, "out"),
    ]);
    assert.notEqual(result.exitCode, 0, result.output);
    assert.match(result.output, /--viewports <WIDTHxHEIGHT,\.\.\.>/i);
  } finally {
    await rm(temporaryRoot, { recursive: true, force: true });
  }
});

test("capture CLI rejects an existing output target without modifying it", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-capture-test-"));
  const outDir = join(temporaryRoot, "out");
  const sentinelPath = join(outDir, "sentinel.txt");
  try {
    await mkdir(outDir);
    await writeFile(sentinelPath, "keep");
    const result = await runCapture([
      "--url",
      "data:text/html,<main>test</main>",
      "--project-root",
      join(temporaryRoot, "missing-project"),
      "--viewports",
      "375x812",
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

test("capture CLI atomically creates a fresh output target before launching Playwright", async () => {
  const temporaryRoot = await mkdtemp(join(tmpdir(), "layout-capture-test-"));
  const outDir = join(temporaryRoot, "fresh-out");
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
    const result = await runCapture([
      "--url",
      "data:text/html,<main>test</main>",
      "--project-root",
      projectRoot,
      "--viewports",
      "375x812",
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
