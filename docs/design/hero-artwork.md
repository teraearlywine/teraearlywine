# Retina glass hero

Generated on 2026-09-07 using the approved imagegen CLI/API fallback, model `gpt-image-2`, edit mode, high quality, explicit size `3072x2544`.

The edit target was `core/home/assets/images/hero-glass.png`. The retained master is `core/home/assets/images/hero-glass-retina.png`, verified at 3072 × 2544 pixels. This replaces the 1379 × 1141 image in the header while preserving its composition and palette. Fine details differ because this is an AI restoration.

## Generation prompt

Restore this website hero artwork at high resolution with crisp glass edges and fine refraction detail. Preserve the same composition, diagonal glass ring silhouette, camera angle, transparent smoky glass, warm graphite and taupe palette, directional lighting, striped caustics, shadows, stone texture and quiet dark space on the upper left for website text. Improve the fine optical detail and remove pixelation and compression artifacts. Keep intentional optical softness natural. No redesign, no added objects, no text, no watermark.

## Delivery

WebP variants are encoded from the master at quality 88, method 6, using Lanczos for downsampling. Their widths are 768, 1536, 2304 and 3072 pixels (approximately 49, 198, 401 and 621 KiB). The template uses width-based `srcset` and retains high fetch priority for the header. The 423px minimum source size accounts for the mobile image covering a 350px-high box.

The uncompressed master is retained in Git and excluded from App Engine uploads. New versioned filenames avoid reusing the old image cache.

## Validation

- All 56 Python tests and both JavaScript checks passed, including a regression check for WebP delivery when the runtime's system MIME registry does not support it.
- At 1440px viewport width and 2× pixel density, Chromium selected the 3072px image.
- At 390px viewport width and 3× pixel density, Chromium selected the 1536px image.
- Both browser checks confirmed successful image decoding, no horizontal overflow and no page errors. Desktop and mobile screenshots were visually reviewed.
- Upload listing includes all four WebP images and excludes the PNG master and local browser screenshots.
