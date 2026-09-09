# Cube blog QA

final result: passed

The initial visual review below covers the approved local implementation at http://127.0.0.1:5003/blog/. At that review, writing was illustrative and development-only. Tera subsequently authorized production publication, removal of illustrative labels, merge, and deployment. The production release section records the additional checks.

## Visual evidence

- Source: `docs/design/cube-blog-reference.png` (1487 × 1058).
- Implementation: `docs/design/cube-blog-desktop.png` (1440 × 1024).
- Full comparison: `docs/design/cube-blog-comparison.png`; source normalized to 1440 × 1024, then placed beside implementation. Both depict the first article selected with its glass layer extended. A different selected pin location follows the actual chronological point mapping.
- Focused material comparison: `docs/design/cube-blog-material-comparison.png`.
- Mobile: `docs/design/cube-blog-mobile.png`, captured at 390px CSS width; selected preview in a stacked layout.
- Mobile article: `docs/design/cube-blog-article-mobile.png`.
- Desktop viewport requested at 1440 × 1024; final screenshot is exactly that size. An earlier in-app capture returned 1440 × 1595; comparison used only the top 1024 pixels, without stretching. Native clipped capture showed a browser density artifact and was excluded. Final CUA screenshot required no rescaling. Source normalization factor is 1440/1487.

## Findings and resolved iterations

1. P2: Initial cube occupied roughly 300 × 335px and cast distracting separate dot shadows. Increased the orthographic view scale by about 32%; removed directional cast shadows and retained a soft contact shadow. Confirmed revised sculpture fills its intended central region.
2. P2: Initial glass appeared flat and pale. Added a matching graphite transmission background, calibrated smoke attenuation, and explicitly assigned the generated studio environment to the physical material. This resolved the Three.js scene-environment intensity override and made the reflected highlights visible. Selected point uses a clear ivory halo. The final material comparison records the result.
3. P2: Escape followed by Enter on a non-first pin could open the first article. Enter now reselects the focused pin before focusing its reading link. Live browser readback confirmed the second pin retained its correct title and `/blog/the-work-after-the-demo/` destination after Escape/Enter.
4. Removed the initial obsolete PCFSoftShadowMap setting with the shadow pass; the final browser console contains no errors or warnings.
5. Prototype Blog navigation initially used an unsupported analytics destination. Removed its analytics attributes; the full existing test suite passes and homepage behavior is preserved.

## Required fidelity surfaces

- Typography: uses the site's local Inter regular/bold/thin-italic files, with a centered large heading, fine italic subtitle, and monospace metadata. Wrapping is intentional on mobile. No cropped headings or preview text.
- Spacing: preserves the centered introduction, primary sculpture, right-hand preview, and two editorial rows below. The discreet reset/growth tools add approximately one line of height compared with the still mockup. At 390px the preview stacks below the cube and all controls remain reachable.
- Colors: persisted graphite #3b3a38, ivory #eee8e0, and stone #c7b7a4; existing website fonts and Feather arrows are reused. No unrelated brand palette.
- Asset quality: the generated reflection panorama is used by actual Three.js glass geometry. Every visible sphere corresponds to an article. A responsive mathematical cube is necessary for the requested interaction; a still image could not supply moving layers, point selection, or growth. The original mockup's photographic floor caustics and path-traced internal reflections are richer than the lightweight real-time rendering; further cinematic lighting is P3 polish for this prototype.
- Copy: approved headline, subtitle, caption, and first three titles retained. Sample article descriptions reflect the actual new illustrative writing. Read times are calculated from that writing rather than copying the mockup's illustrative six-minute estimate. Preview/sample labels appear in the collection and reading pages.

## Interaction verification

- Desktop native point selection updates title, category, duration, and the correct article destination.
- Mouse movement changes projected pin coordinates while no point is selected; verified the first point moved from (376.15, 47.98) to (363.54, 51.91) within its canvas, with no selected point. Selected state freezes whole-cube rotation while its layer extends.
- Preview remains reachable across the cube/preview gap.
- Keyboard focus selects; Enter focuses the reading link; Escape restores the view. Correct Escape/Enter behavior was reproduced after the fix.
- Growth buttons produce exactly 9 and 10 visible native pin controls, with hidden points removed from navigation. 27 restores the full cube. Range display agrees with the point count.
- A reading link opens its corresponding article; Back to the cube returns to the collection.
- Mobile-width pin selection, menu opening, Escape dismissal, article reading, and return navigation verified. No horizontal overflow on desktop or mobile.
- All 27 destinations are server-rendered in the article list and remain accessible without WebGL or JavaScript. Actual GPU loss was not induced in the user's browser.
- Reduced-motion branches disable rotation and transitions; no operating-system accessibility preference was changed. Dedicated device/screen-reader validation remains outside this local preview.
- Final browser console: no errors or warnings.

## Automated checks

- 150 Python tests passed, including all sample article destinations, production route gating, noindex/sitemap behavior, existing contact behavior, analytics, and static assets.
- 7 Node test-runner results passed, including five mathematical growth/topology tests and the existing navigation/analytics suites.
- JavaScript syntax checks and `git diff --check` passed.

## Follow-up polish

- P3: richer floor caustics and more complex optical reflections could move the real-time material closer to the generated still, at a performance cost.
- P3: a real-device touch and screen-reader pass should accompany production preparation.

The prior consultancy release QA is preserved in `docs/design/consultancy-qa-2026-09-07.md`.

## Production release preparation

- Removed illustrative labels and the debug/test route restriction under explicit publication approval. All 27 original essays form the initial collection.
- Added public canonical URLs, Blog/BlogPosting and breadcrumb metadata, and blog sitemap entries. Blog remains before Expertise in the shared navigation.
- Moved the cube module import into the error handler so a failed module download surfaces the reading-list fallback.
- Removed the hardcoded displayed article count and corrected growth explanations beyond the first 27 posts.
- Excluded documentation and test artifacts from the App Engine upload. Deployment uses a clean export of the merged commit.
- Future scale polish: at 125 posts, bounds-based camera fitting could avoid slight clipping of the uppermost sphere. This does not affect the 27-post launch.
- Fresh production-ready verification: 154 Python tests passed, including all 27 article routes with debug/testing disabled, public metadata/sitemap, unknown-article handling, and existing site behavior. All 7 Node checks, JavaScript syntax checks, and authored-code whitespace validation passed. The vendored Three.js source retains one upstream indentation warning unchanged.
