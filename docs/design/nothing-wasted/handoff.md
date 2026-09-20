# Nothing Wasted website brand — 2026-09-20

## Source and interpretation

Figma: https://www.figma.com/design/qE73Y9odXd81lEF1ShPy0D/Nothing-Wasted-Headers?node-id=5-2

The approved scope applies the brand to the whole site while retaining current copy, destinations, article identities, and cube behavior. Website reference nodes: foundations `6:2`, desktop `7:2`, mobile `7:13`, handoff `8:2`. The longer existing headline intentionally wraps differently from “Nothing wasted.” Navigation and delivery-stage links remain functional and visible. Services, articles, forms, and errors extend the reference's typography and palette; Figma only specifies the hero examples.

- Landscape `5:5`: original 2172 × 724 PNG export retained; WebP derivatives at 768, 1440, 2172px, quality 85 (9,286 / 28,844 / 56,504 bytes). Empty alternative text because it is decorative. Mobile crops without distortion.
- Horizontal logo `5:3`: original 1600 × 533 PNG export retained; 800 × 267 WebP at quality 92 (6,988 bytes). Footer preserves proportions and padded clear space. Its embedded lettering and ivory texture are unchanged.
- Social card: 1200 × 630 JPEG using the exported landscape, local brand fonts, and existing hero wording; metadata reports actual dimensions. No new marketing claims.
- Cormorant Garamond Regular Latin WOFF2: Google Fonts v21, 22,896 bytes, SHA-256 prefix `982538ce9654`; SIL OFL stored alongside the font. Inter Regular/Bold and their existing licenses are reused. Unused thin/italic declarations removed from active styles.
- Original PNG masters are excluded from App Engine upload; permanent optimized assets use existing content-versioned URLs. Figma's expiring download URLs are not stored or used at runtime.
- Shared palette is defined once in `main.css`; WebGL reads those CSS properties. `--container-max: 1328px` includes 24px gutters, leaving 1280px of content. The existing favicon remains; vector identity work is deferred.

## Verification

- Python: **174 passed, 17 skipped**. Skips require the separate local contact broker/emulator. Contact tests use mocks; this release does not claim a new delivered email receipt.
- JavaScript: **14 passed, 1 skipped**. Optional live Google network test is disabled; analytics implementation/configuration is unchanged.
- Playwright with installed Chrome, because the Browser plugin is not available: 36 combinations across homepage, all four services, blog archive, representative article, RSS subscription, and 404 at 1440/768/390/320px; no horizontal page overflow or page exceptions.
- Interaction checks: mobile menu open/close; service disclosure; native contact radio selection, arrow-key selection, invalid form handling; consent reopen/reject; all 28 cube pins, keyboard article selection, growth, Escape focus restoration and reset; RSS copy action; 200% zoom and reduced motion; simulated WebGL-unavailable writing fallback.
- Public-route crawl locally: 35 pages, 17 referenced assets, and all 28 RSS items. Versioned assets have immutable caching. 404/500 are covered by Python tests; refreshed 404 additionally inspected in Chrome at three widths.
- Shared text, muted, error and action pairings pass WCAG AA contrast tests on ivory and sage. Selected radios are ivory on moss. Visible action controls have minimum 44px targets; inline prose links retain text flow.
- Cold homepage resource sample at 1440px, with analytics declined: existing production ~560KB, local refresh ~230KB. This is a resource sample, not a field Core Web Vitals claim; local and hosted compression differ. New 1440px artwork alone is 28.8KB versus 202KB for the old 1536px artwork.
- `git diff --check` passes. Final implementation self-review compared against `origin/main`: no remaining actionable issues in the changed routing/metadata, contact/analytics boundaries, asset caching, cube behavior, or responsive styles. No independent reviewer approval is implied.

Screenshots: [desktop](home-desktop.png), [mobile](home-mobile.png), [blog mobile](blog-mobile.png).

## Release procedure

Deploy the merged commit to App Engine `teraearlywine/default` with no promotion. Capture current traffic first (observed baseline: `pomodoro-gates-20260914`, 100%). Verify version-specific routes, assets, RSS, browser rendering and controls before assigning 100% traffic. Recheck native allocation and the canonical domain afterwards. On failure, restore the captured baseline and verify recovery. Record actual release results separately after verification.

## Hero alignment refinement — 2026-09-20

At Tera's request, the landscape cube now shares the hero copy's horizontal row at widths of 1024px and above. The image is cropped to its right-hand artwork without stretching, with no text/image overlap. Narrow screens preserve copy-before-art reading order and the existing stacked layout. Copy, actions, and blog cube behavior are unchanged.

Chrome geometry and visual checks passed at 320, 390, 768, 1024, 1440, and 1920px; no horizontal overflow or page exceptions. Python suite: 174 passed, 17 existing broker/emulator skips. [Desktop screenshot](hero-aligned-desktop.png).

## Blog alignment refinement — 2026-09-20

The archive header is left-aligned to the same 1280px content grid as the writing list and offer. The explorer uses the full content width instead of a separate right-anchored maximum. Caption, reset, and growth controls belong to the cube column; the preview remains beside the cube on desktop and follows it on mobile. The subtitle uses the site's body scale instead of competing with the heading. Shared navigation inherits the site's gutters.

Six-width Chrome checks (320–1920px) verify aligned content edges, controls centered under the cube, separate preview bounds, all 28 pins, keyboard selection, growth, Escape focus restoration, reset, and no page errors/overflow. Python: 174 passed, 17 existing skips. JavaScript: 14 passed, 1 optional live-network skip. [Desktop](blog-aligned-desktop.png) / [mobile](blog-aligned-mobile.png).
