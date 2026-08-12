#!/usr/bin/env node

import { mkdirSync, writeFileSync } from 'node:fs'
import { resolve, join } from 'node:path'
import { parseArgs } from 'node:util'

import {
  buildScrollPlan,
  loadPlaywright,
  parseExpectedFont,
  parseViewportList,
  platformFontMatches,
  safeFileStem,
} from './visual-tools.mjs'

const NAVIGATION_TIMEOUT_MS = 30_000
const ASSET_TIMEOUT_MS = 10_000
const LAZY_SCROLL_DELAY_MS = 40
const MUTATION_QUIET_MS = 500
const QUIET_TIMEOUT_MS = 1_500
const NETWORK_QUIET_MS = 200

function createOutputTarget(path) {
  const outDir = resolve(path)
  try {
    mkdirSync(outDir)
  } catch (error) {
    if (error.code === 'EEXIST') {
      throw new Error(`output target already exists: ${outDir}`)
    }
    throw new Error(`cannot create output target ${outDir}: ${error.message}`)
  }
  return outDir
}

function readHttpCredentials(userEnvName, passwordEnvName) {
  if (!userEnvName && !passwordEnvName) return undefined
  if (!userEnvName || !passwordEnvName) {
    throw new Error('both --http-user-env and --http-password-env are required')
  }
  const username = process.env[userEnvName]
  const httpPassphrase = process.env[passwordEnvName]
  if (!username || !httpPassphrase) {
    throw new Error('HTTP credential environment variables are missing or empty')
  }
  return { username, password: httpPassphrase }
}

async function freezeMotion(page) {
  await page.addStyleTag({
    content: `
      *, *::before, *::after {
        animation-delay: 0s !important;
        animation-duration: 0s !important;
        transition-duration: 0s !important;
        caret-color: transparent !important;
      }
    `,
  })
}

async function triggerLazyMedia(page, selector) {
  const scope = await page.evaluate((targetSelector) => {
    const originalY = window.scrollY
    if (!targetSelector) {
      return { originalY, start: 0, end: Math.max(0, document.documentElement.scrollHeight - innerHeight) }
    }
    const target = document.querySelector(targetSelector)
    if (!target) throw new Error(`selector not found: ${targetSelector}`)
    const rect = target.getBoundingClientRect()
    return {
      originalY,
      start: Math.max(0, rect.top + window.scrollY - innerHeight),
      end: Math.max(0, rect.bottom + window.scrollY - innerHeight / 2),
    }
  }, selector)

  const plan = buildScrollPlan(
    scope.start,
    scope.end,
    Math.max(300, Math.round((await page.viewportSize()).height * 0.8)),
  )
  for (const position of plan.positions) {
    await page.evaluate((nextY) => window.scrollTo(0, nextY), position)
    await page.waitForTimeout(LAZY_SCROLL_DELAY_MS)
  }
  await page.evaluate((originalY) => window.scrollTo(0, originalY), scope.originalY)
  return plan.complete
}

async function readScopeSignature(page, selector) {
  return page.evaluate((targetSelector) => {
    const root = targetSelector ? document.querySelector(targetSelector) : document
    if (!root) throw new Error(`selector not found: ${targetSelector}`)
    const images = [
      ...(root instanceof HTMLImageElement ? [root] : []),
      ...root.querySelectorAll('img'),
    ]
    const scopeHeight =
      root === document
        ? document.documentElement.scrollHeight
        : Math.max(root.scrollHeight, Math.round(root.getBoundingClientRect().height))
    return {
      scopeHeight,
      mediaCount: root.querySelectorAll('img, picture, video, source').length,
      imageCount: images.length,
      unresolvedImageCount: images.filter(
        (image) => !image.complete || image.naturalWidth === 0,
      ).length,
    }
  }, selector)
}

async function startMutationTracking(page, selector) {
  await page.evaluate((targetSelector) => {
    const root = targetSelector ? document.querySelector(targetSelector) : document.documentElement
    if (!root) throw new Error(`selector not found: ${targetSelector}`)
    window.__layoutCaptureMutationObserver?.disconnect()
    window.__layoutCaptureMutationState = { count: 0, lastMutation: performance.now() }
    window.__layoutCaptureMutationObserver = new MutationObserver((records) => {
      window.__layoutCaptureMutationState.count += records.length
      window.__layoutCaptureMutationState.lastMutation = performance.now()
    })
    window.__layoutCaptureMutationObserver.observe(root, {
      attributes: true,
      childList: true,
      characterData: true,
      subtree: true,
    })
  }, selector)
}

async function waitForMutationQuiet(page) {
  return page.evaluate(
    async ({ quietMs, timeoutMs }) => {
      const started = performance.now()
      while (performance.now() - started < timeoutMs) {
        const state = window.__layoutCaptureMutationState
        if (state && performance.now() - state.lastMutation >= quietMs) {
          window.__layoutCaptureMutationObserver?.disconnect()
          return { quiet: true, mutations: state.count }
        }
        await new Promise((done) => setTimeout(done, 50))
      }
      const state = window.__layoutCaptureMutationState || { count: 0 }
      window.__layoutCaptureMutationObserver?.disconnect()
      return { quiet: false, mutations: state.count }
    },
    { quietMs: MUTATION_QUIET_MS, timeoutMs: QUIET_TIMEOUT_MS },
  )
}

async function waitForVisualNetworkQuiet(page, pendingRequests) {
  const started = Date.now()
  let quietStarted = null
  while (Date.now() - started < QUIET_TIMEOUT_MS) {
    if (pendingRequests.size === 0) {
      quietStarted ??= Date.now()
      if (Date.now() - quietStarted >= NETWORK_QUIET_MS) return true
    } else {
      quietStarted = null
    }
    await page.waitForTimeout(50)
  }
  return false
}

async function waitForAssets(page, selector, expectedFonts) {
  return page.evaluate(async ({ timeoutMs, targetSelector, fontRequirements }) => {
    const root = targetSelector ? document.querySelector(targetSelector) : document
    if (!root) throw new Error(`selector not found: ${targetSelector}`)
    const images = [
      ...(root instanceof HTMLImageElement ? [root] : []),
      ...root.querySelectorAll('img'),
    ]
    const imagePromises = images.map((image) => {
      if (image.complete) return Promise.resolve()
      return new Promise((done) => {
        image.addEventListener('load', done, { once: true })
        image.addEventListener('error', done, { once: true })
      })
    })
    const assets = Promise.allSettled([
      document.fonts?.ready || Promise.resolve(),
      ...imagePromises,
    ])
    await Promise.race([
      assets,
      new Promise((done) => setTimeout(done, timeoutMs)),
    ])
    const normalizeFamily = (family) => family.replace(/^['"]|['"]$/g, '').trim().toLowerCase()
    const normalizeWeight = (weight) => ({ normal: '400', bold: '700' })[weight] || weight
    const supportsWeight = (faceWeight, requiredWeight) => {
      const normalizedFace = normalizeWeight(faceWeight)
      const normalizedRequired = normalizeWeight(requiredWeight)
      const range = /^(\d+)\s+(\d+)$/.exec(normalizedFace)
      if (!range) return normalizedFace === normalizedRequired
      const required = Number(normalizedRequired)
      return required >= Number(range[1]) && required <= Number(range[2])
    }
    const availableFaces = [...(document.fonts || [])].map((face) => ({
      family: face.family.replace(/^['"]|['"]$/g, ''),
      weight: face.weight,
      style: face.style,
      status: face.status,
    }))
    const fonts = fontRequirements.map((requirement) => {
      const element = requirement.selector
        ? document.querySelector(requirement.selector)
        : root === document
          ? document.body
          : root
      const computed = element ? getComputedStyle(element) : null
      const expectedFamily = normalizeFamily(requirement.family)
      const matchingFaces = availableFaces.filter(
        (face) =>
          normalizeFamily(face.family) === expectedFamily &&
          supportsWeight(face.weight, requirement.weight) &&
          face.style === requirement.style,
      )
      const computedPrimaryFamily = computed
        ? normalizeFamily(computed.fontFamily.split(',')[0])
        : null
      const check = document.fonts?.check(
        `${requirement.style} ${requirement.weight} 16px "${requirement.family}"`,
      ) ?? false
      const computedMatches =
        computedPrimaryFamily === expectedFamily &&
        normalizeWeight(computed?.fontWeight) === normalizeWeight(requirement.weight) &&
        computed?.fontStyle === requirement.style &&
        check
      const loadedWebfont = matchingFaces.some((face) => face.status === 'loaded')
      return {
        ...requirement,
        computedFamily: computed?.fontFamily || null,
        computedWeight: computed?.fontWeight || null,
        computedStyle: computed?.fontStyle || null,
        matchingFaces,
        fontSetCheck: check,
        status:
          !computedMatches || (matchingFaces.length > 0 && !loadedWebfont)
            ? 'fallback_or_missing'
            : 'rendered_font_check_required',
      }
    })
    return {
      fontsStatus: document.fonts?.status || 'unsupported',
      fonts,
      imageCount: images.length,
      unresolvedImages: images
        .filter((image) => !image.complete || image.naturalWidth === 0)
        .map((image) => {
          const source = image.currentSrc || image.src || '(unknown)'
          if (source.startsWith('data:')) return '(inline image)'
          try {
            const parsed = new URL(source)
            return `${parsed.origin}${parsed.pathname}`
          } catch {
            return source
          }
        })
        .slice(0, 20),
    }
  }, { timeoutMs: ASSET_TIMEOUT_MS, targetSelector: selector, fontRequirements: expectedFonts })
}

async function runPreparationPass(page, selector, expectedFonts, pendingRequests) {
  await startMutationTracking(page, selector)
  const scrollComplete = await triggerLazyMedia(page, selector)
  const assets = await waitForAssets(page, selector, expectedFonts)
  const mutation = await waitForMutationQuiet(page)
  const networkQuiet = await waitForVisualNetworkQuiet(page, pendingRequests)
  const signature = await readScopeSignature(page, selector)
  return { assets, mutation, networkQuiet, scrollComplete, signature }
}

function passIsStable(before, pass) {
  return (
    JSON.stringify(before) === JSON.stringify(pass.signature) &&
    pass.assets.unresolvedImages.length === 0 &&
    pass.mutation.quiet &&
    pass.mutation.mutations === 0 &&
    pass.networkQuiet &&
    pass.scrollComplete
  )
}

async function prepareAssets(page, selector, expectedFonts, pendingRequests) {
  const before = await readScopeSignature(page, selector)
  const first = await runPreparationPass(page, selector, expectedFonts, pendingRequests)
  if (passIsStable(before, first)) {
    return {
      ...first.assets,
      ...first.signature,
      passes: 1,
      stable: true,
      scrollComplete: true,
      mutationQuiet: true,
      networkQuiet: true,
    }
  }

  const second = await runPreparationPass(page, selector, expectedFonts, pendingRequests)
  const stable = passIsStable(first.signature, second)
  return {
    ...second.assets,
    ...second.signature,
    passes: 2,
    stable,
    scrollComplete: first.scrollComplete && second.scrollComplete,
    mutationQuiet: second.mutation.quiet && second.mutation.mutations === 0,
    networkQuiet: second.networkQuiet,
  }
}

async function resolveRenderedFonts(
  context,
  page,
  fonts,
  defaultSelector,
  browserName,
  allowedFallbacks,
) {
  if (!fonts.some((font) => font.status === 'rendered_font_check_required')) return fonts
  if (browserName !== 'chromium') {
    return fonts.map((font) =>
      font.status === 'rendered_font_check_required'
        ? { ...font, status: 'rendered_font_unverifiable' }
        : font,
    )
  }

  const session = await context.newCDPSession(page)
  try {
    await session.send('DOM.enable')
    await session.send('CSS.enable')
    const { root } = await session.send('DOM.getDocument', { depth: 0 })
    const resolved = []
    for (const font of fonts) {
      if (font.status !== 'rendered_font_check_required') {
        resolved.push(font)
        continue
      }
      const selector = font.selector || defaultSelector || 'body'
      const { nodeId } = await session.send('DOM.querySelector', { nodeId: root.nodeId, selector })
      if (!nodeId) {
        resolved.push({ ...font, status: 'fallback_or_missing', platformFonts: [] })
        continue
      }
      const { fonts: platformFonts } = await session.send('CSS.getPlatformFontsForNode', { nodeId })
      const expectedPlatformFamily = font.platformFamily || font.family
      const expectedEntries = platformFonts.filter((entry) =>
        platformFontMatches(expectedPlatformFamily, entry.familyName),
      )
      const unexpectedEntries = platformFonts.filter(
        (entry) =>
          entry.glyphCount > 0 &&
          !platformFontMatches(expectedPlatformFamily, entry.familyName) &&
          !allowedFallbacks.some((allowed) =>
            platformFontMatches(allowed, entry.familyName),
          ),
      )
      const status =
        expectedEntries.length === 0
          ? 'fallback_or_missing'
          : unexpectedEntries.length > 0
            ? 'partial_fallback'
            : 'verified_rendered_font'
      resolved.push({
        ...font,
        expectedPlatformFamily,
        platformFonts: platformFonts.map((entry) => ({
          family: entry.familyName,
          glyphCount: entry.glyphCount,
          custom: entry.isCustomFont,
        })),
        unexpectedFallbacks: unexpectedEntries.map((entry) => entry.familyName),
        status,
      })
    }
    return resolved
  } catch (error) {
    return fonts.map((font) =>
      font.status === 'rendered_font_check_required'
        ? { ...font, status: 'rendered_font_unverifiable', platformFontError: error.message }
        : font,
    )
  } finally {
    await session.detach()
  }
}

async function inspectOverflow(page) {
  return page.evaluate(() => {
    const viewportWidth = document.documentElement.clientWidth
    const nodes = [...document.body.querySelectorAll('*')]
      .map((element) => {
        const rect = element.getBoundingClientRect()
        return { element, rect }
      })
      .filter(({ rect }) => rect.left < -1 || rect.right > viewportWidth + 1)
      .slice(0, 20)
      .map(({ element, rect }) => ({
        element:
          element.tagName.toLowerCase() +
          (element.id ? `#${element.id}` : '') +
          [...element.classList].slice(0, 3).map((name) => `.${name}`).join(''),
        left: Math.round(rect.left * 100) / 100,
        right: Math.round(rect.right * 100) / 100,
        width: Math.round(rect.width * 100) / 100,
      }))
    return {
      viewportWidth,
      documentWidth: document.documentElement.scrollWidth,
      overflowNodes: nodes,
    }
  })
}

async function main() {
  const { values } = parseArgs({
    options: {
      url: { type: 'string' },
      out: { type: 'string' },
      label: { type: 'string', default: 'page' },
      'project-root': { type: 'string', default: process.cwd() },
      viewports: { type: 'string' },
      browser: { type: 'string', default: 'chromium' },
      selector: { type: 'string' },
      'wait-ms': { type: 'string', default: '250' },
      'http-user-env': { type: 'string' },
      'http-password-env': { type: 'string' },
      'expect-font': { type: 'string', multiple: true },
      'allow-font': { type: 'string', multiple: true },
    },
  })

  if (!values.url || !values.viewports || !values.out) {
    throw new Error('usage: capture.mjs --url <url> --project-root <repo> --viewports <WIDTHxHEIGHT,...> --out <new-path> [options]')
  }
  const parsedUrl = new URL(values.url)
  if (!['http:', 'https:', 'file:', 'data:'].includes(parsedUrl.protocol)) {
    throw new Error(`unsupported URL protocol: ${parsedUrl.protocol}`)
  }

  const waitMs = Number(values['wait-ms'])
  if (!Number.isFinite(waitMs) || waitMs < 0 || waitMs > NAVIGATION_TIMEOUT_MS) {
    throw new Error('--wait-ms must be between 0 and 30000')
  }

  const viewports = parseViewportList(values.viewports)
  const expectedFonts = (values['expect-font'] || []).map(parseExpectedFont)
  const allowedFallbacks = values['allow-font'] || []
  const outDir = createOutputTarget(values.out)
  const playwright = loadPlaywright(values['project-root'])
  const browserType = playwright[values.browser]
  if (!browserType || !['chromium', 'webkit', 'firefox'].includes(values.browser)) {
    throw new Error('--browser must be chromium, webkit, or firefox')
  }

  const browser = await browserType.launch()
  const report = []

  try {
    for (const viewport of viewports) {
      const context = await browser.newContext({
        viewport,
        deviceScaleFactor: 1,
        reducedMotion: 'reduce',
        httpCredentials: readHttpCredentials(
          values['http-user-env'],
          values['http-password-env'],
        ),
      })
      const page = await context.newPage()
      const pendingVisualRequests = new Set()
      const failedFontRequests = []
      const recordFontFailure = (request, reason) => {
        if (request.resourceType() !== 'font') return
        try {
          const parsed = new URL(request.url())
          failedFontRequests.push({ url: `${parsed.origin}${parsed.pathname}`, reason })
        } catch {
          failedFontRequests.push({ url: '(unparseable font URL)', reason })
        }
      }
      page.on('requestfailed', (request) =>
        recordFontFailure(request, request.failure()?.errorText || 'request failed'),
      )
      page.on('request', (request) => {
        if (['image', 'media', 'font'].includes(request.resourceType())) {
          pendingVisualRequests.add(request)
        }
      })
      page.on('requestfinished', (request) => pendingVisualRequests.delete(request))
      page.on('requestfailed', (request) => pendingVisualRequests.delete(request))
      page.on('response', (response) => {
        if (!response.ok()) recordFontFailure(response.request(), `HTTP ${response.status()}`)
      })
      const response = await page.goto(values.url, {
        waitUntil: 'domcontentloaded',
        timeout: NAVIGATION_TIMEOUT_MS,
      })
      if (response && response.status() >= 400) {
        throw new Error(`navigation returned HTTP ${response.status()}`)
      }
      const target = values.selector ? page.locator(values.selector).first() : page
      if (values.selector) {
        await target.waitFor({ state: 'visible', timeout: NAVIGATION_TIMEOUT_MS })
      }
      await freezeMotion(page)
      if (waitMs > 0) await page.waitForTimeout(waitMs)
      const assetStatus = await prepareAssets(
        page,
        values.selector,
        expectedFonts,
        pendingVisualRequests,
      )
      assetStatus.fonts = await resolveRenderedFonts(
        context,
        page,
        assetStatus.fonts,
        values.selector,
        values.browser,
        allowedFallbacks,
      )
      if (values.selector) await target.scrollIntoViewIfNeeded()
      const filename = `${safeFileStem(values.label)}-${viewport.width}x${viewport.height}.png`
      const screenshotPath = join(outDir, filename)
      await target.screenshot({
        path: screenshotPath,
        ...(values.selector ? {} : { fullPage: true }),
      })
      report.push({
        viewport,
        screenshot: screenshotPath,
        selector: values.selector || null,
        assets: {
          ...assetStatus,
          failedFontRequests,
          evidenceComplete:
            assetStatus.stable &&
            assetStatus.scrollComplete &&
            assetStatus.mutationQuiet &&
            assetStatus.networkQuiet &&
            assetStatus.unresolvedImages.length === 0 &&
            assetStatus.fonts.every((font) => font.status.startsWith('verified_')),
        },
        ...(await inspectOverflow(page)),
      })
      await context.close()
    }
  } finally {
    await browser.close()
  }

  const reportPath = join(outDir, `${safeFileStem(values.label)}-capture.json`)
  writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`)
  console.log(`[capture] wrote ${report.length} capture(s) and ${reportPath}`)
}

main().catch((error) => {
  console.error(`[capture] ${error.message}`)
  process.exitCode = 1
})
